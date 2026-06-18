from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

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
                _created=CreatedAt(datetime.now(UTC)),
                _updated=UpdatedAt(datetime.now(UTC)),
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

    def test_with_filter_appends_where_clause(self) -> None:
        q = _make_question()
        filtered = q._specification._description._query.with_filter("status", "=", "active")
        assert "WHERE status = 'active'" in filtered._sql.value

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

    def test_derive_drill_down_returns_new_question_with_filter(self) -> None:
        q = _make_question()
        drilled = q.derive_drill_down("country", "US")
        assert "WHERE country = 'US'" in drilled.compiled_sql()

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

    def test_add_appends_the_actual_question_not_none(self) -> None:
        q = _make_question()
        questions = Questions()
        questions.add(q)
        assert questions.to_list()[0] is q

    def test_to_list_contains_all_items(self) -> None:
        q1 = _make_question()
        q2 = _make_question()
        questions = Questions([q1, q2])
        items = questions.to_list()
        assert q1 in items
        assert q2 in items


class TestQuestionChangeDicision:
    def test_change_decision_error_message_exact(self) -> None:
        q = _make_question(fmt=ResponseKind.TABLE)
        same_decision = VizDecision(
            _format=ResponseKind.TABLE,
            _spec=VizSpec(_component="Table", _props={}, _children=()),
        )
        with pytest.raises(SameVisualizationError) as exc_info:
            q.change_decision(same_decision)
        assert str(exc_info.value) == "New viz must differ from current"

    def test_change_decision_preserves_description(self) -> None:
        q = _make_question(fmt=ResponseKind.TABLE)
        new_decision = VizDecision(
            _format=ResponseKind.CHART,
            _spec=VizSpec(_component="BarChart", _props={}, _children=()),
        )
        q.change_decision(new_decision)
        assert q._specification._description is not None
        assert q._specification._rendering is not None
        assert q._specification._rendering._decision._format is ResponseKind.CHART


class TestDerivedrillDown:
    def test_drill_down_title_contains_column_and_value(self) -> None:
        q = _make_question(sql="SELECT 1 FROM t")
        drilled = q.derive_drill_down("region", "WEST")
        assert "region=WEST" in drilled._specification._description._title.value

    def test_drill_down_title_contains_em_dash(self) -> None:
        q = _make_question(sql="SELECT 1 FROM t")
        drilled = q.derive_drill_down("region", "WEST")
        assert "—" in drilled._specification._description._title.value

    def test_drill_down_has_non_none_identity(self) -> None:
        q = _make_question(sql="SELECT 1 FROM t")
        drilled = q.derive_drill_down("region", "WEST")
        assert drilled._identity is not None
        assert drilled._identity._id is not None
        assert drilled._identity._audit is not None

    def test_drill_down_preserves_rendering(self) -> None:
        q = _make_question(fmt=ResponseKind.TABLE)
        drilled = q.derive_drill_down("region", "WEST")
        assert drilled._specification._rendering is not None
        assert drilled._specification._rendering._decision._format is ResponseKind.TABLE

    def test_drill_down_entity_id_is_valid_uuid(self) -> None:
        # Kills mutmut_27: EntityId(None)
        q = _make_question(sql="SELECT 1 FROM t")
        drilled = q.derive_drill_down("region", "EAST")
        assert isinstance(drilled._identity._id.value, UUID)

    def test_drill_down_audit_created_is_not_none(self) -> None:
        # Kills mutmut_28: _created=None
        q = _make_question(sql="SELECT 1 FROM t")
        drilled = q.derive_drill_down("status", "active")
        assert drilled._identity._audit._created is not None

    def test_drill_down_audit_updated_is_not_none(self) -> None:
        # Kills mutmut_29: _updated=None
        q = _make_question(sql="SELECT 1 FROM t")
        drilled = q.derive_drill_down("status", "active")
        assert drilled._identity._audit._updated is not None

    def test_drill_down_audit_created_value_is_utc_aware(self) -> None:
        # Kills mutmut_32 (CreatedAt(None)) and mutmut_33 (datetime.now(None) = naive)
        q = _make_question(sql="SELECT 1 FROM t")
        drilled = q.derive_drill_down("region", "EAST")
        created = drilled._identity._audit._created.value
        assert isinstance(created, datetime)
        assert created.tzinfo is not None

    def test_drill_down_audit_updated_value_is_utc_aware(self) -> None:
        # Kills mutmut_34 (UpdatedAt(None)) and mutmut_35 (datetime.now(None) = naive)
        q = _make_question(sql="SELECT 1 FROM t")
        drilled = q.derive_drill_down("region", "EAST")
        updated = drilled._identity._audit._updated.value
        assert isinstance(updated, datetime)
        assert updated.tzinfo is not None


class TestRenamePreservesFields:
    """Kill rename mutmut_3 (rendering=None) and mutmut_7 (_query=None)."""

    def test_rename_preserves_rendering(self) -> None:
        # Kills mutmut_3: rendering=None
        q = _make_question(fmt=ResponseKind.CHART)
        original_rendering = q._specification._rendering
        q.rename(QuestionTitle("New Title"))
        assert q._specification._rendering is original_rendering

    def test_rename_preserves_query(self) -> None:
        # Kills mutmut_7: _query=None
        q = _make_question(sql="SELECT id FROM sales")
        original_query = q._specification._description._query
        q.rename(QuestionTitle("New Title"))
        assert q._specification._description._query is original_query
