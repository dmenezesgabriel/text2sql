from __future__ import annotations

from src.agent.domain.value_objects import ToolName, Parameters, QueryResult
from src.agent.application.ports.i_tool_executor import IToolExecutor


class SQLGeneratorTool(IToolExecutor):
    @property
    def name(self) -> ToolName:
        return ToolName("sql_generator")

    async def can_handle(self, query: str) -> bool:
        return True

    async def execute(self, parameters: Parameters) -> QueryResult:
        sql = parameters.value.get("sql", "")
        dataset_id = parameters.value.get("dataset_id")

        from datasets.infrastructure.duckdb_executor import DuckDBExecutor
        executor = DuckDBExecutor()
        return await executor.execute_raw(sql)
