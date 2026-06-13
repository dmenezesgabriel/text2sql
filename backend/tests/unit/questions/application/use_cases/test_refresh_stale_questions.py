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
