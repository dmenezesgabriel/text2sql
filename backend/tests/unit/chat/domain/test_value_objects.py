from __future__ import annotations

from uuid import uuid4

import pytest

from src.chat.domain.value_objects import (
    ConversationId,
    LLMToolCall,
    LLMToolResponse,
    MessageContent,
    MessageRole,
    Parameters,
    ResponseFormat,
    SpecFragmentEvent,
    Temperature,
    ThinkingEvent,
    TokenCount,
    ToolCallEvent,
    ToolName,
)
from src.shared.domain.base import ResponseKind


class TestConversationId:
    def test_equality_same_uuid(self) -> None:
        uid = uuid4()
        assert ConversationId(uid) == ConversationId(uid)

    def test_inequality_different_uuid(self) -> None:
        assert ConversationId(uuid4()) != ConversationId(uuid4())


class TestMessageContent:
    def test_is_empty_whitespace(self) -> None:
        assert MessageContent("   ").is_empty()

    def test_is_not_empty_with_text(self) -> None:
        assert not MessageContent("hello").is_empty()


class TestTemperature:
    def test_valid_temperature(self) -> None:
        t = Temperature(0.7)
        assert t.value == 0.7

    def test_zero_and_two_are_valid_bounds(self) -> None:
        Temperature(0.0)
        Temperature(2.0)

    def test_out_of_range_raises(self) -> None:
        with pytest.raises(ValueError):
            Temperature(2.1)

    def test_negative_raises(self) -> None:
        with pytest.raises(ValueError):
            Temperature(-0.1)


class TestTokenCount:
    def test_within_limit(self) -> None:
        assert TokenCount(100).is_within_limit(TokenCount(200))

    def test_exceeds_limit(self) -> None:
        assert not TokenCount(300).is_within_limit(TokenCount(200))

    def test_at_limit_boundary(self) -> None:
        assert TokenCount(200).is_within_limit(TokenCount(200))


class TestResponseFormat:
    def test_kind_is_matches(self) -> None:
        fmt = ResponseFormat(_kind=ResponseKind.CHART, _reasoning="it's a chart")
        assert fmt.kind_is(ResponseKind.CHART)
        assert not fmt.kind_is(ResponseKind.TABLE)


class TestAgentEvents:
    def test_thinking_event_holds_message(self) -> None:
        event = ThinkingEvent(message="thinking...")
        assert event.message == "thinking..."

    def test_tool_call_event(self) -> None:
        event = ToolCallEvent(
            _tool_name=ToolName("sql_generator"),
            _parameters=Parameters({"sql": "SELECT 1"}),
        )
        assert event._tool_name.value == "sql_generator"

    def test_spec_fragment_event_valid_payload(self) -> None:
        spec = {
            "root": "answer",
            "elements": {"answer": {"type": "NarrativeText", "props": {"content": "hi"}}},
        }
        event = SpecFragmentEvent(_payload=spec)
        assert event._payload["root"] == "answer"

    def test_spec_fragment_event_invalid_payload_raises(self) -> None:
        with pytest.raises(ValueError):
            SpecFragmentEvent(
                _payload={"root": "x", "elements": {"e": {"type": "ScatterPlot", "props": {}}}},
            )

    def test_spec_fragment_event_empty_elements_is_valid(self) -> None:
        SpecFragmentEvent(_payload={"root": "x", "elements": {}})


class TestMessageRole:
    def test_all_roles_exist(self) -> None:
        assert MessageRole.USER
        assert MessageRole.ASSISTANT
        assert MessageRole.SYSTEM
        assert MessageRole.TOOL


class TestLLMToolResponse:
    def test_has_tool_calls_true(self) -> None:
        call = LLMToolCall(_id="1", _name="sql", _arguments={})
        resp = LLMToolResponse(_text=None, _tool_calls=(call,), _stop_reason="tool_calls")
        assert resp.has_tool_calls()

    def test_has_tool_calls_false(self) -> None:
        resp = LLMToolResponse(_text="done", _tool_calls=(), _stop_reason="stop")
        assert not resp.has_tool_calls()
