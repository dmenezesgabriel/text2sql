from __future__ import annotations

from src.agent.domain.value_objects import Parameters, QueryResult, ToolName
from src.agent.infrastructure.tools.sql_generator import SQLGeneratorTool
from src.datasets.domain.value_objects import SchemaDefinition
from src.shared.domain.base import EntityId


class FakeQueryEngine:
    def __init__(self) -> None:
        self.last_sql: str | None = None

    async def execute(self, sql: str) -> QueryResult:
        self.last_sql = sql
        return QueryResult(_columns=("id",), _rows=({"id": 1},))

    async def register_schema(self, dataset_id: EntityId, schema: SchemaDefinition) -> None:
        pass

    async def create_view_from_s3(self, dataset_id: EntityId, s3_uri: str) -> SchemaDefinition:
        return SchemaDefinition(_columns=())

    async def preview(self, dataset_id: EntityId, limit: int) -> QueryResult:
        return QueryResult(_columns=(), _rows=())


class TestSQLGeneratorTool:
    def test_name_is_sql_generator(self) -> None:
        tool = SQLGeneratorTool(engine=FakeQueryEngine())
        assert tool.name == ToolName("sql_generator")

    async def test_can_handle_any_query(self) -> None:
        tool = SQLGeneratorTool(engine=FakeQueryEngine())
        assert await tool.can_handle("anything")

    async def test_execute_passes_sql_to_engine(self) -> None:
        engine = FakeQueryEngine()
        tool = SQLGeneratorTool(engine=engine)
        params = Parameters({"sql": "SELECT 1"})
        result = await tool.execute(params)
        assert engine.last_sql == "SELECT 1"
        assert result.row_count() == 1

    async def test_execute_with_missing_sql_key(self) -> None:
        engine = FakeQueryEngine()
        tool = SQLGeneratorTool(engine=engine)
        params = Parameters({})
        await tool.execute(params)
        assert engine.last_sql == ""
