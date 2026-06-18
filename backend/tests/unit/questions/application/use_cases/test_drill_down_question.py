from __future__ import annotations

from datetime import UTC, datetime
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
                _created=CreatedAt(datetime.now(UTC)),
                _updated=UpdatedAt(datetime.now(UTC)),
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

    def test_execute_creates_drill_down_question(self) -> None:
        source = _make_question()
        repo = FakeQuestionRepository({source._identity._id: source})
        use_case = DrillDownQuestionUseCase(questions=repo)
        request = DrillDownRequest(
            _source_id=source._identity._id,
            _column="country",
            _value="US",
        )
        drilled = use_case.execute(request)
        assert drilled is not None
        assert "WHERE country = 'US'" in drilled.compiled_sql()

    def test_not_found_error_message_exact(self) -> None:
        missing_id = EntityId(uuid4())
        repo = FakeQuestionRepository()
        use_case = DrillDownQuestionUseCase(questions=repo)
        request = DrillDownRequest(_source_id=missing_id, _column="x", _value="1")
        with pytest.raises(QuestionNotFoundError) as exc_info:
            use_case.execute(request)
        assert str(missing_id.value) in str(exc_info.value)

    def test_change_viz_requires_both_change_viz_true_and_new_viz_not_none(self) -> None:
        # Kills `or` mutation: `if request._change_viz or request._new_viz is not None`
        # With `or`, change_viz=False but new_viz set → change_decision called → SameVizError (or error)
        # With `and`, change_viz=False → skipped (correct)
        source = _make_question()
        repo = FakeQuestionRepository({source._identity._id: source})
        use_case = DrillDownQuestionUseCase(questions=repo)
        # change_viz=False with new_viz set: should NOT call change_decision
        new_viz = VizDecision(
            _format=ResponseKind.CHART,
            _spec=VizSpec(_component="BarChart", _props={}, _children=()),
        )
        request = DrillDownRequest(
            _source_id=source._identity._id,
            _column="country",
            _value="US",
            _change_viz=False,
            _new_viz=new_viz,
        )
        drilled = use_case.execute(request)
        # Should keep original TABLE format (change_decision not called)
        assert drilled._specification._rendering._decision._format is ResponseKind.TABLE

    def test_change_viz_true_with_none_viz_does_not_change_decision(self) -> None:
        # Kills `_new_viz is None` mutation: `if request._change_viz and request._new_viz is None`
        source = _make_question()
        repo = FakeQuestionRepository({source._identity._id: source})
        use_case = DrillDownQuestionUseCase(questions=repo)
        request = DrillDownRequest(
            _source_id=source._identity._id,
            _column="country",
            _value="US",
            _change_viz=True,
            _new_viz=None,
        )
        drilled = use_case.execute(request)
        # new_viz is None: condition `_change_viz and _new_viz is not None` = True and False = False
        # so change_decision is NOT called, original TABLE stays
        assert drilled._specification._rendering._decision._format is ResponseKind.TABLE

    def test_change_viz_true_with_valid_viz_changes_decision(self) -> None:
        source = _make_question()
        repo = FakeQuestionRepository({source._identity._id: source})
        use_case = DrillDownQuestionUseCase(questions=repo)
        new_viz = VizDecision(
            _format=ResponseKind.CHART,
            _spec=VizSpec(_component="BarChart", _props={}, _children=()),
        )
        request = DrillDownRequest(
            _source_id=source._identity._id,
            _column="country",
            _value="US",
            _change_viz=True,
            _new_viz=new_viz,
        )
        drilled = use_case.execute(request)
        assert drilled._specification._rendering._decision._format is ResponseKind.CHART

    def test_change_decision_arg_is_new_viz(self) -> None:
        # Kills `derived.change_decision(None)` mutation
        source = _make_question()
        repo = FakeQuestionRepository({source._identity._id: source})
        use_case = DrillDownQuestionUseCase(questions=repo)
        new_viz = VizDecision(
            _format=ResponseKind.CHART,
            _spec=VizSpec(_component="LineChart", _props={}, _children=()),
        )
        request = DrillDownRequest(
            _source_id=source._identity._id,
            _column="x",
            _value="1",
            _change_viz=True,
            _new_viz=new_viz,
        )
        drilled = use_case.execute(request)
        assert drilled._specification._rendering._decision._spec._component == "LineChart"
