from __future__ import annotations

from src.agent.application.ports.i_tool_executor import IToolExecutor
from src.agent.domain.value_objects import (
    Parameters,
    QueryResult,
    ToolName,
)
from src.shared.domain.base import ResponseKind


def _select_kind(row_count: int) -> ResponseKind:
    if row_count == 0:
        return ResponseKind.TEXT
    if row_count > 10:
        return ResponseKind.TABLE
    return ResponseKind.CHART


class VizSelectorTool(IToolExecutor):
    @property
    def name(self) -> ToolName:
        return ToolName("viz_selector")

    async def can_handle(self, query: str) -> bool:
        return True

    async def execute(self, parameters: Parameters) -> QueryResult:
        raw = parameters.value.get("row_count", 0)
        row_count = raw if isinstance(raw, int) else 0
        kind = _select_kind(row_count)
        return QueryResult(
            _columns=("kind",),
            _rows=({"kind": kind.name.lower()},),
        )
