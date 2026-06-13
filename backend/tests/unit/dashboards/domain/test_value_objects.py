from __future__ import annotations

from uuid import uuid4

from src.dashboards.domain.value_objects import DashboardTitle, FilterBinding, TilePosition
from src.shared.domain.base import EntityId


class TestDashboardTitle:
    def test_value_stored(self) -> None:
        title = DashboardTitle("My Dashboard")
        assert title.value == "My Dashboard"

    def test_equality(self) -> None:
        assert DashboardTitle("X") == DashboardTitle("X")
        assert DashboardTitle("X") != DashboardTitle("Y")


class TestTilePosition:
    def test_fields_stored(self) -> None:
        pos = TilePosition(_row=1, _col=2, _width=4, _height=3)
        assert pos._row == 1
        assert pos._col == 2
        assert pos._width == 4
        assert pos._height == 3

    def test_equality(self) -> None:
        pos1 = TilePosition(_row=0, _col=0, _width=4, _height=2)
        pos2 = TilePosition(_row=0, _col=0, _width=4, _height=2)
        assert pos1 == pos2


class TestFilterBinding:
    def test_fields_stored(self) -> None:
        src = EntityId(uuid4())
        target = EntityId(uuid4())
        binding = FilterBinding(
            _source_tile=src,
            _column="status",
            _target_tiles=frozenset({target}),
        )
        assert binding._source_tile == src
        assert binding._column == "status"
        assert target in binding._target_tiles
