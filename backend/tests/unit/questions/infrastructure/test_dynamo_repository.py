from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest.mock import patch
from uuid import uuid4

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
