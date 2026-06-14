from __future__ import annotations

from uuid import uuid4

import pytest

from src.chat.domain.entities import (
    AgentConfiguration,
    AgentDirectives,
    Conversation,
    Messages,
    ModelConfig,
)
from src.chat.domain.value_objects import (
    ModelProvider,
    SystemPrompt,
    Temperature,
    TokenCount,
)
from src.shared.domain.base import EntityId


def _make_model_config() -> ModelConfig:
    return ModelConfig(
        _provider=ModelProvider("openai"),
        _temperature=Temperature(0.7),
    )


def _make_directives() -> AgentDirectives:
    return AgentDirectives(
        _system=SystemPrompt("You are a helpful assistant."),
        _max_tokens=TokenCount(1000),
    )


def _make_agent_config() -> AgentConfiguration:
    return AgentConfiguration(
        identity=EntityId(uuid4()),
        model=_make_model_config(),
        directives=_make_directives(),
    )


def _make_conversation() -> Conversation:
    return Conversation(identity=EntityId(uuid4()), history=Messages())


class TestAgentConfiguration:
    def test_provider_is_detects_matching_provider(self) -> None:
        config = _make_agent_config()
        assert config.provider_is("openai")
        assert not config.provider_is("anthropic")

    def test_with_temperature_returns_new_config(self) -> None:
        config = _make_agent_config()
        new_config = config.with_temperature(Temperature(1.0))
        assert new_config is not config

    def test_supports_tool_returns_true(self) -> None:
        config = _make_agent_config()
        assert config.supports_tool("any_tool")

    def test_context_limit_is_within_limit(self) -> None:
        config = _make_agent_config()
        assert config.context_limit_is(TokenCount(500))
        assert not config.context_limit_is(TokenCount(2000))


class TestConversation:
    def test_add_user_message_appends_to_history(self) -> None:
        conv = _make_conversation()
        msg = conv.add_user_message("Hello")
        assert msg._body._content.value == "Hello"
        assert len(conv._history.to_list()) == 1

    def test_should_summarize_exceeds_limit(self) -> None:
        conv = _make_conversation()
        conv.add_user_message("x" * 100)
        assert conv.should_summarize(TokenCount(50))
        assert not conv.should_summarize(TokenCount(200))

    def test_close_prevents_new_messages(self) -> None:
        conv = _make_conversation()
        conv.close()
        with pytest.raises(Exception):
            conv.add_user_message("Should fail")

    def test_new_conversation_accepts_messages(self) -> None:
        conv = _make_conversation()
        msg = conv.add_user_message("Hi")
        assert msg is not None

    def test_history_text_returns_formatted_messages(self) -> None:
        conv = _make_conversation()
        conv.add_user_message("Hello")
        assert "Hello" in conv.history_text()

    def test_recent_messages_returns_last_n(self) -> None:
        conv = _make_conversation()
        conv.add_user_message("first")
        conv.add_assistant_response("response", None)
        conv.add_user_message("second")
        recent = conv.recent_messages(window=1)
        assert len(recent) == 1
        assert recent[0]._body._content.value == "second"

    def test_apply_summary_replaces_history(self) -> None:
        conv = _make_conversation()
        conv.add_user_message("old message")
        conv.add_assistant_response("old reply", None)
        recent = conv.recent_messages(window=1)
        conv.apply_summary("compressed context", recent)
        messages = conv._history.to_list()
        assert (
            messages[0]._body._content.value
            == "Summary of earlier conversation: compressed context"
        )
        assert messages[-1]._body._content.value == "old reply"
