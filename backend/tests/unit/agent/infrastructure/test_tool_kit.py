from __future__ import annotations

from src.agent.application.ports.i_tool_executor import IToolExecutor
from src.agent.domain.value_objects import Parameters, QueryResult, ToolName
from src.agent.infrastructure.tool_kit import ToolKit


class FakeToolExecutor(IToolExecutor):
    @property
    def name(self) -> ToolName:
        return ToolName("fake_tool")

    async def can_handle(self, query: str) -> bool:
        return True

    async def execute(self, parameters: Parameters) -> QueryResult:
        return QueryResult(_columns=(), _rows=())


class TestToolKit:
    def test_register_and_find(self) -> None:
        kit = ToolKit()
        tool = FakeToolExecutor()
        kit.register(tool)
        found = kit.find(ToolName("fake_tool"))
        assert found is tool

    def test_find_unknown_returns_none(self) -> None:
        kit = ToolKit()
        assert kit.find(ToolName("nonexistent")) is None

    def test_all_returns_registered_tools(self) -> None:
        kit = ToolKit()
        tool = FakeToolExecutor()
        kit.register(tool)
        assert tool in kit.all()

    def test_empty_toolkit_returns_no_tools(self) -> None:
        kit = ToolKit()
        assert kit.all() == []
