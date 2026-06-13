from __future__ import annotations

from src.agent.domain.value_objects import (
    ToolName, Parameters, QueryResult, ResponseKind, ResponseFormat,
)
from src.agent.application.ports.i_tool_executor import IToolExecutor


class VizSelectorTool(IToolExecutor):
    @property
    def name(self) -> ToolName:
        return ToolName("viz_selector")

    async def can_handle(self, query: str) -> bool:
        return True

    async def execute(self, parameters: Parameters) -> QueryResult:
        columns = parameters.value.get("columns", [])
        row_count = parameters.value.get("row_count", 0)

        has_numeric = any(
            isinstance(col.get("type"), str) and "int" in col.get("type", "")
            for col in columns
        )

        if row_count == 1 and has_numeric:
            kind = ResponseKind.CHART
        elif row_count > 10:
            kind = ResponseKind.TABLE
        elif row_count > 0:
            kind = ResponseKind.CHART
        else:
            kind = ResponseKind.TEXT

        return QueryResult(
            _columns=("kind",),
            _rows=({"kind": kind.name.lower()},),
        )
