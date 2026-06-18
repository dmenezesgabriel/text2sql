from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest.mock import patch
from uuid import UUID, uuid4

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
from src.questions.infrastructure.dynamo_repository import DynamoQuestionRepository
from src.shared.domain.base import AuditRecord, CreatedAt, EntityId, ResponseKind, UpdatedAt
from src.shared.infrastructure.dynamo_models import QuestionModel


def _make_question(
    *,
    viz_format: ResponseKind = ResponseKind.CHART,
    viz_props: dict[str, object] | None = None,
    viz_children: tuple[object, ...] = (),
) -> Question:
    now = datetime.now(UTC)
    return Question(
        identity=QuestionIdentity(
            entity_id=EntityId(uuid4()),
            audit=AuditRecord(_created=CreatedAt(now), _updated=UpdatedAt(now)),
        ),
        specification=QuestionSpecification(
            description=QuestionDescription(
                _title=QuestionTitle("Test"),
                _query=QueryDefinition(
                    _sql=SqlQuery("SELECT 1"),
                    _source=DatasetReference(_id=EntityId(uuid4()), _alias=None),
                ),
            ),
            rendering=RenderDirective(
                _decision=VizDecision(
                    _format=viz_format,
                    _spec=VizSpec(
                        _component="BarChart",
                        _props=viz_props or {},
                        _children=viz_children,
                    ),
                ),
            ),
        ),
    )


def _make_question_model(
    *,
    viz_format: str = "CHART",
    viz_props: str = "{}",
    viz_children: str = "[]",
) -> QuestionModel:
    return QuestionModel(
        id=str(uuid4()),
        title="Test Question",
        sql="SELECT 1",
        dataset_id=str(uuid4()),
        viz_component="BarChart",
        viz_format=viz_format,
        viz_props=viz_props,
        viz_children=viz_children,
        created_at="2026-01-01T00:00:00+00:00",
        updated_at="2026-01-01T00:00:00+00:00",
    )


class TestDynamoQuestionRepository:
    def test_module_imports(self) -> None:
        from src.questions.infrastructure.dynamo_repository import DynamoQuestionRepository

        assert DynamoQuestionRepository is not None

    def test_class_is_instantiable(self) -> None:
        from src.questions.infrastructure.dynamo_repository import DynamoQuestionRepository

        repo = DynamoQuestionRepository()
        assert repo is not None

    def test_doc_to_question_restores_table_format(self) -> None:
        model = _make_question_model(viz_format="TABLE")
        question = DynamoQuestionRepository()._doc_to_question(model)
        assert question._specification._rendering._decision._format is ResponseKind.TABLE

    def test_doc_to_question_restores_text_format(self) -> None:
        model = _make_question_model(viz_format="TEXT")
        question = DynamoQuestionRepository()._doc_to_question(model)
        assert question._specification._rendering._decision._format is ResponseKind.TEXT

    def test_doc_to_question_restores_viz_props(self) -> None:
        model = _make_question_model(viz_props='{"color": "red", "size": 42}')
        question = DynamoQuestionRepository()._doc_to_question(model)
        assert question._specification._rendering._decision._spec._props == {
            "color": "red",
            "size": 42,
        }

    def test_doc_to_question_restores_viz_children(self) -> None:
        model = _make_question_model(viz_children='["child1", "child2"]')
        question = DynamoQuestionRepository()._doc_to_question(model)
        assert question._specification._rendering._decision._spec._children == ("child1", "child2")

    def test_save_serializes_viz_format(self) -> None:
        question = _make_question(viz_format=ResponseKind.TABLE)
        with patch.object(QuestionModel, "save", autospec=True) as mock_save:
            DynamoQuestionRepository().save(question)
        saved = mock_save.call_args[0][0]
        assert saved.viz_format == "TABLE"

    def test_save_serializes_viz_props(self) -> None:
        question = _make_question(viz_props={"x": 1, "label": "hello"})
        with patch.object(QuestionModel, "save", autospec=True) as mock_save:
            DynamoQuestionRepository().save(question)
        saved = mock_save.call_args[0][0]
        assert json.loads(saved.viz_props) == {"x": 1, "label": "hello"}

    def test_save_serializes_viz_children(self) -> None:
        question = _make_question(viz_children=("a", "b"))
        with patch.object(QuestionModel, "save", autospec=True) as mock_save:
            DynamoQuestionRepository().save(question)
        saved = mock_save.call_args[0][0]
        assert json.loads(saved.viz_children) == ["a", "b"]

    def test_doc_to_question_uses_barchart_when_component_is_none(self) -> None:
        # Kills `_component=model.viz_component or "BarChart"` → `and "BarChart"` mutation
        # (`None and "BarChart"` = None, `None or "BarChart"` = "BarChart")
        model = QuestionModel(
            id=str(uuid4()),
            title="Test",
            sql="SELECT 1",
            dataset_id=str(uuid4()),
            viz_component=None,
            viz_format="CHART",
            viz_props="{}",
            viz_children="[]",
            created_at="2026-01-01T00:00:00+00:00",
            updated_at="2026-01-01T00:00:00+00:00",
        )
        question = DynamoQuestionRepository()._doc_to_question(model)
        assert question._specification._rendering._decision._spec._component == "BarChart"

    def test_doc_to_question_uses_chart_format_when_viz_format_is_none(self) -> None:
        model = QuestionModel(
            id=str(uuid4()),
            title="Test",
            sql="SELECT 1",
            dataset_id=str(uuid4()),
            viz_component="BarChart",
            viz_format=None,
            viz_props="{}",
            viz_children="[]",
            created_at="2026-01-01T00:00:00+00:00",
            updated_at="2026-01-01T00:00:00+00:00",
        )
        question = DynamoQuestionRepository()._doc_to_question(model)
        assert question._specification._rendering._decision._format is ResponseKind.CHART

    def test_doc_to_question_uses_empty_dict_when_viz_props_is_none(self) -> None:
        model = QuestionModel(
            id=str(uuid4()),
            title="Test",
            sql="SELECT 1",
            dataset_id=str(uuid4()),
            viz_component="BarChart",
            viz_format="CHART",
            viz_props=None,
            viz_children="[]",
            created_at="2026-01-01T00:00:00+00:00",
            updated_at="2026-01-01T00:00:00+00:00",
        )
        question = DynamoQuestionRepository()._doc_to_question(model)
        assert question._specification._rendering._decision._spec._props == {}

    def test_doc_to_question_uses_empty_tuple_when_viz_children_is_none(self) -> None:
        model = QuestionModel(
            id=str(uuid4()),
            title="Test",
            sql="SELECT 1",
            dataset_id=str(uuid4()),
            viz_component="BarChart",
            viz_format="CHART",
            viz_props="{}",
            viz_children=None,
            created_at="2026-01-01T00:00:00+00:00",
            updated_at="2026-01-01T00:00:00+00:00",
        )
        question = DynamoQuestionRepository()._doc_to_question(model)
        assert question._specification._rendering._decision._spec._children == ()

    def test_doc_to_question_identity_is_not_none(self) -> None:
        model = _make_question_model()
        question = DynamoQuestionRepository()._doc_to_question(model)
        assert question._identity is not None
        assert question._identity._id is not None
        assert question._identity._audit is not None
        assert question._identity._audit._created is not None
        assert question._identity._audit._updated is not None

    def test_doc_to_question_description_is_not_none(self) -> None:
        model = _make_question_model()
        question = DynamoQuestionRepository()._doc_to_question(model)
        assert question._specification._description is not None
        assert question._specification._description._title is not None
        assert question._specification._description._query is not None
        assert question._specification._description._query._source is not None
        assert question._specification._description._query._source._id is not None

    def test_doc_to_question_preserves_component_when_set(self) -> None:
        model = _make_question_model()
        model.viz_component = "LineChart"
        question = DynamoQuestionRepository()._doc_to_question(model)
        assert question._specification._rendering._decision._spec._component == "LineChart"

    def test_doc_to_question_created_value_is_utc_aware(self) -> None:
        # Kills mutmut_11: _created=CreatedAt(None) — wrapper is non-None but .value is None
        model = _make_question_model()
        question = DynamoQuestionRepository()._doc_to_question(model)
        created = question._identity._audit._created.value
        assert created is not None
        assert created.tzinfo is not None

    def test_doc_to_question_updated_value_is_utc_aware(self) -> None:
        # Kills mutmut_13: _updated=UpdatedAt(None) — wrapper is non-None but .value is None
        model = _make_question_model()
        question = DynamoQuestionRepository()._doc_to_question(model)
        updated = question._identity._audit._updated.value
        assert updated is not None
        assert updated.tzinfo is not None

    def test_doc_to_question_dataset_id_value_is_valid_uuid(self) -> None:
        # Kills mutmut_31: _id=EntityId(None) — wrapper is non-None but .value is None
        model = _make_question_model()
        question = DynamoQuestionRepository()._doc_to_question(model)
        dataset_id_value = question._specification._description._query._source._id.value
        assert dataset_id_value is not None
        assert isinstance(dataset_id_value, UUID)
