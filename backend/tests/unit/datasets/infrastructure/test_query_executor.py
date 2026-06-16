from __future__ import annotations

from src.datasets.domain.value_objects import SchemaDefinition
from src.datasets.infrastructure.query_executor import DuckDBQueryExecutor
from src.shared.domain.base import EntityId, QueryResult


class FakeQueryEngine:
    async def execute(self, sql: str) -> QueryResult:
        return QueryResult(_columns=("x",), _rows=({"x": 1},))

    async def create_view_from_s3(self, dataset_id: EntityId, s3_uri: str) -> SchemaDefinition:
        return SchemaDefinition(_columns=())

    async def preview(self, dataset_id: EntityId, limit: int) -> QueryResult:
        return QueryResult(_columns=(), _rows=())


class TestDuckDBQueryExecutor:
    def test_instantiate_with_fake_engine(self) -> None:
        engine = FakeQueryEngine()
        executor = DuckDBQueryExecutor(engine=engine)  # type: ignore[arg-type]
        assert executor is not None

    async def test_execute_delegates_to_engine(self) -> None:
        from uuid import uuid4

        engine = FakeQueryEngine()
        executor = DuckDBQueryExecutor(engine=engine)  # type: ignore[arg-type]
        result = await executor.execute(sql="SELECT 1", dataset_id=EntityId(uuid4()))
        assert result.row_count() == 1
