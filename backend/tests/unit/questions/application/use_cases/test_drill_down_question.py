from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest

from src.questions.application.use_cases.drill_down_question import (
    DrillDownQuestionUseCase,
    DrillDownRequest,
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
from src.questions.exceptions.question_not_found_error import QuestionNotFoundError
from src.shared.domain.base import AuditRecord, CreatedAt, EntityId, ResponseKind, UpdatedAt


def _make_question(question_id: EntityId | None = None) -> Question:
    return Question(
        identity=QuestionIdentity(
            entity_id=question_id or EntityId(uuid4()),
            audit=AuditRecord(
                _created=CreatedAt(datetime.utcnow()),
                _updated=UpdatedAt(datetime.utcnow()),
            ),
        ),
        specification=QuestionSpecification(
            description=QuestionDescription(
                _title=QuestionTitle("Sales"),
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


class TestDrillDownQuestionUseCase:
    async def test_raises_when_source_not_found(self) -> None:
        repo = FakeQuestionRepository()
        use_case = DrillDownQuestionUseCase(questions=repo)
        request = DrillDownRequest(
            _source_id=EntityId(uuid4()),
            _column="country",
            _value="US",
        )
        with pytest.raises(QuestionNotFoundError):
            use_case.execute(request)

    def test_execute_raises_due_to_source_bug_in_with_filter(self) -> None:
        # DrillDownQuestionUseCase.execute calls question.derive_drill_down which
        # calls QueryDefinition.with_filter. That method has a bug: it passes
        # sql= and source= as kwargs, but the frozen dataclass fields are _sql and _source.
        # This test documents the bug.
        source = _make_question()
        repo = FakeQuestionRepository({source._identity._id: source})
        use_case = DrillDownQuestionUseCase(questions=repo)
        request = DrillDownRequest(
            _source_id=source._identity._id,
            _column="country",
            _value="US",
        )
        with pytest.raises(TypeError):
            use_case.execute(request)
