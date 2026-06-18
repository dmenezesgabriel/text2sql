from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest

from src.shared.domain.base import (
    AuditRecord,
    CreatedAt,
    Entity,
    EntityId,
    QueryResult,
    ResponseKind,
    UpdatedAt,
    ValueObject,
)


class TestEntityId:
    def test_equality_same_uuid(self) -> None:
        uid = uuid4()
        assert EntityId(uid) == EntityId(uid)

    def test_inequality_different_uuid(self) -> None:
        assert EntityId(uuid4()) != EntityId(uuid4())

    def test_hashable(self) -> None:
        uid = uuid4()
        s = {EntityId(uid)}
        assert EntityId(uid) in s

    def test_not_equal_to_non_entity_id(self) -> None:
        entity_id = EntityId(uuid4())
        assert entity_id.__eq__("not an entity id") is NotImplemented


class TestCreatedAt:
    def test_is_after(self) -> None:
        earlier = CreatedAt(datetime(2024, 1, 1))
        later = CreatedAt(datetime(2025, 1, 1))
        assert later.is_after(earlier)
        assert not earlier.is_after(later)


class TestAuditRecord:
    def test_touch_updates_updated_at(self) -> None:
        created = CreatedAt(datetime(2024, 1, 1))
        updated = UpdatedAt(datetime(2024, 1, 1))
        record = AuditRecord(_created=created, _updated=updated)
        new_record = record.touch()
        assert new_record._created == created
        assert new_record._updated != updated


class TestValueObject:
    def test_value_object_is_dataclass(self) -> None:
        import dataclasses

        assert dataclasses.is_dataclass(ValueObject)

    def test_frozen_subclass_cannot_be_mutated(self) -> None:
        from dataclasses import FrozenInstanceError, dataclass

        @dataclass(frozen=True)
        class ConcreteVO(ValueObject):
            x: int = 0

        vo = ConcreteVO(x=1)
        with pytest.raises(FrozenInstanceError):
            vo.__class__.__setattr__(vo, "x", 99)


class TestQueryResult:
    def test_column_count(self) -> None:
        result = QueryResult(_columns=("id", "name"), _rows=())
        assert result.column_count() == 2

    def test_row_count(self) -> None:
        result = QueryResult(
            _columns=("id",),
            _rows=({"id": 1}, {"id": 2}),
        )
        assert result.row_count() == 2

    def test_has_numeric_columns_true(self) -> None:
        result = QueryResult(
            _columns=("amount",),
            _rows=({"amount": 42.5},),
        )
        assert result.has_numeric_columns()

    def test_has_numeric_columns_false(self) -> None:
        result = QueryResult(
            _columns=("name",),
            _rows=({"name": "Alice"},),
        )
        assert not result.has_numeric_columns()


class _ConcreteEntity(Entity):
    def __init__(self, identity: EntityId | None = None) -> None:
        if identity is not None:
            self._identity = identity


class TestEntity:
    def test_equal_with_same_identity(self) -> None:
        uid = uuid4()
        assert _ConcreteEntity(EntityId(uid)) == _ConcreteEntity(EntityId(uid))

    def test_not_equal_with_different_identity(self) -> None:
        assert _ConcreteEntity(EntityId(uuid4())) != _ConcreteEntity(EntityId(uuid4()))

    def test_not_equal_to_non_entity_returns_not_implemented(self) -> None:
        result = _ConcreteEntity(EntityId(uuid4())).__eq__("not an entity")
        assert result is NotImplemented

    def test_two_entities_without_identity_are_equal(self) -> None:
        # getattr fallback to None for both sides
        assert _ConcreteEntity() == _ConcreteEntity()

    def test_entity_with_identity_not_equal_to_entity_without(self) -> None:
        assert _ConcreteEntity(EntityId(uuid4())) != _ConcreteEntity()


class TestResponseKind:
    def test_all_variants(self) -> None:
        assert ResponseKind.CHART
        assert ResponseKind.TABLE
        assert ResponseKind.TEXT
        assert ResponseKind.DASHBOARD
