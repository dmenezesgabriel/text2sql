from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol
from dataclasses import dataclass, field
from datetime import datetime

from uuid import UUID, uuid4


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
            _updated=UpdatedAt(datetime.utcnow()),
        )


@dataclass(frozen=True)
class DomainEvent:
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)


class Entity:
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return self._identity == other._identity

    def __hash__(self) -> int:
        return hash(self._identity)


class AggregateRoot(Entity):
    def __init__(self) -> None:
        self._events: list[DomainEvent] = []

    def _record(self, event: DomainEvent) -> None:
        self._events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        events = list(self._events)
        self._events.clear()
        return events


@dataclass(frozen=True)
class ValueObject:
    pass


class EntityCollection[T: Entity](ABC):
    @abstractmethod
    def add(self, entity: T) -> None: ...

    @abstractmethod
    def remove(self, entity_id: EntityId) -> None: ...

    @abstractmethod
    def contains(self, entity_id: EntityId) -> bool: ...

    @abstractmethod
    def to_list(self) -> list[T]: ...
