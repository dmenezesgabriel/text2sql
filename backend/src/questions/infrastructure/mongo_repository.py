from __future__ import annotations

from src.shared.domain.base import EntityId
from src.shared.infrastructure.mongo_client import MongoClientSingleton
from src.questions.application.ports.i_question_repository import IQuestionRepository
from src.questions.domain.entities import Question, Questions


class MongoQuestionRepository(IQuestionRepository):
    def __init__(self, mongo: MongoClientSingleton) -> None:
        self._collection = mongo.database["questions"]

    async def save(self, question: Question) -> None:
        doc = {
            "_id": str(question._identity._id.value),
            "title": question._specification._description._title.value,
            "sql": question._specification._description._query._sql.value,
            "dataset_id": str(
                question._specification._description._query._source._id.value
            ),
            "viz_component": question._specification._rendering._decision._spec._component,
            "created_at": question._identity._audit._created.value.isoformat(),
            "updated_at": question._identity._audit._updated.value.isoformat(),
        }
        await self._collection.replace_one(
            {"_id": doc["_id"]}, doc, upsert=True
        )

    async def load(self, question_id: EntityId) -> Question | None:
        doc = await self._collection.find_one({"_id": str(question_id.value)})
        if doc is None:
            return None
        return self._doc_to_question(doc)

    async def delete(self, question_id: EntityId) -> None:
        await self._collection.delete_one({"_id": str(question_id.value)})

    async def find_all(self) -> Questions:
        cursor = self._collection.find()
        items = [self._doc_to_question(doc) for doc in await cursor.to_list(length=1000)]
        return Questions(items)

    def _doc_to_question(self, doc: dict) -> Question:
        from uuid import UUID
        from datetime import datetime
        from questions.domain.value_objects import (
            QuestionTitle, SqlQuery, VizSpec, VizDecision,
        )
        from questions.domain.entities import (
            QuestionIdentity, QuestionSpecification,
            QuestionDescription, QueryDefinition, DatasetReference,
            RenderDirective,
        )
        from shared.domain.base import AuditRecord, CreatedAt, UpdatedAt
        from agent.domain.value_objects import ResponseKind

        return Question(
            identity=QuestionIdentity(
                id=EntityId(UUID(doc["_id"])),
                audit=AuditRecord(
                    _created=CreatedAt(datetime.fromisoformat(doc["created_at"])),
                    _updated=UpdatedAt(datetime.fromisoformat(doc["updated_at"])),
                ),
            ),
            specification=QuestionSpecification(
                description=QuestionDescription(
                    _title=QuestionTitle(doc["title"]),
                    _query=QueryDefinition(
                        _sql=SqlQuery(doc["sql"]),
                        _source=DatasetReference(
                            _id=EntityId(UUID(doc["dataset_id"])),
                            _alias=None,
                        ),
                    ),
                ),
                rendering=RenderDirective(
                    _decision=VizDecision(
                        _format=ResponseKind.CHART,
                        _spec=VizSpec(
                            _component=doc.get("viz_component", "BarChart"),
                            _props={},
                            _children=(),
                        ),
                    )
                ),
            ),
        )
