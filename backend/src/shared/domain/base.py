from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum, auto
from uuid import UUID


@dataclass(frozen=True)
class EntityId:
    value: UUID

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EntityId):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class CreatedAt:
    value: datetime

    def is_after(self, other: CreatedAt) -> bool:
        return self.value > other.value


@dataclass(frozen=True)
class UpdatedAt:
    value: datetime


@dataclass(frozen=True)
class AuditRecord:
    _created: CreatedAt
    _updated: UpdatedAt

    def touch(self) -> AuditRecord:
        return AuditRecord(
            _created=self._created,
            _updated=UpdatedAt(datetime.now(UTC)),
        )


class Entity:
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return getattr(self, "_identity", None) == getattr(other, "_identity", None)

    def __hash__(self) -> int:
        return hash(getattr(self, "_identity", None))


@dataclass(frozen=True)
class ValueObject:
    pass


class ResponseKind(Enum):
    """Visualization format shared across agent and questions domains."""

    CHART = auto()
    TABLE = auto()
    TEXT = auto()
    DASHBOARD = auto()


@dataclass(frozen=True)
class QueryResult(ValueObject):
    """Generic SQL query result shared by the query engine and executor ports."""

    _columns: tuple[str, ...]
    _rows: tuple[dict[str, object], ...]

    def column_count(self) -> int:
        return len(self._columns)

    def row_count(self) -> int:
        return len(self._rows)

    def has_numeric_columns(self) -> bool:
        return any(
            isinstance(row.get(col), (int, float)) for col in self._columns for row in self._rows
        )


class EntityCollection[T: Entity](ABC):
    @abstractmethod
    def add(self, entity: T) -> None: ...

    @abstractmethod
    def remove(self, entity_id: EntityId) -> None: ...

    @abstractmethod
    def contains(self, entity_id: EntityId) -> bool: ...

    @abstractmethod
    def to_list(self) -> list[T]: ...
