from __future__ import annotations

from dataclasses import dataclass

from src.shared.domain.base import ResponseKind, ValueObject


@dataclass(frozen=True)
class QuestionTitle(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            msg = "Question title cannot be empty"
            raise ValueError(msg)


@dataclass(frozen=True)
class SqlQuery(ValueObject):
    value: str

    def is_select(self) -> bool:
        return self.value.strip().upper().startswith("SELECT")


@dataclass(frozen=True)
class VizSpec(ValueObject):
    _component: str
    _props: dict[str, object]
    _children: tuple[object, ...]


@dataclass(frozen=True)
class VizDecision(ValueObject):
    _format: ResponseKind
    _spec: VizSpec
