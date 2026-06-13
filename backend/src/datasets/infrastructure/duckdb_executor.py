from __future__ import annotations

from src.shared.domain.base import EntityId
from src.shared.infrastructure.duckdb_pool import DuckDBPool
from src.datasets.application.ports.i_query_engine import IQueryEngine
from src.datasets.domain.value_objects import SchemaDefinition
from src.agent.domain.value_objects import QueryResult


class DuckDBExecutor(IQueryEngine):
    def __init__(self, pool: DuckDBPool) -> None:
        self._pool = pool

    async def register_schema(
        self, dataset_id: EntityId, schema: SchemaDefinition
    ) -> None:
        table_name = f"ds_{dataset_id.value.hex}"
        columns_def = ", ".join(
            f'"{col._name}" {col._dtype}'
            for col in schema._columns
        )
        with self._pool.connection() as conn:
            conn.execute(
                f"CREATE OR REPLACE TABLE {table_name} ({columns_def})"
            )

    async def execute(self, sql: str) -> QueryResult:
        with self._pool.connection() as conn:
            result = conn.execute(sql)
            columns = tuple(desc[0] for desc in result.description)
            rows = tuple(
                dict(zip(columns, row)) for row in result.fetchall()
            )
            return QueryResult(_columns=columns, _rows=rows)

    async def execute_raw(self, sql: str) -> QueryResult:
        return await self.execute(sql)

    async def preview(
        self, dataset_id: EntityId, limit: int
    ) -> QueryResult:
        table_name = f"ds_{dataset_id.value.hex}"
        return await self.execute(
            f"SELECT * FROM {table_name} LIMIT {limit}"
        )
