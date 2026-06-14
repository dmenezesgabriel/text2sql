from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum, auto
from uuid import uuid4

from src.chat.domain.value_objects import (
    MessageContent,
    MessageRole,
    ModelProvider,
    SystemPrompt,
    Temperature,
    TokenCount,
    ToolCallEvent,
)
from src.chat.exceptions.closed_conversation_error import ClosedConversationError
from src.chat.exceptions.conversation_order_error import ConversationOrderError
from src.shared.domain.base import CreatedAt, Entity, EntityId, ValueObject


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

    def supports_tool(self, tool_name: str) -> bool:
        return self._profile._model.supports_tool_calling()

    def context_limit_is(self, limit: TokenCount) -> bool:
        return self._profile._directives.within_limit(limit)


@dataclass(frozen=True)
class MessageIdentity(ValueObject):
    _id: EntityId
    _role: MessageRole
    _timestamp: CreatedAt


@dataclass(frozen=True)
class MessageBody(ValueObject):
    _content: MessageContent
    _tool_call: ToolCallEvent | None


class Message(Entity):
    def __init__(self, identity: MessageIdentity, body: MessageBody) -> None:
        if body._content.is_empty():
            msg = "Message content cannot be empty"
            raise ValueError(msg)
        self._identity = identity
        self._body = body

    def is_from(self, role: MessageRole) -> bool:
        return self._identity._role is role

    def has_tool_call(self) -> bool:
        return self._body._tool_call is not None


class Messages:
    def __init__(self) -> None:
        self._items: list[Message] = []

    def append(self, message: Message) -> None:
        if self._items and self._items[-1].is_from(message._identity._role):
            msg = (
                f"Cannot append {message._identity._role.name} "
                f"after {self._items[-1]._identity._role.name}"
            )
            raise ConversationOrderError(msg)
        self._items.append(message)

    def trim_to_token_limit(self, limit: TokenCount) -> None:
        system = [m for m in self._items if m.is_from(MessageRole.SYSTEM)]
        non_system = [m for m in self._items if not m.is_from(MessageRole.SYSTEM)]
        total = sum(len(m._body._content.value) for m in non_system)
        while total > limit.value and non_system:
            dropped = non_system.pop(0)
            total -= len(dropped._body._content.value)
        self._items = system + non_system

    def recent_context(self, window: int) -> list[Message]:
        system = [m for m in self._items if m.is_from(MessageRole.SYSTEM)]
        rest = [m for m in self._items if not m.is_from(MessageRole.SYSTEM)]
        return system + rest[-window:]

    def summary(self) -> str:
        lines: list[str] = []
        for msg in self._items:
            role = "U" if msg.is_from(MessageRole.USER) else "A"
            lines.append(f"{role}: {msg._body._content.value}")
        return "\n".join(lines)

    def to_list(self) -> list[Message]:
        return list(self._items)


class ConversationThread:
    """Bundles conversation history and lifecycle state."""

    def __init__(self, history: Messages | None = None) -> None:
        self._history = history or Messages()
        self._state: ConversationState = ConversationState.ACTIVE


class Conversation(Entity):
    def __init__(self, identity: EntityId, history: Messages | None = None) -> None:
        self._identity = identity
        self._thread = ConversationThread(history)

    @property
    def _history(self) -> Messages:
        return self._thread._history

    @property
    def _state(self) -> ConversationState:
        return self._thread._state

    def add_user_message(self, content: str) -> Message:
        if self._thread._state is ConversationState.CLOSED:
            msg = f"Conversation {self._identity.value} is closed"
            raise ClosedConversationError(msg)
        message = Message(
            identity=MessageIdentity(
                _id=EntityId(uuid4()),
                _role=MessageRole.USER,
                _timestamp=CreatedAt(datetime.now(UTC)),
            ),
            body=MessageBody(
                _content=MessageContent(content),
                _tool_call=None,
            ),
        )
        self._thread._history.append(message)
        return message

    def add_assistant_response(
        self,
        content: str,
        tool_call: ToolCallEvent | None,
    ) -> Message:
        message = Message(
            identity=MessageIdentity(
                _id=EntityId(uuid4()),
                _role=MessageRole.ASSISTANT,
                _timestamp=CreatedAt(datetime.now(UTC)),
            ),
            body=MessageBody(
                _content=MessageContent(content),
                _tool_call=tool_call,
            ),
        )
        self._thread._history.append(message)
        return message

    def should_summarize(self, threshold: TokenCount) -> bool:
        total = sum(len(m._body._content.value) for m in self._thread._history.to_list())
        return TokenCount(total).value > threshold.value

    def history_text(self) -> str:
        return self._thread._history.summary()

    def recent_messages(self, window: int) -> list[Message]:
        return self._thread._history.recent_context(window)

    def apply_summary(self, summary: str, recent: list[Message]) -> None:
        """Replace history: one SYSTEM summary message followed by `recent`."""
        self._thread._history = Messages()
        self._thread._history.append(
            Message(
                identity=MessageIdentity(
                    _id=EntityId(uuid4()),
                    _role=MessageRole.SYSTEM,
                    _timestamp=CreatedAt(datetime.now(UTC)),
                ),
                body=MessageBody(
                    _content=MessageContent(f"Summary of earlier conversation: {summary}"),
                    _tool_call=None,
                ),
            ),
        )
        for msg in recent:
            self._thread._history.append(msg)

    def close(self) -> None:
        self._thread._state = ConversationState.CLOSED
