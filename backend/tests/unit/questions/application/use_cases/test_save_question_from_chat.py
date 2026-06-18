from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

import pytest

from src.questions.application.use_cases.save_question_from_chat import (
    SaveQuestionFromChatRequest,
    SaveQuestionFromChatUseCase,
)
from src.questions.domain.entities import (
    DatasetReference,
    QueryDefinition,
    Question,
    QuestionDescription,
    Questions,
    QuestionSpecification,
    RenderDirective,
)
from src.questions.domain.value_objects import QuestionTitle, SqlQuery, VizDecision, VizSpec
from src.questions.exceptions.dataset_not_found_error import DatasetNotFoundError
from src.questions.exceptions.duplicate_question_error import DuplicateQuestionError
from src.shared.domain.base import EntityId, ResponseKind


def _make_spec(dataset_id: EntityId, sql: str = "SELECT 1") -> QuestionSpecification:
    return QuestionSpecification(
        description=QuestionDescription(
            _title=QuestionTitle("Q"),
            _query=QueryDefinition(
                _sql=SqlQuery(sql),
                _source=DatasetReference(_id=dataset_id, _alias=None),
            ),
        ),
        rendering=RenderDirective(
            _decision=VizDecision(
                _format=ResponseKind.TABLE,
                _spec=VizSpec(_component="Table", _props={}, _children=()),
            ),
        ),
    )


class FakeQuestionRepository:
    def __init__(self) -> None:
        self._questions: dict[EntityId, Question] = {}

    def load(self, question_id: EntityId) -> Question | None:
        return self._questions.get(question_id)

    def save(self, question: Question) -> None:
        self._questions[question._identity._id] = question

    def find_all(self) -> Questions:
        return Questions(list(self._questions.values()))

    def delete(self, question_id: EntityId) -> None:
        self._questions.pop(question_id, None)


class FakeDatasetExistence:
    def __init__(self, existing_ids: set[EntityId] | None = None) -> None:
        self._ids: set[EntityId] = existing_ids or set()

    def exists(self, dataset_id: EntityId) -> bool:
        return dataset_id in self._ids


class TestSaveQuestionFromChatUseCase:
    def setup_method(self) -> None:
        self.repo = FakeQuestionRepository()
        self.dataset_id = EntityId(uuid4())
        self.datasets = FakeDatasetExistence({self.dataset_id})
        self.use_case = SaveQuestionFromChatUseCase(
            questions=self.repo,
            datasets=self.datasets,
        )

    def test_saves_question_successfully(self) -> None:
        spec = _make_spec(self.dataset_id)
        request = SaveQuestionFromChatRequest(
            _sql=SqlQuery("SELECT 1"),
            _title=QuestionTitle("Test"),
            _dataset_id=self.dataset_id,
            _decision=spec._rendering._decision,
            _spec=spec,
        )
        question = self.use_case.execute(request)
        assert question._specification._description._title.value == "Q"

    def test_raises_on_dataset_not_found(self) -> None:
        missing_id = EntityId(uuid4())
        spec = _make_spec(missing_id)
        request = SaveQuestionFromChatRequest(
            _sql=SqlQuery("SELECT 1"),
            _title=QuestionTitle("Test"),
            _dataset_id=missing_id,
            _decision=spec._rendering._decision,
            _spec=spec,
        )
        with pytest.raises(DatasetNotFoundError):
            self.use_case.execute(request)

    def test_raises_on_duplicate_sql(self) -> None:
        spec = _make_spec(self.dataset_id, "SELECT 1")
        request = SaveQuestionFromChatRequest(
            _sql=SqlQuery("SELECT 1"),
            _title=QuestionTitle("Test"),
            _dataset_id=self.dataset_id,
            _decision=spec._rendering._decision,
            _spec=spec,
        )
        self.use_case.execute(request)
        with pytest.raises(DuplicateQuestionError):
            self.use_case.execute(request)

    def test_duplicate_error_message_contains_question_id(self) -> None:
        spec = _make_spec(self.dataset_id, "SELECT 1")
        request = SaveQuestionFromChatRequest(
            _sql=SqlQuery("SELECT 1"),
            _title=QuestionTitle("Test"),
            _dataset_id=self.dataset_id,
            _decision=spec._rendering._decision,
            _spec=spec,
        )
        saved = self.use_case.execute(request)
        with pytest.raises(DuplicateQuestionError) as exc_info:
            self.use_case.execute(request)
        assert str(saved._identity._id.value) in str(exc_info.value)

    def test_dataset_not_found_message_contains_dataset_id(self) -> None:
        missing_id = EntityId(uuid4())
        spec = _make_spec(missing_id)
        request = SaveQuestionFromChatRequest(
            _sql=SqlQuery("SELECT 1"),
            _title=QuestionTitle("Test"),
            _dataset_id=missing_id,
            _decision=spec._rendering._decision,
            _spec=spec,
        )
        with pytest.raises(DatasetNotFoundError) as exc_info:
            self.use_case.execute(request)
        assert str(missing_id.value) in str(exc_info.value)

    def test_saved_question_has_non_none_identity(self) -> None:
        spec = _make_spec(self.dataset_id)
        request = SaveQuestionFromChatRequest(
            _sql=SqlQuery("SELECT 99"),
            _title=QuestionTitle("Test"),
            _dataset_id=self.dataset_id,
            _decision=spec._rendering._decision,
            _spec=spec,
        )
        question = self.use_case.execute(request)
        assert question._identity is not None
        assert question._identity._id is not None
        assert question._identity._audit is not None
        assert question._identity._audit._created is not None
        assert question._identity._audit._updated is not None

    def _make_request(self, sql: str = "SELECT 100") -> SaveQuestionFromChatRequest:
        spec = _make_spec(self.dataset_id, sql)
        return SaveQuestionFromChatRequest(
            _sql=SqlQuery(sql),
            _title=QuestionTitle("T"),
            _dataset_id=self.dataset_id,
            _decision=spec._rendering._decision,
            _spec=spec,
        )

    def test_saved_question_entity_id_is_valid_uuid(self) -> None:
        # Kills mutmut_18: EntityId(None)
        question = self.use_case.execute(self._make_request("SELECT 101"))
        assert isinstance(question._identity._id.value, UUID)

    def test_saved_question_created_is_utc_aware(self) -> None:
        # Kills mutmut_23 (CreatedAt(None)) and mutmut_24 (CreatedAt(datetime.now(None)))
        question = self.use_case.execute(self._make_request("SELECT 102"))
        created = question._identity._audit._created.value
        assert isinstance(created, datetime)
        assert created.tzinfo is not None

    def test_saved_question_updated_is_utc_aware(self) -> None:
        # Kills mutmut_25 (UpdatedAt(None)) and mutmut_26 (UpdatedAt(datetime.now(None)))
        question = self.use_case.execute(self._make_request("SELECT 103"))
        updated = question._identity._audit._updated.value
        assert isinstance(updated, datetime)
        assert updated.tzinfo is not None
