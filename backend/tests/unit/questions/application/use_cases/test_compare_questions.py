from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.questions.application.use_cases.compare_questions import (
    CompareQuestionsUseCase,
    CompareRequest,
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
from src.questions.exceptions.incompatible_questions_error import IncompatibleQuestionsError
from src.questions.exceptions.question_not_found_error import QuestionNotFoundError
from src.shared.domain.base import (
    AuditRecord,
    CreatedAt,
    EntityId,
    QueryResult,
    ResponseKind,
    UpdatedAt,
)


def _make_question(dataset_id: EntityId) -> Question:
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
                    _sql=SqlQuery("SELECT 1"),
                    _source=DatasetReference(_id=dataset_id, _alias=None),
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


class FakeQueryExecutor:
    async def execute(self, sql: str, dataset_id: EntityId) -> QueryResult:
        return QueryResult(_columns=("id",), _rows=({"id": 1},))


class TestCompareQuestionsUseCase:
    def setup_method(self) -> None:
        self.executor = FakeQueryExecutor()

    async def test_raises_when_question_not_found(self) -> None:
        repo = FakeQuestionRepository()
        use_case = CompareQuestionsUseCase(questions=repo, executor=self.executor)
        request = CompareRequest(_first_id=EntityId(uuid4()), _second_id=EntityId(uuid4()))
        with pytest.raises(QuestionNotFoundError):
            await use_case.execute(request)

    async def test_raises_when_questions_incompatible(self) -> None:
        q1 = _make_question(EntityId(uuid4()))
        q2 = _make_question(EntityId(uuid4()))  # different dataset
        repo = FakeQuestionRepository({q1._identity._id: q1, q2._identity._id: q2})
        use_case = CompareQuestionsUseCase(questions=repo, executor=self.executor)
        request = CompareRequest(_first_id=q1._identity._id, _second_id=q2._identity._id)
        with pytest.raises(IncompatibleQuestionsError):
            await use_case.execute(request)

    async def test_returns_report_for_compatible_questions(self) -> None:
        dataset_id = EntityId(uuid4())
        q1 = _make_question(dataset_id)
        q2 = _make_question(dataset_id)
        repo = FakeQuestionRepository({q1._identity._id: q1, q2._identity._id: q2})
        use_case = CompareQuestionsUseCase(questions=repo, executor=self.executor)
        request = CompareRequest(_first_id=q1._identity._id, _second_id=q2._identity._id)
        report = await use_case.execute(request)
        assert report._first_title == "Q"
        assert report._second_title == "Q"

    async def test_raises_when_only_first_is_missing(self) -> None:
        # Kills `or` → `and`: `if first is None and second is None` would NOT raise when only first is None
        dataset_id = EntityId(uuid4())
        q2 = _make_question(dataset_id)
        repo = FakeQuestionRepository({q2._identity._id: q2})
        use_case = CompareQuestionsUseCase(questions=repo, executor=self.executor)
        request = CompareRequest(_first_id=EntityId(uuid4()), _second_id=q2._identity._id)
        with pytest.raises(QuestionNotFoundError):
            await use_case.execute(request)

    async def test_raises_when_only_second_is_missing(self) -> None:
        dataset_id = EntityId(uuid4())
        q1 = _make_question(dataset_id)
        repo = FakeQuestionRepository({q1._identity._id: q1})
        use_case = CompareQuestionsUseCase(questions=repo, executor=self.executor)
        request = CompareRequest(_first_id=q1._identity._id, _second_id=EntityId(uuid4()))
        with pytest.raises(QuestionNotFoundError):
            await use_case.execute(request)

    async def test_not_found_error_message_exact(self) -> None:
        repo = FakeQuestionRepository()
        use_case = CompareQuestionsUseCase(questions=repo, executor=self.executor)
        request = CompareRequest(_first_id=EntityId(uuid4()), _second_id=EntityId(uuid4()))
        with pytest.raises(QuestionNotFoundError) as exc_info:
            await use_case.execute(request)
        assert str(exc_info.value) == "One or both questions not found"

    async def test_incompatible_error_message_exact(self) -> None:
        q1 = _make_question(EntityId(uuid4()))
        q2 = _make_question(EntityId(uuid4()))
        repo = FakeQuestionRepository({q1._identity._id: q1, q2._identity._id: q2})
        use_case = CompareQuestionsUseCase(questions=repo, executor=self.executor)
        request = CompareRequest(_first_id=q1._identity._id, _second_id=q2._identity._id)
        with pytest.raises(IncompatibleQuestionsError) as exc_info:
            await use_case.execute(request)
        assert str(exc_info.value) == "Questions must query the same dataset"

    async def test_report_first_rows_not_none(self) -> None:
        dataset_id = EntityId(uuid4())
        q1 = _make_question(dataset_id)
        q2 = _make_question(dataset_id)
        repo = FakeQuestionRepository({q1._identity._id: q1, q2._identity._id: q2})
        use_case = CompareQuestionsUseCase(questions=repo, executor=self.executor)
        request = CompareRequest(_first_id=q1._identity._id, _second_id=q2._identity._id)
        report = await use_case.execute(request)
        assert report._first_rows is not None
        assert report._second_rows is not None
        assert report._differences is not None

    async def test_report_differences_has_added_and_removed(self) -> None:
        dataset_id = EntityId(uuid4())
        q1 = _make_question(dataset_id)
        q2 = _make_question(dataset_id)
        repo = FakeQuestionRepository({q1._identity._id: q1, q2._identity._id: q2})
        use_case = CompareQuestionsUseCase(questions=repo, executor=self.executor)
        request = CompareRequest(_first_id=q1._identity._id, _second_id=q2._identity._id)
        report = await use_case.execute(request)
        assert len(report._differences) == 1
        diff = report._differences[0]
        assert diff._added is not None
        assert diff._removed is not None

    async def test_diff_added_contains_rows_from_second_not_in_first(self) -> None:
        """Kills mutmut_10: dict(None) instead of dict(r) for _added."""
        dataset_id = EntityId(uuid4())
        q1 = _make_question(dataset_id)
        q2 = _make_question(dataset_id)

        call_count = 0

        class DifferentResultsExecutor:
            async def execute(self, sql: str, dataset_id: EntityId) -> QueryResult:
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return QueryResult(_columns=("id",), _rows=({"id": 1},))
                return QueryResult(_columns=("id",), _rows=({"id": 1}, {"id": 2}))

        repo = FakeQuestionRepository({q1._identity._id: q1, q2._identity._id: q2})
        use_case = CompareQuestionsUseCase(questions=repo, executor=DifferentResultsExecutor())  # type: ignore[arg-type]
        request = CompareRequest(_first_id=q1._identity._id, _second_id=q2._identity._id)
        report = await use_case.execute(request)
        diff = report._differences[0]
        assert diff._added == [{"id": 2}]

    async def test_diff_removed_contains_rows_from_first_not_in_second(self) -> None:
        """Kills mutmut_11/13: dict(None) instead of dict(r) for _removed."""
        dataset_id = EntityId(uuid4())
        q1 = _make_question(dataset_id)
        q2 = _make_question(dataset_id)

        call_count = 0

        class DifferentResultsExecutor:
            async def execute(self, sql: str, dataset_id: EntityId) -> QueryResult:
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return QueryResult(_columns=("id",), _rows=({"id": 1}, {"id": 3}))
                return QueryResult(_columns=("id",), _rows=({"id": 1},))

        repo = FakeQuestionRepository({q1._identity._id: q1, q2._identity._id: q2})
        use_case = CompareQuestionsUseCase(questions=repo, executor=DifferentResultsExecutor())  # type: ignore[arg-type]
        request = CompareRequest(_first_id=q1._identity._id, _second_id=q2._identity._id)
        report = await use_case.execute(request)
        diff = report._differences[0]
        assert diff._removed == [{"id": 3}]

    async def test_diff_added_and_removed_present_when_queries_differ(self) -> None:
        """Kills mutmut_9: entire _added/_removed block removed from ComparisonDiff."""
        dataset_id = EntityId(uuid4())
        q1 = _make_question(dataset_id)
        q2 = _make_question(dataset_id)

        call_count = 0

        class DifferentResultsExecutor:
            async def execute(self, sql: str, dataset_id: EntityId) -> QueryResult:
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return QueryResult(_columns=("id",), _rows=({"id": 1}, {"id": 2}))
                return QueryResult(_columns=("id",), _rows=({"id": 1}, {"id": 3}))

        repo = FakeQuestionRepository({q1._identity._id: q1, q2._identity._id: q2})
        use_case = CompareQuestionsUseCase(questions=repo, executor=DifferentResultsExecutor())  # type: ignore[arg-type]
        report = await use_case.execute(
            CompareRequest(_first_id=q1._identity._id, _second_id=q2._identity._id),
        )
        diff = report._differences[0]
        assert diff._added == [{"id": 3}]
        assert diff._removed == [{"id": 2}]

    async def test_executor_called_with_correct_sql(self) -> None:
        dataset_id = EntityId(uuid4())

        class RecordingExecutor:
            calls: list[dict] = []

            async def execute(self, sql: str, dataset_id: EntityId) -> QueryResult:
                RecordingExecutor.calls.append({"sql": sql, "dataset_id": dataset_id})
                return QueryResult(_columns=("id",), _rows=({"id": 1},))

        executor = RecordingExecutor()
        q1 = _make_question(dataset_id)
        q2 = _make_question(dataset_id)
        repo = FakeQuestionRepository({q1._identity._id: q1, q2._identity._id: q2})
        use_case = CompareQuestionsUseCase(questions=repo, executor=executor)
        request = CompareRequest(_first_id=q1._identity._id, _second_id=q2._identity._id)
        await use_case.execute(request)
        assert len(RecordingExecutor.calls) == 2
        assert RecordingExecutor.calls[0]["sql"] == q1.compiled_sql()
        assert RecordingExecutor.calls[0]["dataset_id"] == dataset_id
        assert RecordingExecutor.calls[1]["sql"] == q2.compiled_sql()
        assert RecordingExecutor.calls[1]["dataset_id"] == dataset_id
