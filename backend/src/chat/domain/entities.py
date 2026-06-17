from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from src.chat.domain.value_objects import (
    ModelProvider,
    SystemPrompt,
    Temperature,
    TokenCount,
)
from src.chat.exceptions.closed_conversation_error import ClosedConversationError
from src.shared.domain.base import Entity, EntityId, ValueObject


class ConversationState(Enum):
    ACTIVE = auto()
    CLOSED = auto()


@dataclass(frozen=True)
class ModelConfig(ValueObject):
    _provider: ModelProvider
    _temperature: Temperature

    def provider_is(self, provider: str) -> bool:
        return self._provider.value == provider

    def supports_tool_calling(self) -> bool:
        return True

    def with_temperature(self, temperature: Temperature) -> ModelConfig:
        return ModelConfig(_provider=self._provider, _temperature=temperature)


@dataclass(frozen=True)
class AgentDirectives(ValueObject):
    _system: SystemPrompt
    _max_tokens: TokenCount

    def within_limit(self, count: TokenCount) -> bool:
        return count.is_within_limit(self._max_tokens)


@dataclass(frozen=True)
class AgentProfile(ValueObject):
    """Bundles model config and directives for an agent configuration."""

    _model: ModelConfig
    _directives: AgentDirectives


class AgentConfiguration(Entity):
    def __init__(
        self,
        identity: EntityId,
        model: ModelConfig,
        directives: AgentDirectives,
    ) -> None:
        self._identity = identity
        self._profile = AgentProfile(_model=model, _directives=directives)

    def provider_is(self, provider: str) -> bool:
        return self._profile._model.provider_is(provider)

    def with_temperature(self, temperature: Temperature) -> AgentConfiguration:
        return AgentConfiguration(
            identity=self._identity,
            model=self._profile._model.with_temperature(temperature),
            directives=self._profile._directives,
        )

    def supports_tool(self, _tool_name: str) -> bool:
        return self._profile._model.supports_tool_calling()

    def context_limit_is(self, limit: TokenCount) -> bool:
        return self._profile._directives.within_limit(limit)


class Conversation(Entity):
    """Conversation metadata. Message history is managed by LangGraph checkpointing."""

    def __init__(self, identity: EntityId) -> None:
        self._identity = identity
        self._state: ConversationState = ConversationState.ACTIVE

    def close(self) -> None:
        if self._state is ConversationState.CLOSED:
            msg = f"Conversation {self._identity.value} is already closed"
            raise ClosedConversationError(msg)
        self._state = ConversationState.CLOSED

    def is_closed(self) -> bool:
        return self._state is ConversationState.CLOSED
