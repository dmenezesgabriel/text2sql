from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from src.dashboards.domain.entities import (
    Dashboard,
    DashboardIdentity,
    DashboardLayout,
    DashboardTile,
    TileIdentity,
    Tiles,
)
from src.dashboards.domain.value_objects import DashboardTitle, TilePosition
from src.dashboards.exceptions.self_filter_error import SelfFilterError
from src.dashboards.exceptions.tile_not_found_error import TileNotFoundError
from src.dashboards.exceptions.tile_overlap_error import TileOverlapError
from src.questions.domain.entities import (
    DatasetReference,
    QueryDefinition,
    Question,
    QuestionDescription,
    QuestionIdentity,
    QuestionSpecification,
    RenderDirective,
)
from src.questions.domain.value_objects import QuestionTitle, SqlQuery, VizDecision, VizSpec
from src.shared.domain.base import AuditRecord, CreatedAt, EntityId, ResponseKind, UpdatedAt


def _make_question() -> Question:
    return Question(
        identity=QuestionIdentity(
            entity_id=EntityId(uuid4()),
            audit=AuditRecord(
                _created=CreatedAt(datetime.now(UTC)),
                _updated=UpdatedAt(datetime.now(UTC)),
            ),
        ),
        specification=QuestionSpecification(
            description=QuestionDescription(
                _title=QuestionTitle("Q"),
                _query=QueryDefinition(
                    _sql=SqlQuery("SELECT 1"),
                    _source=DatasetReference(_id=EntityId(uuid4()), _alias=None),
                ),
            ),
            rendering=RenderDirective(
                _decision=VizDecision(
                    _format=ResponseKind.TABLE,
                    _spec=VizSpec(_component="Table", _props={}, _children=()),
                ),
            ),
        ),
    )


def _make_tile(row: int = 0, col: int = 0, w: int = 4, h: int = 2) -> DashboardTile:
    return DashboardTile(
        identity=TileIdentity(
            _id=EntityId(uuid4()),
            _position=TilePosition(_row=row, _col=col, _width=w, _height=h),
        ),
        source=_make_question(),
    )


def _make_layout(*tiles: DashboardTile) -> DashboardLayout:
    return DashboardLayout(
        title=DashboardTitle("Test"),
        tiles=Tiles(list(tiles)),
    )


class TestTiles:
    def test_add_and_find(self) -> None:
        tile = _make_tile()
        tiles = Tiles()
        tiles.add(tile)
        assert tiles.find(tile._identity._id) is tile

    def test_contains(self) -> None:
        tile = _make_tile()
        tiles = Tiles([tile])
        assert tiles.contains(tile._identity._id)
        assert not tiles.contains(EntityId(uuid4()))

    def test_remove(self) -> None:
        tile = _make_tile()
        tiles = Tiles([tile])
        tiles.remove(tile._identity._id)
        assert not tiles.contains(tile._identity._id)

    def test_to_list(self) -> None:
        tile = _make_tile()
        tiles = Tiles([tile])
        assert tile in tiles.to_list()


class TestDashboardLayout:
    def test_add_tile_succeeds_when_no_overlap(self) -> None:
        layout = _make_layout()
        tile = _make_tile(row=0, col=0)
        layout.add_tile(tile)
        assert layout._tiles.contains(tile._identity._id)

    def test_add_tile_raises_on_overlap(self) -> None:
        tile1 = _make_tile(row=0, col=0, w=4, h=2)
        layout = _make_layout(tile1)
        tile2 = _make_tile(row=0, col=0, w=4, h=2)
        with pytest.raises(TileOverlapError):
            layout.add_tile(tile2)

    def test_remove_tile_cleans_filters(self) -> None:
        tile1 = _make_tile(row=0, col=0)
        tile2 = _make_tile(row=2, col=0)
        layout = _make_layout(tile1, tile2)
        layout.bind_filter(
            source_tile_id=tile1._identity._id,
            column="x",
            target_tile_ids={tile2._identity._id},
        )
        layout.remove_tile(tile2._identity._id)
        affected = layout.tiles_affected_by(tile1._identity._id, "x")
        assert affected == []

    def test_bind_filter_raises_on_self_filter(self) -> None:
        tile = _make_tile()
        layout = _make_layout(tile)
        with pytest.raises(SelfFilterError):
            layout.bind_filter(
                source_tile_id=tile._identity._id,
                column="x",
                target_tile_ids={tile._identity._id},
            )

    def test_bind_filter_raises_on_missing_source(self) -> None:
        layout = _make_layout()
        with pytest.raises(TileNotFoundError):
            layout.bind_filter(
                source_tile_id=EntityId(uuid4()),
                column="x",
                target_tile_ids=set(),
            )

    def test_tiles_affected_by(self) -> None:
        tile1 = _make_tile(row=0, col=0)
        tile2 = _make_tile(row=2, col=0)
        layout = _make_layout(tile1, tile2)
        layout.bind_filter(
            source_tile_id=tile1._identity._id,
            column="country",
            target_tile_ids={tile2._identity._id},
        )
        affected = layout.tiles_affected_by(tile1._identity._id, "country")
        assert len(affected) == 1
        assert affected[0]._identity._id == tile2._identity._id


class TestDashboardLayoutErrorMessages:
    def test_self_filter_message_exact(self) -> None:
        tile = _make_tile()
        layout = _make_layout(tile)
        with pytest.raises(SelfFilterError) as exc_info:
            layout.bind_filter(
                source_tile_id=tile._identity._id,
                column="x",
                target_tile_ids={tile._identity._id},
            )
        assert str(exc_info.value) == "A tile cannot filter itself"

    def test_missing_source_message_contains_id(self) -> None:
        layout = _make_layout()
        missing_id = EntityId(uuid4())
        with pytest.raises(TileNotFoundError) as exc_info:
            layout.bind_filter(
                source_tile_id=missing_id,
                column="x",
                target_tile_ids=set(),
            )
        assert str(missing_id.value) in str(exc_info.value)

    def test_overlap_message_contains_tile_id(self) -> None:
        tile1 = _make_tile(row=0, col=0, w=4, h=2)
        layout = _make_layout(tile1)
        tile2 = _make_tile(row=0, col=0, w=4, h=2)
        with pytest.raises(TileOverlapError) as exc_info:
            layout.add_tile(tile2)
        assert str(tile2._identity._id.value) in str(exc_info.value)


class TestOverlapBoundaryConditions:
    def test_tiles_adjacent_by_row_do_not_overlap(self) -> None:
        # tile1 occupies rows [0,2), tile2 starts at row=2 — they touch but do not overlap
        tile1 = _make_tile(row=0, col=0, w=4, h=2)
        layout = _make_layout(tile1)
        tile2 = _make_tile(row=2, col=0, w=4, h=2)
        layout.add_tile(tile2)  # must NOT raise TileOverlapError
        assert layout._tiles.contains(tile2._identity._id)

    def test_tiles_adjacent_by_col_do_not_overlap(self) -> None:
        # tile1 occupies cols [0,4), tile2 starts at col=4 — they touch but do not overlap
        tile1 = _make_tile(row=0, col=0, w=4, h=2)
        layout = _make_layout(tile1)
        tile2 = _make_tile(row=0, col=4, w=4, h=2)
        layout.add_tile(tile2)
        assert layout._tiles.contains(tile2._identity._id)

    def test_tiles_adjacent_on_right_edge_do_not_overlap(self) -> None:
        # tile1 at col=4 w=4 occupies [4,8), tile2 at col=8 — no overlap
        tile1 = _make_tile(row=0, col=4, w=4, h=2)
        layout = _make_layout(tile1)
        tile2 = _make_tile(row=0, col=8, w=4, h=2)
        layout.add_tile(tile2)
        assert layout._tiles.contains(tile2._identity._id)

    def test_overlapping_tiles_raises(self) -> None:
        tile1 = _make_tile(row=0, col=0, w=4, h=2)
        layout = _make_layout(tile1)
        tile2 = _make_tile(row=1, col=0, w=4, h=2)  # overlaps in both row and col
        with pytest.raises(TileOverlapError):
            layout.add_tile(tile2)


class TestFilterBindingAccumulation:
    def test_multiple_bindings_for_same_source_tile_accumulated(self) -> None:
        tile1 = _make_tile(row=0, col=0)
        tile2 = _make_tile(row=2, col=0)
        tile3 = _make_tile(row=4, col=0)
        layout = _make_layout(tile1, tile2, tile3)
        layout.bind_filter(tile1._identity._id, "col_a", {tile2._identity._id})
        layout.bind_filter(tile1._identity._id, "col_b", {tile3._identity._id})
        assert len(layout.tiles_affected_by(tile1._identity._id, "col_a")) == 1
        assert len(layout.tiles_affected_by(tile1._identity._id, "col_b")) == 1

    def test_remove_tile_removes_it_from_tiles_list(self) -> None:
        tile1 = _make_tile(row=0, col=0)
        tile2 = _make_tile(row=2, col=0)
        layout = _make_layout(tile1, tile2)
        layout.remove_tile(tile2._identity._id)
        assert not layout._tiles.contains(tile2._identity._id)

    def test_remove_source_tile_drops_its_filter_entry(self) -> None:
        tile1 = _make_tile(row=0, col=0)
        tile2 = _make_tile(row=2, col=0)
        layout = _make_layout(tile1, tile2)
        layout.bind_filter(tile2._identity._id, "x", {tile1._identity._id})
        layout.remove_tile(tile2._identity._id)
        affected = layout.tiles_affected_by(tile2._identity._id, "x")
        assert affected == []

    def test_remove_target_tile_keeps_unrelated_binding(self) -> None:
        tile1 = _make_tile(row=0, col=0)
        tile2 = _make_tile(row=2, col=0)
        tile3 = _make_tile(row=4, col=0)
        layout = _make_layout(tile1, tile2, tile3)
        layout.bind_filter(tile1._identity._id, "col_a", {tile2._identity._id})
        layout.bind_filter(tile1._identity._id, "col_b", {tile3._identity._id})
        layout.remove_tile(tile2._identity._id)
        # col_b binding to tile3 must survive
        assert len(layout.tiles_affected_by(tile1._identity._id, "col_b")) == 1
        # col_a binding to removed tile2 must be gone
        assert layout.tiles_affected_by(tile1._identity._id, "col_a") == []


class TestDashboard:
    def test_add_tile_from_question(self) -> None:
        dashboard_id = EntityId(uuid4())
        dashboard = Dashboard(
            identity=DashboardIdentity(
                entity_id=dashboard_id,
                audit=AuditRecord(
                    _created=CreatedAt(datetime.now(UTC)),
                    _updated=UpdatedAt(datetime.now(UTC)),
                ),
            ),
            layout=DashboardLayout(
                title=DashboardTitle("D"),
                tiles=Tiles(),
            ),
        )
        question = _make_question()
        position = TilePosition(_row=0, _col=0, _width=4, _height=2)
        tile = dashboard.add_tile_from_question(question, position)
        assert tile._source is question

    def _make_dashboard(self) -> Dashboard:
        return Dashboard(
            identity=DashboardIdentity(
                entity_id=EntityId(uuid4()),
                audit=AuditRecord(
                    _created=CreatedAt(datetime.now(UTC)),
                    _updated=UpdatedAt(datetime.now(UTC)),
                ),
            ),
            layout=DashboardLayout(title=DashboardTitle("D"), tiles=Tiles()),
        )

    def test_add_tile_from_question_id_is_not_none(self) -> None:
        # Kills add_tile_from_question__mutmut_6: _id=None
        d = self._make_dashboard()
        tile = d.add_tile_from_question(
            _make_question(),
            TilePosition(_row=0, _col=0, _width=4, _height=2),
        )
        assert tile._identity._id is not None

    def test_add_tile_from_question_id_is_valid_uuid(self) -> None:
        # Kills add_tile_from_question__mutmut_10: EntityId(None)
        d = self._make_dashboard()
        tile = d.add_tile_from_question(
            _make_question(),
            TilePosition(_row=0, _col=0, _width=4, _height=2),
        )
        assert isinstance(tile._identity._id.value, UUID)

    def test_add_tile_from_question_position_matches(self) -> None:
        # Kills add_tile_from_question__mutmut_7: _position=None
        d = self._make_dashboard()
        pos = TilePosition(_row=2, _col=4, _width=4, _height=2)
        tile = d.add_tile_from_question(_make_question(), pos)
        assert tile._identity._position == pos


class TestBindFilterTargetMissing:
    """Kill bind_filter__mutmut_7/8 (msg=None/raise TileNotFoundError(None) for missing target)."""

    def test_bind_filter_missing_target_raises_with_message(self) -> None:
        tile1 = _make_tile(row=0, col=0)
        layout = _make_layout(tile1)
        missing_id = EntityId(uuid4())
        with pytest.raises(TileNotFoundError) as exc:
            layout.bind_filter(
                source_tile_id=tile1._identity._id,
                column="x",
                target_tile_ids={missing_id},
            )
        assert str(exc.value)

    def test_bind_filter_missing_target_message_contains_id(self) -> None:
        # Kills mutmut_7: msg=None (str(None)="None", target_id.value not in "None")
        # Kills mutmut_8: raise TileNotFoundError(None)
        tile1 = _make_tile(row=0, col=0)
        layout = _make_layout(tile1)
        missing_id = EntityId(uuid4())
        with pytest.raises(TileNotFoundError) as exc:
            layout.bind_filter(
                source_tile_id=tile1._identity._id,
                column="x",
                target_tile_ids={missing_id},
            )
        assert str(missing_id.value) in str(exc.value)


class TestFilterBindingSourceTile:
    """Kill bind_filter__mutmut_16: _source_tile=None instead of source_tile_id."""

    def test_binding_source_tile_matches_source_id(self) -> None:
        tile1 = _make_tile(row=0, col=0)
        tile2 = _make_tile(row=2, col=0)
        layout = _make_layout(tile1, tile2)
        layout.bind_filter(tile1._identity._id, "col", {tile2._identity._id})
        binding = layout._filters[tile1._identity._id][0]
        assert binding._source_tile == tile1._identity._id


class TestOverlapBoundaryReverseDirection:
    """Kill _tile_overlaps mutmut_9/13 (>= instead of > for row/col boundary)."""

    def test_tile_above_existing_adjacent_does_not_overlap(self) -> None:
        # Kills mutmut_9: pos._row + pos._height >= epos._row triggers False positive
        # existing tile at row=2; new tile at row=0, h=2 → bottom=2 touches existing top=2
        existing = _make_tile(row=2, col=0, w=4, h=2)
        layout = _make_layout(existing)
        new_tile = _make_tile(row=0, col=0, w=4, h=2)
        layout.add_tile(new_tile)  # must NOT raise TileOverlapError
        assert layout._tiles.contains(new_tile._identity._id)

    def test_tile_left_of_existing_adjacent_does_not_overlap(self) -> None:
        # Kills mutmut_13: pos._col + pos._width >= epos._col triggers False positive
        # existing at col=4; new tile col=0, w=4 → right edge=4 touches existing left=4
        existing = _make_tile(row=0, col=4, w=4, h=2)
        layout = _make_layout(existing)
        new_tile = _make_tile(row=0, col=0, w=4, h=2)
        layout.add_tile(new_tile)  # must NOT raise TileOverlapError
        assert layout._tiles.contains(new_tile._identity._id)
