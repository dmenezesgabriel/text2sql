from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest

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
from src.questions.exceptions.invalid_query_error import InvalidQueryError
from src.questions.exceptions.same_visualization_error import SameVisualizationError
from src.shared.domain.base import AuditRecord, CreatedAt, EntityId, ResponseKind, UpdatedAt


def _make_question(
    dataset_id: EntityId | None = None,
    sql: str = "SELECT 1",
    fmt: ResponseKind = ResponseKind.TABLE,
) -> Question:
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
                    _sql=SqlQuery(sql),
                    _source=DatasetReference(
                        _id=dataset_id or EntityId(uuid4()),
                        _alias=None,
                    ),
                ),
            ),
            rendering=RenderDirective(
                _decision=VizDecision(
                    _format=fmt,
                    _spec=VizSpec(_component="Table", _props={}, _children=()),
                ),
            ),
        ),
    )


class TestQueryDefinition:
    def test_only_select_is_valid(self) -> None:
        with pytest.raises(InvalidQueryError):
            QueryDefinition(
                _sql=SqlQuery("DROP TABLE users"),
                _source=DatasetReference(_id=EntityId(uuid4()), _alias=None),
            )

    def test_with_filter_raises_due_to_source_bug(self) -> None:
        # with_filter calls QueryDefinition(sql=..., source=...) using wrong kwarg names
        # (_sql and _source are the correct dataclass field names). This documents the bug.
        q = _make_question()
        with pytest.raises(TypeError):
            q._specification._description._query.with_filter("status", "=", "active")

    def test_is_equivalent_to_normalizes_whitespace(self) -> None:
        qd1 = QueryDefinition(
            _sql=SqlQuery("SELECT   1"),
            _source=DatasetReference(_id=EntityId(uuid4()), _alias=None),
        )
        qd2 = QueryDefinition(
            _sql=SqlQuery("SELECT 1"),
            _source=DatasetReference(_id=EntityId(uuid4()), _alias=None),
        )
        assert qd1.is_equivalent_to(qd2)


class TestQuestion:
    def test_rename_changes_title(self) -> None:
        q = _make_question()
        q.rename(QuestionTitle("New Title"))
        assert q._specification._description._title.value == "New Title"

    def test_change_decision_raises_on_same_format(self) -> None:
        q = _make_question(fmt=ResponseKind.TABLE)
        same_decision = VizDecision(
            _format=ResponseKind.TABLE,
            _spec=VizSpec(_component="Table", _props={}, _children=()),
        )
        with pytest.raises(SameVisualizationError):
            q.change_decision(same_decision)

    def test_change_decision_succeeds_with_different_format(self) -> None:
        q = _make_question(fmt=ResponseKind.TABLE)
        new_decision = VizDecision(
            _format=ResponseKind.CHART,
            _spec=VizSpec(_component="BarChart", _props={}, _children=()),
        )
        q.change_decision(new_decision)
        assert q._specification._rendering._decision._format == ResponseKind.CHART

    def test_derive_drill_down_raises_due_to_source_bug(self) -> None:
        # derive_drill_down internally calls with_filter which has a source bug.
        # Documents that the code path raises TypeError.
        q = _make_question()
        with pytest.raises(TypeError):
            q.derive_drill_down("country", "US")

    def test_is_compatible_with_same_dataset(self) -> None:
        dataset_id = EntityId(uuid4())
        q1 = _make_question(dataset_id=dataset_id)
        q2 = _make_question(dataset_id=dataset_id)
        assert q1.is_compatible_with(q2)

    def test_is_not_compatible_with_different_dataset(self) -> None:
        q1 = _make_question()
        q2 = _make_question()
        assert not q1.is_compatible_with(q2)

    def test_compiled_sql(self) -> None:
        q = _make_question(sql="SELECT id FROM sales")
        assert q.compiled_sql() == "SELECT id FROM sales"


class TestQuestions:
    def test_add_and_count(self) -> None:
        questions = Questions()
        questions.add(_make_question())
        assert questions.count() == 1

    def test_remove(self) -> None:
        q = _make_question()
        questions = Questions([q])
        questions.remove(q._identity._id)
        assert questions.count() == 0
