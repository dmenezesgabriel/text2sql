from __future__ import annotations

from typing import Protocol

from src.chat.application.ports.i_tool_executor import IToolExecutor
from src.chat.domain.value_objects import ToolName


class IToolKit(Protocol):
    def register(self, tool: IToolExecutor) -> None: ...

    def find(self, name: ToolName) -> IToolExecutor | None: ...

    def all(self) -> list[IToolExecutor]: ...
