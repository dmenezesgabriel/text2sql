from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import uuid4

from src.agent.domain.entities import Conversation, Message, MessageBody, MessageIdentity, Messages
from src.agent.domain.value_objects import (
    AgentEvent,
    ErrorEvent,
    LLMToolCall,
    LLMToolResponse,
    MessageContent,
    MessageRole,
    Parameters,
    SpecFragmentEvent,
    ThinkingEvent,
    ToolName,
)
from src.agent.infrastructure.deep_agents import DeepAgentsOrchestrator
from src.datasets.domain.entities import Datasets
from src.shared.domain.base import CreatedAt, EntityId, QueryResult


class FakeLLMProvider:
    def __init__(self, responses: list[LLMToolResponse]) -> None:
        self._responses = list(responses)
        self._call_count = 0

    async def call_with_tools(self, messages: list[dict], tools: list[dict]) -> LLMToolResponse:
        response = self._responses[self._call_count % len(self._responses)]
        self._call_count += 1
        return response

    async def generate(self, messages: object, config: object) -> str:
        return ""


class FakeDatasetRepository:
    def find_all(self) -> Datasets:
        return Datasets()

    def save(self, dataset: object) -> None:
        pass

    def load(self, dataset_id: object) -> None:
        return None

    def delete(self, dataset_id: object) -> None:
        pass


class FakeSqlTool:
    @property
    def name(self) -> ToolName:
        return ToolName("sql_generator")

    async def execute(self, parameters: Parameters) -> QueryResult:
        return QueryResult(_columns=("count",), _rows=({"count": 1},))

    async def can_handle(self, query: str) -> bool:
        return True


class FakeToolKit:
    def __init__(self) -> None:
        self._sql_tool = FakeSqlTool()

    def find(self, name: ToolName) -> FakeSqlTool | None:
        if name.value == "sql_generator":
            return self._sql_tool
        return None

    def register(self, tool: object) -> None:
        pass

    def all(self) -> list[object]:
        return [self._sql_tool]


def _make_conversation() -> Conversation:
    return Conversation(identity=EntityId(uuid4()), history=Messages())


def _make_user_message() -> Message:
    return Message(
        identity=MessageIdentity(
            _id=EntityId(uuid4()),
            _role=MessageRole.USER,
            _timestamp=CreatedAt(datetime.now(UTC)),
        ),
        body=MessageBody(
            _content=MessageContent("what is the count?"),
            _tool_call=None,
        ),
    )


async def _collect(gen: AsyncIterator[AgentEvent]) -> list[AgentEvent]:
    return [event async for event in gen]


class TestDeepAgentsOrchestrator:
    def setup_method(self) -> None:
        self.datasets = FakeDatasetRepository()
        self.toolkit = FakeToolKit()

    async def test_yields_thinking_event_at_start(self) -> None:
        llm = FakeLLMProvider(
            [
                LLMToolResponse(_text="done", _tool_calls=(), _stop_reason="stop"),
            ],
        )
        orchestrator = DeepAgentsOrchestrator(llm=llm, datasets=self.datasets)
        events = await _collect(
            orchestrator.run(_make_user_message(), _make_conversation(), self.toolkit),
        )
        assert any(isinstance(e, ThinkingEvent) for e in events)

    async def test_yields_spec_fragment_when_no_tool_calls(self) -> None:
        llm = FakeLLMProvider(
            [
                LLMToolResponse(_text="Here is the answer.", _tool_calls=(), _stop_reason="stop"),
            ],
        )
        orchestrator = DeepAgentsOrchestrator(llm=llm, datasets=self.datasets)
        events = await _collect(
            orchestrator.run(_make_user_message(), _make_conversation(), self.toolkit),
        )
        spec_events = [e for e in events if isinstance(e, SpecFragmentEvent)]
        assert len(spec_events) == 1

    async def test_terminates_after_build_visualization_tool_call(self) -> None:
        spec_payload = {"root": "c", "elements": {"c": {"type": "BarChart", "props": {}}}}
        llm = FakeLLMProvider(
            [
                LLMToolResponse(
                    _text=None,
                    _tool_calls=(
                        LLMToolCall(
                            _id="t1",
                            _name="build_visualization",
                            _arguments={"spec": spec_payload},
                        ),
                    ),
                    _stop_reason="tool_calls",
                ),
            ],
        )
        orchestrator = DeepAgentsOrchestrator(llm=llm, datasets=self.datasets)
        events = await _collect(
            orchestrator.run(_make_user_message(), _make_conversation(), self.toolkit),
        )
        spec_events = [e for e in events if isinstance(e, SpecFragmentEvent)]
        assert len(spec_events) == 1
        assert spec_events[0]._payload == spec_payload

    async def test_handles_generate_sql_then_build_visualization(self) -> None:
        spec_payload = {"root": "t", "elements": {}}
        sql_response = LLMToolResponse(
            _text=None,
            _tool_calls=(
                LLMToolCall(
                    _id="s1",
                    _name="generate_sql",
                    _arguments={"sql": "SELECT 1", "reasoning": "test"},
                ),
            ),
            _stop_reason="tool_calls",
        )
        viz_response = LLMToolResponse(
            _text=None,
            _tool_calls=(
                LLMToolCall(
                    _id="v1",
                    _name="build_visualization",
                    _arguments={"spec": spec_payload},
                ),
            ),
            _stop_reason="tool_calls",
        )
        llm = FakeLLMProvider([sql_response, viz_response])
        orchestrator = DeepAgentsOrchestrator(llm=llm, datasets=self.datasets)
        events = await _collect(
            orchestrator.run(_make_user_message(), _make_conversation(), self.toolkit),
        )
        spec_events = [e for e in events if isinstance(e, SpecFragmentEvent)]
        assert len(spec_events) == 1
        assert spec_events[0]._payload == spec_payload

    async def test_yields_error_after_max_steps_without_visualization(self) -> None:
        sql_response = LLMToolResponse(
            _text=None,
            _tool_calls=(
                LLMToolCall(
                    _id="s1",
                    _name="generate_sql",
                    _arguments={"sql": "SELECT 1", "reasoning": "x"},
                ),
            ),
            _stop_reason="tool_calls",
        )
        llm = FakeLLMProvider([sql_response])
        orchestrator = DeepAgentsOrchestrator(llm=llm, datasets=self.datasets)
        events = await _collect(
            orchestrator.run(_make_user_message(), _make_conversation(), self.toolkit),
        )
        error_events = [e for e in events if isinstance(e, ErrorEvent)]
        assert len(error_events) == 1
