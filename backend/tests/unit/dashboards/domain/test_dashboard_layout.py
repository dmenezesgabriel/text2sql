from __future__ import annotations

from uuid import uuid4

import pytest

from src.dashboards.domain.entities import DashboardLayout, DashboardTile, TileIdentity, Tiles
from src.dashboards.domain.value_objects import DashboardTitle, TilePosition
from src.shared.domain.base import EntityId


def _make_tile(row: int = 0, col: int = 0, width: int = 1, height: int = 1) -> DashboardTile:
    return DashboardTile(
        identity=TileIdentity(
            _id=EntityId(uuid4()),
            _position=TilePosition(_row=row, _col=col, _width=width, _height=height),
        ),
        source=None,  # type: ignore[arg-type]
    )


def _make_layout(title: str = "Dashboard") -> DashboardLayout:
    return DashboardLayout(title=DashboardTitle(title), tiles=Tiles())


class TestDashboardLayout:
    def test_add_tile_stores_tile(self) -> None:
        layout = _make_layout()
        tile = _make_tile(row=0, col=0)
        layout.add_tile(tile)
        assert tile in layout._tiles.to_list()

    def test_add_overlapping_tile_raises(self) -> None:
        layout = _make_layout()
        layout.add_tile(_make_tile(row=0, col=0, width=2, height=2))
        with pytest.raises(Exception):
            layout.add_tile(_make_tile(row=0, col=1))

    def test_bind_filter_links_tiles(self) -> None:
        layout = _make_layout()
        source = _make_tile(row=0, col=0)
        target = _make_tile(row=1, col=0)
        layout.add_tile(source)
        layout.add_tile(target)
        layout.bind_filter(
            source_tile_id=source._identity._id,
            column="region",
            target_tile_ids={target._identity._id},
        )
        affected = layout.tiles_affected_by(source._identity._id, "region")
        assert target in affected

    def test_tiles_affected_by_returns_empty_with_no_bindings(self) -> None:
        layout = _make_layout()
        tile = _make_tile()
        layout.add_tile(tile)
        assert layout.tiles_affected_by(tile._identity._id, "col") == []

    def test_remove_tile_cleans_filters(self) -> None:
        layout = _make_layout()
        source = _make_tile(row=0, col=0)
        target = _make_tile(row=1, col=0)
        layout.add_tile(source)
        layout.add_tile(target)
        layout.bind_filter(
            source_tile_id=source._identity._id,
            column="x",
            target_tile_ids={target._identity._id},
        )
        layout.remove_tile(target._identity._id)
        affected = layout.tiles_affected_by(source._identity._id, "x")
        assert affected == []
