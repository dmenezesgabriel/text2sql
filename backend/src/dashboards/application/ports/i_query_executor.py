from __future__ import annotations

from typing import Protocol

from src.shared.domain.base import EntityId
from src.questions.domain.value_objects import SqlQuery
from src.agent.domain.value_objects import QueryResult


class IQueryExecutor(Protocol):
    async def execute(
        self, sql: SqlQuery, dataset_id: EntityId
    ) -> QueryResult: ...
