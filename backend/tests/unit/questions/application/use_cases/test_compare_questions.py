from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.questions.application.use_cases.compare_questions import (
    CompareQuestionsUseCase,
    CompareRequest,
)
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
from src.questions.exceptions.incompatible_questions_error import IncompatibleQuestionsError
from src.questions.exceptions.question_not_found_error import QuestionNotFoundError
from src.shared.domain.base import (
    AuditRecord,
    CreatedAt,
    EntityId,
    QueryResult,
    ResponseKind,
    UpdatedAt,
)


def _make_question(dataset_id: EntityId) -> Question:
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


class FakeQuestionRepository:
    def __init__(self, questions: dict[EntityId, Question] | None = None) -> None:
        self._questions: dict[EntityId, Question] = questions or {}

    def load(self, question_id: EntityId) -> Question | None:
        return self._questions.get(question_id)

    def save(self, question: Question) -> None:
        self._questions[question._identity._id] = question

    def find_all(self) -> Questions:
        return Questions(list(self._questions.values()))

    def delete(self, question_id: EntityId) -> None:
        self._questions.pop(question_id, None)


class FakeQueryExecutor:
    async def execute(self, sql: str, dataset_id: EntityId) -> QueryResult:
        return QueryResult(_columns=("id",), _rows=({"id": 1},))


class TestCompareQuestionsUseCase:
    def setup_method(self) -> None:
        self.executor = FakeQueryExecutor()

    async def test_raises_when_question_not_found(self) -> None:
        repo = FakeQuestionRepository()
        use_case = CompareQuestionsUseCase(questions=repo, executor=self.executor)
        request = CompareRequest(_first_id=EntityId(uuid4()), _second_id=EntityId(uuid4()))
        with pytest.raises(QuestionNotFoundError):
            await use_case.execute(request)

    async def test_raises_when_questions_incompatible(self) -> None:
        q1 = _make_question(EntityId(uuid4()))
        q2 = _make_question(EntityId(uuid4()))  # different dataset
        repo = FakeQuestionRepository({q1._identity._id: q1, q2._identity._id: q2})
        use_case = CompareQuestionsUseCase(questions=repo, executor=self.executor)
        request = CompareRequest(_first_id=q1._identity._id, _second_id=q2._identity._id)
        with pytest.raises(IncompatibleQuestionsError):
            await use_case.execute(request)

    async def test_returns_report_for_compatible_questions(self) -> None:
        dataset_id = EntityId(uuid4())
        q1 = _make_question(dataset_id)
        q2 = _make_question(dataset_id)
        repo = FakeQuestionRepository({q1._identity._id: q1, q2._identity._id: q2})
        use_case = CompareQuestionsUseCase(questions=repo, executor=self.executor)
        request = CompareRequest(_first_id=q1._identity._id, _second_id=q2._identity._id)
        report = await use_case.execute(request)
        assert report._first_title == "Q"
        assert report._second_title == "Q"
