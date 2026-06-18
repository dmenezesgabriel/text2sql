from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest

from src.dashboards.domain.entities import (
    Dashboard,
    DashboardIdentity,
    DashboardLayout,
    DashboardTile,
    DashboardTitle,
    TileIdentity,
    TilePosition,
    Tiles,
)
from src.dashboards.infrastructure.dynamo_repository import DynamoDashboardRepository
from src.questions.domain.entities import (
    DatasetReference,
    QueryDefinition,
    Question,
    QuestionDescription,
    QuestionIdentity,
    Questions,
    QuestionSpecification,
    RenderDirective,
)
from src.questions.domain.value_objects import QuestionTitle, SqlQuery, VizDecision, VizSpec
from src.shared.domain.base import AuditRecord, CreatedAt, EntityId, ResponseKind, UpdatedAt
from src.shared.infrastructure.dynamo_models import DashboardModel


class FakeQuestionRepository:
    """In-memory question store for dashboard repository tests."""

    def __init__(self, questions: dict[str, Question] | None = None) -> None:
        self._store: dict[str, Question] = questions or {}

    def load(self, question_id: EntityId) -> Question | None:
        return self._store.get(str(question_id.value))

    def save(self, question: Question) -> None:
        self._store[str(question._identity._id.value)] = question

    def delete(self, question_id: EntityId) -> None:
        self._store.pop(str(question_id.value), None)

    def find_all(self) -> Questions:
        return Questions(list(self._store.values()))


def _make_question(question_id_str: str | None = None) -> Question:
    qid = EntityId(UUID(question_id_str) if question_id_str else uuid4())
    now = datetime.now(UTC)
    return Question(
        identity=QuestionIdentity(
            entity_id=qid,
            audit=AuditRecord(_created=CreatedAt(now), _updated=UpdatedAt(now)),
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
                    _format=ResponseKind.CHART,
                    _spec=VizSpec(_component="BarChart", _props={}, _children=()),
                ),
            ),
        ),
    )


def _make_dashboard_model(*, tiles: str = "[]", filters: str = "[]") -> DashboardModel:
    return DashboardModel(
        id=str(uuid4()),
        title="Test Dashboard",
        tiles=tiles,
        filters=filters,
        created_at="2026-01-01T00:00:00+00:00",
        updated_at="2026-01-01T00:00:00+00:00",
    )


def _make_dashboard_with_two_tiles() -> tuple[Dashboard, EntityId, EntityId]:
    """Returns a dashboard with two tiles and their tile IDs."""
    q1 = _make_question()
    q2 = _make_question()
    tid1 = EntityId(uuid4())
    tid2 = EntityId(uuid4())
    now = datetime.now(UTC)
    tile1 = DashboardTile(
        identity=TileIdentity(
            _id=tid1,
            _position=TilePosition(_row=0, _col=0, _width=4, _height=2),
        ),
        source=q1,
    )
    tile2 = DashboardTile(
        identity=TileIdentity(
            _id=tid2,
            _position=TilePosition(_row=0, _col=4, _width=4, _height=2),
        ),
        source=q2,
    )
    layout = DashboardLayout(title=DashboardTitle("Dash"), tiles=Tiles([tile1, tile2]))
    dashboard = Dashboard(
        identity=DashboardIdentity(
            entity_id=EntityId(uuid4()),
            audit=AuditRecord(_created=CreatedAt(now), _updated=UpdatedAt(now)),
        ),
        layout=layout,
    )
    return dashboard, tid1, tid2


class TestDynamoDashboardRepository:
    def test_module_imports(self) -> None:
        from src.dashboards.infrastructure.dynamo_repository import DynamoDashboardRepository

        assert DynamoDashboardRepository is not None

    def test_class_is_instantiable(self) -> None:
        repo = DynamoDashboardRepository(questions=FakeQuestionRepository())
        assert repo is not None

    def test_empty_dashboard_has_no_tiles(self) -> None:
        model = _make_dashboard_model()
        dashboard = DynamoDashboardRepository(questions=FakeQuestionRepository())._doc_to_dashboard(
            model,
        )
        assert dashboard._layout._tiles.to_list() == []

    def test_doc_to_dashboard_restores_tile_position(self) -> None:
        qid = str(uuid4())
        question = _make_question(qid)
        model = _make_dashboard_model(
            tiles=json.dumps(
                [
                    {
                        "tile_id": str(uuid4()),
                        "question_id": qid,
                        "row": 1,
                        "col": 2,
                        "width": 6,
                        "height": 3,
                    },
                ],
            ),
        )
        dashboard = DynamoDashboardRepository(
            questions=FakeQuestionRepository({qid: question}),
        )._doc_to_dashboard(model)

        pos = dashboard._layout._tiles.to_list()[0]._identity._position
        assert (pos._row, pos._col, pos._width, pos._height) == (1, 2, 6, 3)

    def test_doc_to_dashboard_links_tile_to_question(self) -> None:
        qid = str(uuid4())
        question = _make_question(qid)
        model = _make_dashboard_model(
            tiles=json.dumps(
                [
                    {
                        "tile_id": str(uuid4()),
                        "question_id": qid,
                        "row": 0,
                        "col": 0,
                        "width": 4,
                        "height": 2,
                    },
                ],
            ),
        )
        dashboard = DynamoDashboardRepository(
            questions=FakeQuestionRepository({qid: question}),
        )._doc_to_dashboard(model)

        assert dashboard._layout._tiles.to_list()[0]._source is question

    def test_doc_to_dashboard_restores_filter_bindings(self) -> None:
        qid1, qid2 = str(uuid4()), str(uuid4())
        tid1, tid2 = str(uuid4()), str(uuid4())
        model = _make_dashboard_model(
            tiles=json.dumps(
                [
                    {
                        "tile_id": tid1,
                        "question_id": qid1,
                        "row": 0,
                        "col": 0,
                        "width": 4,
                        "height": 2,
                    },
                    {
                        "tile_id": tid2,
                        "question_id": qid2,
                        "row": 0,
                        "col": 4,
                        "width": 4,
                        "height": 2,
                    },
                ],
            ),
            filters=json.dumps(
                [
                    {"source_tile_id": tid1, "column": "region", "target_tile_ids": [tid2]},
                ],
            ),
        )
        fake_questions = FakeQuestionRepository(
            {
                qid1: _make_question(qid1),
                qid2: _make_question(qid2),
            },
        )
        dashboard = DynamoDashboardRepository(questions=fake_questions)._doc_to_dashboard(model)

        affected = dashboard._layout.tiles_affected_by(EntityId(UUID(tid1)), "region")
        assert len(affected) == 1
        assert str(affected[0]._identity._id.value) == tid2

    def test_save_serializes_tile_position(self) -> None:
        q = _make_question()
        tid = EntityId(uuid4())
        now = datetime.now(UTC)
        tile = DashboardTile(
            identity=TileIdentity(
                _id=tid,
                _position=TilePosition(_row=2, _col=3, _width=5, _height=4),
            ),
            source=q,
        )
        layout = DashboardLayout(title=DashboardTitle("D"), tiles=Tiles([tile]))
        dashboard = Dashboard(
            identity=DashboardIdentity(
                entity_id=EntityId(uuid4()),
                audit=AuditRecord(_created=CreatedAt(now), _updated=UpdatedAt(now)),
            ),
            layout=layout,
        )

        with patch.object(DashboardModel, "save", autospec=True) as mock_save:
            DynamoDashboardRepository(questions=FakeQuestionRepository()).save(dashboard)

        tiles_data = json.loads(mock_save.call_args[0][0].tiles)
        assert len(tiles_data) == 1
        assert (
            tiles_data[0]["row"],
            tiles_data[0]["col"],
            tiles_data[0]["width"],
            tiles_data[0]["height"],
        ) == (2, 3, 5, 4)

    def test_save_serializes_question_id_in_tile(self) -> None:
        q = _make_question()
        now = datetime.now(UTC)
        tile = DashboardTile(
            identity=TileIdentity(
                _id=EntityId(uuid4()),
                _position=TilePosition(_row=0, _col=0, _width=4, _height=2),
            ),
            source=q,
        )
        layout = DashboardLayout(title=DashboardTitle("D"), tiles=Tiles([tile]))
        dashboard = Dashboard(
            identity=DashboardIdentity(
                entity_id=EntityId(uuid4()),
                audit=AuditRecord(_created=CreatedAt(now), _updated=UpdatedAt(now)),
            ),
            layout=layout,
        )

        with patch.object(DashboardModel, "save", autospec=True) as mock_save:
            DynamoDashboardRepository(questions=FakeQuestionRepository()).save(dashboard)

        tiles_data = json.loads(mock_save.call_args[0][0].tiles)
        assert tiles_data[0]["question_id"] == str(q._identity._id.value)

    def test_save_serializes_filter_bindings(self) -> None:
        dashboard, tid1, tid2 = _make_dashboard_with_two_tiles()
        dashboard._layout.bind_filter(source_tile_id=tid1, column="region", target_tile_ids={tid2})

        with patch.object(DashboardModel, "save", autospec=True) as mock_save:
            DynamoDashboardRepository(questions=FakeQuestionRepository()).save(dashboard)

        filters_data = json.loads(mock_save.call_args[0][0].filters)
        assert len(filters_data) == 1
        assert filters_data[0]["source_tile_id"] == str(tid1.value)
        assert filters_data[0]["column"] == "region"
        assert str(tid2.value) in filters_data[0]["target_tile_ids"]

    def test_save_empty_dashboard_writes_empty_tiles_and_filters(self) -> None:
        now = datetime.now(UTC)
        layout = DashboardLayout(title=DashboardTitle("Empty"), tiles=Tiles())
        dashboard = Dashboard(
            identity=DashboardIdentity(
                entity_id=EntityId(uuid4()),
                audit=AuditRecord(_created=CreatedAt(now), _updated=UpdatedAt(now)),
            ),
            layout=layout,
        )

        with patch.object(DashboardModel, "save", autospec=True) as mock_save:
            DynamoDashboardRepository(questions=FakeQuestionRepository()).save(dashboard)

        saved = mock_save.call_args[0][0]
        assert json.loads(saved.tiles) == []
        assert json.loads(saved.filters) == []

    def test_doc_to_dashboard_restores_dashboard_id(self) -> None:
        model = _make_dashboard_model()
        dashboard = DynamoDashboardRepository(questions=FakeQuestionRepository())._doc_to_dashboard(
            model,
        )
        assert str(dashboard._identity._id.value) == model.id

    def test_doc_to_dashboard_restores_audit_timestamps(self) -> None:
        created_ts = "2025-03-01T10:00:00+00:00"
        updated_ts = "2025-03-02T12:00:00+00:00"
        model = DashboardModel(
            id=str(uuid4()),
            title="T",
            tiles="[]",
            filters="[]",
            created_at=created_ts,
            updated_at=updated_ts,
        )
        dashboard = DynamoDashboardRepository(questions=FakeQuestionRepository())._doc_to_dashboard(
            model,
        )
        assert dashboard._identity._audit._created.value.isoformat() == created_ts
        assert dashboard._identity._audit._updated.value.isoformat() == updated_ts

    def test_doc_to_dashboard_with_none_tiles_treated_as_empty(self) -> None:
        model = DashboardModel(
            id=str(uuid4()),
            title="T",
            tiles=None,
            filters=None,
            created_at="2026-01-01T00:00:00+00:00",
            updated_at="2026-01-01T00:00:00+00:00",
        )
        dashboard = DynamoDashboardRepository(questions=FakeQuestionRepository())._doc_to_dashboard(
            model,
        )
        assert dashboard._layout._tiles.to_list() == []

    def test_deserialize_tile_error_message_contains_question_id(self) -> None:
        from src.dashboards.exceptions.tile_not_found_error import TileNotFoundError

        missing_qid = str(uuid4())
        model = _make_dashboard_model(
            tiles=json.dumps(
                [
                    {
                        "tile_id": str(uuid4()),
                        "question_id": missing_qid,
                        "row": 0,
                        "col": 0,
                        "width": 4,
                        "height": 2,
                    },
                ],
            ),
        )
        with pytest.raises(TileNotFoundError) as exc_info:
            DynamoDashboardRepository(questions=FakeQuestionRepository())._doc_to_dashboard(model)
        assert missing_qid in str(exc_info.value)
