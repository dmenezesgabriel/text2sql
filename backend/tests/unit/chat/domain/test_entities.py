from __future__ import annotations

from uuid import uuid4

import pytest

from src.chat.domain.entities import (
    AgentConfiguration,
    AgentDirectives,
    Conversation,
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
    def test_new_conversation_is_active(self) -> None:
        conv = Conversation(identity=EntityId(uuid4()))
        assert not conv.is_closed()

    def test_close_marks_as_closed(self) -> None:
        conv = Conversation(identity=EntityId(uuid4()))
        conv.close()
        assert conv.is_closed()

    def test_close_twice_raises(self) -> None:
        conv = Conversation(identity=EntityId(uuid4()))
        conv.close()
        with pytest.raises(Exception):
            conv.close()
