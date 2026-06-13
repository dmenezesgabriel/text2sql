from __future__ import annotations

from typing import Protocol

from src.agent.domain.value_objects import QueryResult
from src.questions.domain.value_objects import SqlQuery
from src.shared.domain.base import EntityId


class IQueryExecutor(Protocol):
    async def execute(
        self,
        sql: SqlQuery,
        dataset_id: EntityId,
    ) -> QueryResult: ...
