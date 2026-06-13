from __future__ import annotations

from src.agent.domain.value_objects import (
    ErrorEvent,
    Parameters,
    SpecFragmentEvent,
    ThinkingEvent,
    ToolCallEvent,
    ToolName,
)
from src.agent.infrastructure.fastapi.router import _serialize_event, create_chat_router


class TestSerializeEvent:
    def test_thinking_event(self) -> None:
        result = _serialize_event(ThinkingEvent(message="processing"))
        assert result["type"] == "ThinkingEvent"
        assert result["payload"] == "processing"

    def test_tool_call_event(self) -> None:
        event = ToolCallEvent(
            _tool_name=ToolName("sql_generator"),
            _parameters=Parameters({"sql": "SELECT 1"}),
        )
        result = _serialize_event(event)
        assert result["type"] == "ToolCallEvent"
        assert result["payload"]["tool_name"] == "sql_generator"

    def test_spec_fragment_event(self) -> None:
        event = SpecFragmentEvent(_payload={"chart": "bar"})
        result = _serialize_event(event)
        assert result["type"] == "SpecFragmentEvent"
        assert result["payload"] == {"chart": "bar"}

    def test_error_event(self) -> None:
        event = ErrorEvent(_message="something failed")
        result = _serialize_event(event)
        assert result["type"] == "ErrorEvent"
        assert result["payload"] == "something failed"

    def test_unknown_event_fallback(self) -> None:
        class UnknownEvent:
            pass

        result = _serialize_event(UnknownEvent())  # type: ignore[arg-type]
        assert result["type"] == "UnknownEvent"


class TestCreateChatRouter:
    def test_router_is_created(self) -> None:
        router = create_chat_router()
        assert router is not None

    def test_router_prefix(self) -> None:
        router = create_chat_router()
        assert router.prefix == "/api/v1/chat"
