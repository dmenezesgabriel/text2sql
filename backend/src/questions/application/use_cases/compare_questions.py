from __future__ import annotations

from dataclasses import dataclass, field

from src.shared.domain.base import EntityId
from src.questions.application.ports.i_question_repository import IQuestionRepository
from src.questions.application.ports.i_query_executor import IQueryExecutor
from src.questions.exceptions.question_not_found_error import QuestionNotFoundError
from src.questions.exceptions.incompatible_questions_error import IncompatibleQuestionsError
from src.agent.domain.value_objects import QueryResult


@dataclass(frozen=True)
class CompareRequest:
    _first_id: EntityId
    _second_id: EntityId


@dataclass(frozen=True)
class RowDifference:
    _added: list[dict] = field(default_factory=list)
    _removed: list[dict] = field(default_factory=list)


@dataclass(frozen=True)
class ComparisonReport:
    _first_title: str
    _second_title: str
    _first_rows: QueryResult
    _second_rows: QueryResult
    _differences: list[RowDifference]


class CompareQuestionsUseCase:
    def __init__(
        self,
        questions: IQuestionRepository,
        executor: IQueryExecutor,
    ) -> None:
        self._questions = questions
        self._executor = executor

    async def execute(self, request: CompareRequest) -> ComparisonReport:
        first = await self._questions.load(request._first_id)
        second = await self._questions.load(request._second_id)
        if first is None or second is None:
            raise QuestionNotFoundError("One or both questions not found")

        if not first.is_compatible_with(second):
            raise IncompatibleQuestionsError(
                "Questions must query the same dataset"
            )

        first_result = await self._executor.execute(
            sql=first._specification._description._query._sql,
            dataset_id=first._specification._description._query._source._id,
        )
        second_result = await self._executor.execute(
            sql=second._specification._description._query._sql,
            dataset_id=second._specification._description._query._source._id,
        )

        return ComparisonReport(
            _first_title=first._specification._description._title.value,
            _second_title=second._specification._description._title.value,
            _first_rows=first_result,
            _second_rows=second_result,
            _differences=self._compute_differences(first_result, second_result),
        )

    def _compute_differences(
        self, first: QueryResult, second: QueryResult
    ) -> list[RowDifference]:
        first_set = {tuple(sorted(r.items())) for r in first._rows}
        second_set = {tuple(sorted(r.items())) for r in second._rows}
        return [
            RowDifference(
                _added=[dict(r) for r in second_set - first_set],
                _removed=[dict(r) for r in first_set - second_set],
            )
        ]
