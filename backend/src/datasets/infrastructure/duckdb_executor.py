# ruff: noqa: S608 -- view names are hex UUIDs, not user input
from __future__ import annotations

from src.datasets.domain.value_objects import ColumnDefinition, SchemaDefinition
from src.shared.domain.base import EntityId, QueryResult
from src.shared.infrastructure.duckdb_pool import DuckDBPool


class DuckDBExecutor:
    """Implements IQueryRegistrar + IQueryEngine via structural typing.

    DuckDB is in-process and synchronous. The async def wrappers exist for
    interface consistency with the rest of the application, not for non-blocking
    I/O — DuckDB queries at BI scale are sub-100ms and concurrency is low.
    """

    def __init__(self, pool: DuckDBPool) -> None:
        self._pool = pool

    async def register_schema(
        self,
        dataset_id: EntityId,
        schema: SchemaDefinition,
    ) -> None:
        table_name = f"ds_{dataset_id.value.hex}"
        columns_def = ", ".join(f'"{col._name}" {col._dtype}' for col in schema._columns)
        with self._pool.connection() as conn:
            conn.execute(f"CREATE OR REPLACE TABLE {table_name} ({columns_def})")

    async def create_view_from_s3(self, dataset_id: EntityId, s3_uri: str) -> SchemaDefinition:
        view_name = f"ds_{dataset_id.value.hex}"
        with self._pool.connection() as conn:
            parquet_sql = (
                f"CREATE OR REPLACE VIEW {view_name} AS SELECT * FROM read_parquet('{s3_uri}')"
            )
            conn.execute(parquet_sql)
            rows = conn.execute(f"DESCRIBE {view_name}").fetchall()
        cols = tuple(
            ColumnDefinition(_name=r[0], _dtype=r[1], _nullable=r[2] == "YES") for r in rows
        )
        return SchemaDefinition(_columns=cols)

    async def execute(self, sql: str) -> QueryResult:
        with self._pool.connection() as conn:
            result = conn.execute(sql)
            columns = tuple(desc[0] for desc in result.description)
            rows = tuple(dict(zip(columns, row)) for row in result.fetchall())
            return QueryResult(_columns=columns, _rows=rows)

    async def preview(self, dataset_id: EntityId, limit: int) -> QueryResult:
        view_name = f"ds_{dataset_id.value.hex}"
        return await self.execute(f"SELECT * FROM {view_name} LIMIT {limit}")
