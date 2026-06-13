from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from src.shared.domain.base import ValueObject, EntityId


@dataclass(frozen=True)
class DashboardTitle(ValueObject):
    value: str


@dataclass(frozen=True)
class TilePosition(ValueObject):
    _row: int
    _col: int
    _width: int
    _height: int


@dataclass(frozen=True)
class FilterBinding(ValueObject):
    _source_tile: EntityId
    _column: str
    _target_tiles: frozenset[EntityId]
