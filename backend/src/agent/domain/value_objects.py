from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from uuid import UUID, uuid4

from src.shared.domain.base import ValueObject


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
            raise ValueError(f"Temperature must be between 0 and 2, got {self.value}")


@dataclass(frozen=True)
class Parameters(ValueObject):
    value: dict


@dataclass(frozen=True)
class TokenCount(ValueObject):
    value: int

    def is_within_limit(self, limit: TokenCount) -> bool:
        return self.value <= limit.value


class ResponseKind(Enum):
    CHART = auto()
    TABLE = auto()
    TEXT = auto()
    DASHBOARD = auto()


@dataclass(frozen=True)
class ResponseFormat(ValueObject):
    _kind: ResponseKind
    _reasoning: str

    def kind_is(self, kind: ResponseKind) -> bool:
        return self._kind is kind


@dataclass(frozen=True)
class QueryResult(ValueObject):
    _columns: tuple[str, ...]
    _rows: tuple[dict[str, object], ...]

    def column_count(self) -> int:
        return len(self._columns)

    def row_count(self) -> int:
        return len(self._rows)

    def has_numeric_columns(self) -> bool:
        return any(
            isinstance(row.get(col), (int, float))
            for col in self._columns
            for row in self._rows
        )


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
