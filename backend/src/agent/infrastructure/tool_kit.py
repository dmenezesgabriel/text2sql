from __future__ import annotations

from src.agent.application.ports.i_tool_executor import IToolExecutor
from src.agent.application.ports.i_tool_kit import IToolKit
from src.agent.domain.value_objects import ToolName


class ToolKit(IToolKit):
    def __init__(self) -> None:
        self._tools: dict[str, IToolExecutor] = {}

    def register(self, tool: IToolExecutor) -> None:
        self._tools[tool.name.value] = tool

    def find(self, name: ToolName) -> IToolExecutor | None:
        return self._tools.get(name.value)

    def all(self) -> list[IToolExecutor]:
        return list(self._tools.values())
