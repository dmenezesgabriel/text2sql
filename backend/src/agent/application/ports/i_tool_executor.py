from __future__ import annotations

from typing import Protocol

from src.agent.domain.value_objects import Parameters, QueryResult, ToolName


class IToolExecutor(Protocol):
    @property
    def name(self) -> ToolName: ...

    async def can_handle(self, query: str) -> bool: ...

    async def execute(self, parameters: Parameters) -> QueryResult: ...
