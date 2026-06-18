from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from src.dashboards.application.use_cases.compose_dashboard import (
    ComposeDashboardFromQuestionsUseCase,
    ComposeDashboardRequest,
)
from src.dashboards.domain.entities import Dashboard
from src.dashboards.domain.value_objects import DashboardTitle
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
from src.shared.domain.base import (
    AuditRecord,
    CreatedAt,
    EntityId,
    ResponseKind,
    UpdatedAt,
)


def _make_question_for_dataset(question_id: EntityId, dataset_id: EntityId) -> Question:
    return Question(
        identity=QuestionIdentity(
            entity_id=question_id,
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
                    _source=DatasetReference(_id=dataset_id, _alias=None),
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


def _make_question(question_id: EntityId) -> Question:
    dataset_id = EntityId(uuid4())
    return Question(
        identity=QuestionIdentity(
            entity_id=question_id,
            audit=AuditRecord(
                _created=CreatedAt(datetime.now(UTC)),
                _updated=UpdatedAt(datetime.now(UTC)),
            ),
        ),
        specification=QuestionSpecification(
            description=QuestionDescription(
                _title=QuestionTitle("Test Question"),
                _query=QueryDefinition(
                    _sql=SqlQuery("SELECT 1"),
                    _source=DatasetReference(_id=dataset_id, _alias=None),
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


class FakeDashboardRepository:
    def __init__(self) -> None:
        self._dashboards: list[Dashboard] = []

    def save(self, dashboard: Dashboard) -> None:
        self._dashboards.append(dashboard)

    def load(self, dashboard_id: EntityId) -> Dashboard | None:
        return None

    def delete(self, dashboard_id: EntityId) -> None:
        pass

    def find_all(self) -> list[Dashboard]:
        return list(self._dashboards)


class FakeQuestionRepository:
    def __init__(self, questions: dict[EntityId, Question] | None = None) -> None:
        self._questions = questions or {}

    def load(self, question_id: EntityId) -> Question | None:
        return self._questions.get(question_id)

    def save(self, question: Question) -> None:
        self._questions[question._identity._id] = question

    def delete(self, question_id: EntityId) -> None:
        self._questions.pop(question_id, None)

    def find_all(self):
        from src.questions.domain.entities import Questions

        return Questions(list(self._questions.values()))


def _make_use_case(
    q_ids: list[EntityId],
    questions: dict[EntityId, Question] | None = None,
) -> tuple[ComposeDashboardFromQuestionsUseCase, FakeDashboardRepository]:
    dash_repo = FakeDashboardRepository()
    q_repo = FakeQuestionRepository(questions or {qid: _make_question(qid) for qid in q_ids})
    return ComposeDashboardFromQuestionsUseCase(dashboards=dash_repo, questions=q_repo), dash_repo


class TestComposeDashboardFromQuestionsUseCase:
    def test_creates_dashboard_with_one_tile(self) -> None:
        q_id = EntityId(uuid4())
        question = _make_question(q_id)
        dash_repo = FakeDashboardRepository()
        q_repo = FakeQuestionRepository({q_id: question})
        use_case = ComposeDashboardFromQuestionsUseCase(
            dashboards=dash_repo,
            questions=q_repo,
        )
        request = ComposeDashboardRequest(
            _title=DashboardTitle("My Dashboard"),
            _question_ids=[q_id],
        )
        dashboard = use_case.execute(request)
        assert len(dash_repo.find_all()) == 1
        assert dashboard._layout._title.value == "My Dashboard"

    def test_raises_when_question_not_found(self) -> None:
        from src.dashboards.domain.entities import TileNotFoundError

        dash_repo = FakeDashboardRepository()
        q_repo = FakeQuestionRepository()
        use_case = ComposeDashboardFromQuestionsUseCase(
            dashboards=dash_repo,
            questions=q_repo,
        )
        request = ComposeDashboardRequest(
            _title=DashboardTitle("Bad Dashboard"),
            _question_ids=[EntityId(uuid4())],
        )
        with pytest.raises(TileNotFoundError):
            use_case.execute(request)

    def test_raises_error_message_contains_question_id(self) -> None:
        from src.dashboards.domain.entities import TileNotFoundError

        missing_id = EntityId(uuid4())
        use_case, _ = _make_use_case([], {})
        request = ComposeDashboardRequest(
            _title=DashboardTitle("X"),
            _question_ids=[missing_id],
        )
        with pytest.raises(TileNotFoundError) as exc_info:
            use_case.execute(request)
        assert str(missing_id.value) in str(exc_info.value)

    def test_tile_width_is_four(self) -> None:
        q_id = EntityId(uuid4())
        use_case, _ = _make_use_case([q_id])
        dashboard = use_case.execute(
            ComposeDashboardRequest(_title=DashboardTitle("D"), _question_ids=[q_id]),
        )
        pos = dashboard._layout._tiles.to_list()[0]._identity._position
        assert pos._width == 4

    def test_tile_height_is_two(self) -> None:
        q_id = EntityId(uuid4())
        use_case, _ = _make_use_case([q_id])
        dashboard = use_case.execute(
            ComposeDashboardRequest(_title=DashboardTitle("D"), _question_ids=[q_id]),
        )
        pos = dashboard._layout._tiles.to_list()[0]._identity._position
        assert pos._height == 2

    def test_first_tile_at_row_zero_col_zero(self) -> None:
        q_id = EntityId(uuid4())
        use_case, _ = _make_use_case([q_id])
        dashboard = use_case.execute(
            ComposeDashboardRequest(_title=DashboardTitle("D"), _question_ids=[q_id]),
        )
        pos = dashboard._layout._tiles.to_list()[0]._identity._position
        assert pos._row == 0
        assert pos._col == 0

    def test_second_tile_in_same_row_col_four(self) -> None:
        q_ids = [EntityId(uuid4()), EntityId(uuid4())]
        use_case, _ = _make_use_case(q_ids)
        dashboard = use_case.execute(
            ComposeDashboardRequest(_title=DashboardTitle("D"), _question_ids=q_ids),
        )
        tiles = dashboard._layout._tiles.to_list()
        assert tiles[0]._identity._position._row == 0
        assert tiles[1]._identity._position._row == 0
        assert tiles[1]._identity._position._col == 4

    def test_fourth_tile_starts_second_row_with_three_cols(self) -> None:
        # cols=3: divmod(3,3)=(1,0) → row=1*2=2; with cols=4: divmod(3,4)=(0,3) → row=0
        q_ids = [EntityId(uuid4()) for _ in range(4)]
        use_case, _ = _make_use_case(q_ids)
        dashboard = use_case.execute(
            ComposeDashboardRequest(_title=DashboardTitle("D"), _question_ids=q_ids),
        )
        fourth = dashboard._layout._tiles.to_list()[3]._identity._position
        assert fourth._row == 2
        assert fourth._col == 0

    def test_third_tile_col_is_eight(self) -> None:
        # divmod(2,3)=(0,2) → col=2*4=8
        q_ids = [EntityId(uuid4()) for _ in range(3)]
        use_case, _ = _make_use_case(q_ids)
        dashboard = use_case.execute(
            ComposeDashboardRequest(_title=DashboardTitle("D"), _question_ids=q_ids),
        )
        third = dashboard._layout._tiles.to_list()[2]._identity._position
        assert third._row == 0
        assert third._col == 8

    def test_tile_source_is_loaded_question(self) -> None:
        q_id = EntityId(uuid4())
        question = _make_question(q_id)
        q_repo = FakeQuestionRepository({q_id: question})
        dash_repo = FakeDashboardRepository()
        use_case = ComposeDashboardFromQuestionsUseCase(dashboards=dash_repo, questions=q_repo)
        dashboard = use_case.execute(
            ComposeDashboardRequest(_title=DashboardTitle("D"), _question_ids=[q_id]),
        )
        tile = dashboard._layout._tiles.to_list()[0]
        assert tile._source is question

    def test_tile_identity_id_is_not_none(self) -> None:
        q_id = EntityId(uuid4())
        use_case, _ = _make_use_case([q_id])
        dashboard = use_case.execute(
            ComposeDashboardRequest(_title=DashboardTitle("D"), _question_ids=[q_id]),
        )
        tile = dashboard._layout._tiles.to_list()[0]
        assert tile._identity._id is not None

    def test_tile_identity_id_value_is_uuid(self) -> None:
        q_id = EntityId(uuid4())
        use_case, _ = _make_use_case([q_id])
        dashboard = use_case.execute(
            ComposeDashboardRequest(_title=DashboardTitle("D"), _question_ids=[q_id]),
        )
        tile = dashboard._layout._tiles.to_list()[0]
        assert isinstance(tile._identity._id.value, UUID)

    def test_dashboard_identity_is_not_none(self) -> None:
        q_id = EntityId(uuid4())
        use_case, _ = _make_use_case([q_id])
        dashboard = use_case.execute(
            ComposeDashboardRequest(_title=DashboardTitle("D"), _question_ids=[q_id]),
        )
        assert dashboard._identity is not None

    def test_dashboard_entity_id_value_is_uuid(self) -> None:
        q_id = EntityId(uuid4())
        use_case, _ = _make_use_case([q_id])
        dashboard = use_case.execute(
            ComposeDashboardRequest(_title=DashboardTitle("D"), _question_ids=[q_id]),
        )
        assert isinstance(dashboard._identity._id.value, UUID)

    def test_dashboard_audit_is_not_none(self) -> None:
        q_id = EntityId(uuid4())
        use_case, _ = _make_use_case([q_id])
        dashboard = use_case.execute(
            ComposeDashboardRequest(_title=DashboardTitle("D"), _question_ids=[q_id]),
        )
        assert dashboard._identity._audit is not None

    def test_dashboard_audit_created_is_utc_aware(self) -> None:
        q_id = EntityId(uuid4())
        use_case, _ = _make_use_case([q_id])
        dashboard = use_case.execute(
            ComposeDashboardRequest(_title=DashboardTitle("D"), _question_ids=[q_id]),
        )
        created = dashboard._identity._audit._created.value
        assert isinstance(created, datetime) and created.tzinfo is not None

    def test_dashboard_audit_updated_is_utc_aware(self) -> None:
        q_id = EntityId(uuid4())
        use_case, _ = _make_use_case([q_id])
        dashboard = use_case.execute(
            ComposeDashboardRequest(_title=DashboardTitle("D"), _question_ids=[q_id]),
        )
        updated = dashboard._identity._audit._updated.value
        assert isinstance(updated, datetime) and updated.tzinfo is not None

    def test_saved_dashboard_is_returned_dashboard(self) -> None:
        q_id = EntityId(uuid4())
        use_case, dash_repo = _make_use_case([q_id])
        dashboard = use_case.execute(
            ComposeDashboardRequest(_title=DashboardTitle("D"), _question_ids=[q_id]),
        )
        assert dash_repo._dashboards[0] is dashboard

    def test_auto_bind_compatible_tiles_creates_filter(self) -> None:
        dataset_id = EntityId(uuid4())
        q1_id, q2_id = EntityId(uuid4()), EntityId(uuid4())
        q1 = _make_question_for_dataset(q1_id, dataset_id)
        q2 = _make_question_for_dataset(q2_id, dataset_id)
        dash_repo = FakeDashboardRepository()
        q_repo = FakeQuestionRepository({q1_id: q1, q2_id: q2})
        use_case = ComposeDashboardFromQuestionsUseCase(dashboards=dash_repo, questions=q_repo)
        dashboard = use_case.execute(
            ComposeDashboardRequest(
                _title=DashboardTitle("D"),
                _question_ids=[q1_id, q2_id],
                _auto_bind_filters=True,
            ),
        )
        tiles = dashboard._layout._tiles.to_list()
        affected = dashboard._layout.tiles_affected_by(tiles[0]._identity._id, "*")
        assert len(affected) == 1

    def test_auto_bind_incompatible_tiles_creates_no_filter(self) -> None:
        # Different dataset_ids → not compatible → no bindings
        q1_id = EntityId(uuid4())
        q2_id = EntityId(uuid4())
        q1 = _make_question_for_dataset(q1_id, EntityId(uuid4()))
        q2 = _make_question_for_dataset(q2_id, EntityId(uuid4()))
        dash_repo = FakeDashboardRepository()
        q_repo = FakeQuestionRepository({q1_id: q1, q2_id: q2})
        use_case = ComposeDashboardFromQuestionsUseCase(dashboards=dash_repo, questions=q_repo)
        dashboard = use_case.execute(
            ComposeDashboardRequest(
                _title=DashboardTitle("D"),
                _question_ids=[q1_id, q2_id],
                _auto_bind_filters=True,
            ),
        )
        tiles = dashboard._layout._tiles.to_list()
        affected = dashboard._layout.tiles_affected_by(tiles[0]._identity._id, "*")
        assert len(affected) == 0
