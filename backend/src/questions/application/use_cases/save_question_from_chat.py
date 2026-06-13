from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from src.datasets.application.ports.i_dataset_repository import IDatasetRepository
from src.questions.application.ports.i_question_repository import IQuestionRepository
from src.questions.domain.entities import (
    Question,
    QuestionIdentity,
    QuestionSpecification,
    QuestionTitle,
)
from src.questions.domain.value_objects import SqlQuery, VizDecision
from src.questions.exceptions.dataset_not_found_error import DatasetNotFoundError
from src.questions.exceptions.duplicate_question_error import DuplicateQuestionError
from src.shared.domain.base import AuditRecord, CreatedAt, EntityId, UpdatedAt


@dataclass(frozen=True)
class SaveQuestionFromChatRequest:
    _sql: SqlQuery
    _title: QuestionTitle
    _dataset_id: EntityId
    _decision: VizDecision
    _spec: QuestionSpecification


class SaveQuestionFromChatUseCase:
    def __init__(
        self,
        questions: IQuestionRepository,
        datasets: IDatasetRepository,
    ) -> None:
        self._questions = questions
        self._datasets = datasets

    def execute(self, request: SaveQuestionFromChatRequest) -> Question:
        all_questions = self._questions.find_all()

        for existing in all_questions.to_list():
            if existing._specification._description._query.is_equivalent_to(
                request._spec._description._query,
            ):
                raise DuplicateQuestionError(
                    f"A question with identical SQL already exists: "
                    f"'{existing._identity._id.value}'",
                )

        dataset = self._datasets.load(request._dataset_id)
        if dataset is None:
            raise DatasetNotFoundError(
                f"Dataset {request._dataset_id.value} not found",
            )

        question = Question(
            identity=QuestionIdentity(
                id=EntityId(uuid4()),
                audit=AuditRecord(
                    _created=CreatedAt(datetime.utcnow()),
                    _updated=UpdatedAt(datetime.utcnow()),
                ),
            ),
            specification=request._spec,
        )
        self._questions.save(question)
        return question
