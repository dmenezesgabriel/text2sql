from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from src.questions.application.use_cases.refresh_stale_questions import (
    RefreshStaleQuestionsUseCase,
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
from src.questions.domain.value_objects import QuestionTitle, SqlQuery, VizDecision
from src.shared.domain.base import (
    AuditRecord,
    CreatedAt,
    EntityId,
    QueryResult,
    ResponseKind,
    UpdatedAt,
)


class FakeQuestionRepository:
    def __init__(self, questions: list[Question]) -> None:
        self._questions = questions
        self.saved: list[Question] = []

    def find_all(self) -> Questions:
        return Questions(list(self._questions))

    def save(self, question: Question) -> None:
        self.saved.append(question)

    def load(self, question_id: EntityId) -> Question | None:
        return next((q for q in self._questions if q._identity._id == question_id), None)

    def delete(self, question_id: EntityId) -> None:
        self._questions = [q for q in self._questions if q._identity._id != question_id]


class FakeQueryExecutor:
    def __init__(self, should_fail: bool = False) -> None:
        self._should_fail = should_fail
        self.calls: list[str] = []

    async def execute(self, sql: str, dataset_id: EntityId) -> QueryResult:
        self.calls.append(sql)
        if self._should_fail:
            msg = "DB error"
            raise RuntimeError(msg)
        return QueryResult(_columns=("x",), _rows=({"x": 1},))


class FakeNotifier:
    def __init__(self) -> None:
        self.notifications: list[str] = []

    def notify(self, message: str) -> None:
        self.notifications.append(message)


def _make_stale_question(days_old: int = 10) -> Question:
    dataset_id = EntityId(uuid4())
    return Question(
        identity=QuestionIdentity(
            entity_id=EntityId(uuid4()),
            audit=AuditRecord(
                _created=CreatedAt(datetime.now(UTC) - timedelta(days=days_old)),
                _updated=UpdatedAt(datetime.now(UTC) - timedelta(days=days_old)),
            ),
        ),
        specification=QuestionSpecification(
            description=QuestionDescription(
                _title=QuestionTitle("Test Q"),
                _query=QueryDefinition(
                    _sql=SqlQuery("SELECT 1"),
                    _source=DatasetReference(_id=dataset_id, _alias=None),
                ),
            ),
            rendering=RenderDirective(
                _decision=VizDecision(_format=ResponseKind.TABLE, _spec=None),
            ),
        ),
    )


class TestRefreshStaleQuestionsUseCase:
    def _make_use_case(
        self,
        questions: list[Question],
        executor: FakeQueryExecutor | None = None,
        notifier: FakeNotifier | None = None,
    ) -> tuple[RefreshStaleQuestionsUseCase, FakeNotifier]:
        notifier = notifier or FakeNotifier()
        executor = executor or FakeQueryExecutor()
        repo = FakeQuestionRepository(questions)
        use_case = RefreshStaleQuestionsUseCase(
            questions=repo,
            executor=executor,
            notifier=notifier,
        )
        return use_case, notifier

    async def test_refreshes_stale_questions(self) -> None:
        question = _make_stale_question(days_old=10)
        use_case, notifier = self._make_use_case([question])
        report = await use_case.execute(threshold_days=5)
        assert len(report._refreshed) == 1
        assert len(notifier.notifications) == 1

    async def test_skips_fresh_questions(self) -> None:
        question = _make_stale_question(days_old=1)
        use_case, notifier = self._make_use_case([question])
        report = await use_case.execute(threshold_days=5)
        assert len(report._refreshed) == 0
        assert len(notifier.notifications) == 0

    async def test_records_failures(self) -> None:
        question = _make_stale_question(days_old=10)
        executor = FakeQueryExecutor(should_fail=True)
        use_case, _ = self._make_use_case([question], executor=executor)
        report = await use_case.execute(threshold_days=5)
        assert len(report._failed) == 1
        assert len(report._refreshed) == 0

    async def test_empty_question_list(self) -> None:
        use_case, notifier = self._make_use_case([])
        report = await use_case.execute(threshold_days=5)
        assert report._refreshed == []
        assert report._failed == []
        assert notifier.notifications == []

    async def test_refreshes_question_exactly_at_threshold_days(self) -> None:
        # Kills `age.days <= threshold_days` mutation (was `<`).
        # When age.days == threshold_days: `<` is False → do refresh; `<=` is True → skip.
        question = _make_stale_question(days_old=5)
        use_case, notifier = self._make_use_case([question])
        report = await use_case.execute(threshold_days=5)
        assert len(report._refreshed) == 1

    async def test_fresh_question_at_threshold_minus_one_is_skipped(self) -> None:
        question = _make_stale_question(days_old=4)
        use_case, notifier = self._make_use_case([question])
        report = await use_case.execute(threshold_days=5)
        assert len(report._refreshed) == 0

    async def test_continue_not_break_on_fresh_question(self) -> None:
        # Kills `continue` → `break`: fresh question followed by stale question.
        # With break, second question would never be processed.
        fresh = _make_stale_question(days_old=1)
        stale = _make_stale_question(days_old=10)
        use_case, notifier = self._make_use_case([fresh, stale])
        report = await use_case.execute(threshold_days=5)
        assert len(report._refreshed) == 1
        assert report._refreshed[0] == stale._identity._id

    async def test_failure_tuple_has_question_id_and_error_string(self) -> None:
        question = _make_stale_question(days_old=10)
        executor = FakeQueryExecutor(should_fail=True)
        use_case, _ = self._make_use_case([question], executor=executor)
        report = await use_case.execute(threshold_days=5)
        assert len(report._failed) == 1
        failed_id, error_str = report._failed[0]
        assert failed_id == question._identity._id
        assert isinstance(error_str, str)
        assert error_str == "DB error"

    async def test_notification_message_contains_title(self) -> None:
        question = _make_stale_question(days_old=10)
        use_case, notifier = self._make_use_case([question])
        await use_case.execute(threshold_days=5)
        assert len(notifier.notifications) == 1
        msg = notifier.notifications[0]
        assert "Test Q" in msg
        assert "new data available" in msg

    async def test_executor_called_with_correct_sql(self) -> None:
        question = _make_stale_question(days_old=10)
        executor = FakeQueryExecutor()
        use_case, _ = self._make_use_case([question], executor=executor)
        await use_case.execute(threshold_days=5)
        assert question.compiled_sql() in executor.calls

    async def test_executor_called_with_correct_dataset_id(self) -> None:
        class RecordingExecutor:
            calls: list[dict] = []

            async def execute(self, sql: str, dataset_id: EntityId) -> QueryResult:
                RecordingExecutor.calls.append({"sql": sql, "dataset_id": dataset_id})
                return QueryResult(_columns=("x",), _rows=({"x": 1},))

        question = _make_stale_question(days_old=10)
        executor = RecordingExecutor()
        use_case, _ = self._make_use_case([question], executor=executor)
        await use_case.execute(threshold_days=5)
        expected_dataset_id = question._specification._description._query._source._id
        assert RecordingExecutor.calls[0]["dataset_id"] == expected_dataset_id
