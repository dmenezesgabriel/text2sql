from __future__ import annotations

from typing import Protocol

from src.agent.domain.value_objects import ToolName
from src.agent.application.ports.i_tool_executor import IToolExecutor


class IToolKit(Protocol):
    def register(self, tool: IToolExecutor) -> None: ...

    def find(self, name: ToolName) -> IToolExecutor | None: ...

    def all(self) -> list[IToolExecutor]: ...
