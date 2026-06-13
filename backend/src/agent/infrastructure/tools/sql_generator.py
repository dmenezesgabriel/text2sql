from __future__ import annotations

from src.agent.application.ports.i_tool_executor import IToolExecutor
from src.agent.domain.value_objects import Parameters, QueryResult, ToolName
from src.datasets.application.ports.i_query_engine import IQueryEngine


class SQLGeneratorTool(IToolExecutor):
    def __init__(self, engine: IQueryEngine) -> None:
        self._engine = engine

    @property
    def name(self) -> ToolName:
        return ToolName("sql_generator")

    async def can_handle(self, query: str) -> bool:
        return True

    async def execute(self, parameters: Parameters) -> QueryResult:
        sql = parameters.value.get("sql", "")
        return await self._engine.execute(sql)
