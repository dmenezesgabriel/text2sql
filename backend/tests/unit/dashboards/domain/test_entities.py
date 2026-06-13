from __future__ import annotations

from datetime import datetime
from uuid import uuid4

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
                _created=CreatedAt(datetime.utcnow()),
                _updated=UpdatedAt(datetime.utcnow()),
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


class TestDashboard:
    def test_add_tile_from_question(self) -> None:
        dashboard_id = EntityId(uuid4())
        dashboard = Dashboard(
            identity=DashboardIdentity(
                entity_id=dashboard_id,
                audit=AuditRecord(
                    _created=CreatedAt(datetime.utcnow()),
                    _updated=UpdatedAt(datetime.utcnow()),
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
