from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from uuid import UUID

from src.shared.domain.base import QueryResult, ResponseKind, ValueObject

__all__ = ["QueryResult", "ResponseKind"]  # re-export so existing imports still work


@dataclass(frozen=True)
class ConversationId(ValueObject):
    value: UUID


@dataclass(frozen=True)
class MessageContent(ValueObject):
    value: str

    def is_empty(self) -> bool:
        return len(self.value.strip()) == 0


@dataclass(frozen=True)
class ToolName(ValueObject):
    value: str


@dataclass(frozen=True)
class ModelProvider(ValueObject):
    value: str


@dataclass(frozen=True)
class SystemPrompt(ValueObject):
    value: str


@dataclass(frozen=True)
class Temperature(ValueObject):
    value: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 2.0:
            msg = f"Temperature must be between 0 and 2, got {self.value}"
            raise ValueError(msg)


@dataclass(frozen=True)
class Parameters(ValueObject):
    value: dict


@dataclass(frozen=True)
class TokenCount(ValueObject):
    value: int

    def is_within_limit(self, limit: TokenCount) -> bool:
        return self.value <= limit.value


@dataclass(frozen=True)
class ResponseFormat(ValueObject):
    _kind: ResponseKind
    _reasoning: str

    def kind_is(self, kind: ResponseKind) -> bool:
        return self._kind is kind


class AgentEvent:
    pass


@dataclass(frozen=True)
class ThinkingEvent(AgentEvent):
    message: str


@dataclass(frozen=True)
class ToolCallEvent(AgentEvent):
    _tool_name: ToolName
    _parameters: Parameters


@dataclass(frozen=True)
class SpecFragmentEvent(AgentEvent):
    _payload: dict


@dataclass(frozen=True)
class ErrorEvent(AgentEvent):
    _message: str


class MessageRole(Enum):
    USER = auto()
    ASSISTANT = auto()
    SYSTEM = auto()
    TOOL = auto()


@dataclass(frozen=True)
class LLMToolCall(ValueObject):
    _id: str
    _name: str
    _arguments: dict


@dataclass(frozen=True)
class LLMToolResponse(ValueObject):
    _text: str | None
    _tool_calls: tuple[LLMToolCall, ...]
    _stop_reason: str

    def has_tool_calls(self) -> bool:
        return len(self._tool_calls) > 0
