from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from src.shared.domain.base import EntityId
from src.questions.domain.entities import Question
from src.questions.application.ports.i_question_repository import IQuestionRepository
from src.questions.application.ports.i_query_executor import IQueryExecutor


class INotificationPort(Protocol):
    def notify(self, message: str) -> None: ...


@dataclass(frozen=True)
class RefreshReport:
    _refreshed: list[EntityId]
    _failed: list[tuple[EntityId, str]]


class RefreshStaleQuestionsUseCase:
    def __init__(
        self,
        questions: IQuestionRepository,
        executor: IQueryExecutor,
        notifier: INotificationPort,
    ) -> None:
        self._questions = questions
        self._executor = executor
        self._notifier = notifier

    async def execute(self, threshold_days: int) -> RefreshReport:
        all_questions = await self._questions.find_all()
        changed: list[Question] = []
        failed: list[tuple[EntityId, str]] = []
        now = datetime.utcnow()

        for question in all_questions.to_list():
            age = now - question._identity._audit._updated.value
            if age.days < threshold_days:
                continue

            try:
                await self._executor.execute(
                    sql=question._specification._description._query._sql,
                    dataset_id=question._specification._description._query._source._id,
                )
                changed.append(question)
            except Exception as exc:
                failed.append((question._identity._id, str(exc)))

        for question in changed:
            self._notifier.notify(
                f"Question '{question._specification._description._title.value}' "
                f"has new data available"
            )

        return RefreshReport(
            _refreshed=[q._identity._id for q in changed],
            _failed=failed,
        )
