from __future__ import annotations

import json
from datetime import datetime
from uuid import UUID

from src.questions.application.ports.i_question_repository import IQuestionRepository
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
from src.questions.domain.value_objects import (
    QuestionTitle,
    SqlQuery,
    VizDecision,
    VizSpec,
)
from src.shared.domain.base import AuditRecord, CreatedAt, EntityId, ResponseKind, UpdatedAt
from src.shared.infrastructure.dynamo_models import QuestionModel


class DynamoQuestionRepository(IQuestionRepository):
    def save(self, question: Question) -> None:
        spec = question._specification
        decision = spec._rendering._decision
        model = QuestionModel(
            id=str(question._identity._id.value),
            title=spec._description._title.value,
            sql=spec._description._query._sql.value,
            dataset_id=str(spec._description._query._source._id.value),
            viz_component=decision._spec._component,
            viz_format=decision._format.name,
            viz_props=json.dumps(decision._spec._props),
            viz_children=json.dumps(list(decision._spec._children)),
            created_at=question._identity._audit._created.value.isoformat(),
            updated_at=question._identity._audit._updated.value.isoformat(),
        )
        model.save()

    def load(self, question_id: EntityId) -> Question | None:
        try:
            model = QuestionModel.get(str(question_id.value))
        except QuestionModel.DoesNotExist:
            return None
        return self._doc_to_question(model)

    def delete(self, question_id: EntityId) -> None:
        try:
            QuestionModel.get(str(question_id.value)).delete()
        except QuestionModel.DoesNotExist:
            return

    def find_all(self) -> Questions:
        models = list(QuestionModel.scan())
        return Questions([self._doc_to_question(m) for m in models])

    def _doc_to_question(self, model: QuestionModel) -> Question:
        return Question(
            identity=self._make_identity(model),
            specification=self._make_spec(model),
        )

    def _make_identity(self, model: QuestionModel) -> QuestionIdentity:
        return QuestionIdentity(
            entity_id=EntityId(UUID(model.id)),
            audit=AuditRecord(
                _created=CreatedAt(datetime.fromisoformat(model.created_at)),
                _updated=UpdatedAt(datetime.fromisoformat(model.updated_at)),
            ),
        )

    def _make_spec(self, model: QuestionModel) -> QuestionSpecification:
        viz_format = ResponseKind[model.viz_format or "CHART"]
        viz_props: dict[str, object] = json.loads(model.viz_props or "{}")
        viz_children: tuple[object, ...] = tuple(json.loads(model.viz_children or "[]"))
        return QuestionSpecification(
            description=QuestionDescription(
                _title=QuestionTitle(model.title),
                _query=QueryDefinition(
                    _sql=SqlQuery(model.sql),
                    _source=DatasetReference(
                        _id=EntityId(UUID(model.dataset_id)),
                        _alias=None,
                    ),
                ),
            ),
            rendering=RenderDirective(
                _decision=VizDecision(
                    _format=viz_format,
                    _spec=VizSpec(
                        _component=model.viz_component or "BarChart",
                        _props=viz_props,
                        _children=viz_children,
                    ),
                ),
            ),
        )
