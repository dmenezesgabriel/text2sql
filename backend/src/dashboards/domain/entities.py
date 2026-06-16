from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from src.dashboards.domain.value_objects import DashboardTitle, FilterBinding, TilePosition
from src.dashboards.exceptions.self_filter_error import SelfFilterError
from src.dashboards.exceptions.tile_not_found_error import TileNotFoundError
from src.dashboards.exceptions.tile_overlap_error import TileOverlapError
from src.questions.domain.entities import Question
from src.shared.domain.base import AuditRecord, Entity, EntityId, ValueObject


@dataclass(frozen=True)
class TileIdentity(ValueObject):
    _id: EntityId
    _position: TilePosition


class DashboardTile(Entity):
    def __init__(self, identity: TileIdentity, source: Question) -> None:
        self._identity = identity
        self._source = source

    def position(self) -> TilePosition:
        return self._identity._position


class Tiles:
    def __init__(
        self,
        items: list[DashboardTile] | None = None,
    ) -> None:
        self._items: list[DashboardTile] = items or []

    def add(self, tile: DashboardTile) -> None:
        self._items.append(tile)

    def remove(self, tile_id: EntityId) -> None:
        self._items = [t for t in self._items if t._identity._id != tile_id]

    def contains(self, tile_id: EntityId) -> bool:
        return any(t._identity._id == tile_id for t in self._items)

    def find(self, tile_id: EntityId) -> DashboardTile | None:
        for tile in self._items:
            if tile._identity._id == tile_id:
                return tile
        return None

    def to_list(self) -> list[DashboardTile]:
        return list(self._items)


class DashboardIdentity:
    def __init__(self, entity_id: EntityId, audit: AuditRecord) -> None:
        self._id = entity_id
        self._audit = audit


@dataclass
class LayoutContent:
    """Bundles the immutable composition of a dashboard (title + tiles)."""

    _title: DashboardTitle
    _tiles: Tiles


class DashboardLayout:
    def __init__(self, title: DashboardTitle, tiles: Tiles) -> None:
        self._content = LayoutContent(_title=title, _tiles=tiles)
        self._filters: dict[EntityId, tuple[FilterBinding, ...]] = {}

    @property
    def _title(self) -> DashboardTitle:
        return self._content._title

    @property
    def _tiles(self) -> Tiles:
        return self._content._tiles

    def add_tile(self, tile: DashboardTile) -> None:
        if self._tile_overlaps(tile):
            msg = f"Tile {tile._identity._id.value} overlaps existing tile"
            raise TileOverlapError(msg)
        self._content._tiles.add(tile)

    def remove_tile(self, tile_id: EntityId) -> None:
        self._content._tiles.remove(tile_id)
        self._filters.pop(tile_id, None)
        for source_id, bindings in self._filters.items():
            cleaned = tuple(b for b in bindings if tile_id not in b._target_tiles)
            self._filters[source_id] = cleaned

    def bind_filter(
        self,
        source_tile_id: EntityId,
        column: str,
        target_tile_ids: set[EntityId],
    ) -> None:
        if not self._content._tiles.contains(source_tile_id):
            msg = f"Source tile {source_tile_id.value} not found"
            raise TileNotFoundError(msg)
        for target_id in target_tile_ids:
            if not self._content._tiles.contains(target_id):
                msg = f"Target tile {target_id.value} not found"
                raise TileNotFoundError(msg)
            if target_id == source_tile_id:
                msg = "A tile cannot filter itself"
                raise SelfFilterError(msg)

        binding = FilterBinding(
            _source_tile=source_tile_id,
            _column=column,
            _target_tiles=frozenset(target_tile_ids),
        )
        existing = self._filters.get(source_tile_id, ())
        self._filters[source_tile_id] = existing + (binding,)

    def tiles_affected_by(
        self,
        source_tile_id: EntityId,
        column: str,
    ) -> list[DashboardTile]:
        bindings = self._filters.get(source_tile_id, ())
        targets: set[EntityId] = set()
        for binding in bindings:
            if binding._column == column:
                targets.update(binding._target_tiles)
        return [t for t in self._content._tiles.to_list() if t._identity._id in targets]

    def _tile_overlaps(self, tile: DashboardTile) -> bool:
        pos = tile._identity._position
        for existing in self._content._tiles.to_list():
            epos = existing._identity._position
            if (
                pos._row < epos._row + epos._height
                and pos._row + pos._height > epos._row
                and pos._col < epos._col + epos._width
                and pos._col + pos._width > epos._col
            ):
                return True
        return False


class Dashboard(Entity):
    def __init__(
        self,
        identity: DashboardIdentity,
        layout: DashboardLayout,
    ) -> None:
        self._identity = identity
        self._layout = layout

    def add_tile_from_question(
        self,
        question: Question,
        position: TilePosition,
    ) -> DashboardTile:
        tile = DashboardTile(
            identity=TileIdentity(
                _id=EntityId(uuid4()),
                _position=position,
            ),
            source=question,
        )
        self._layout.add_tile(tile)
        return tile
