from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

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
