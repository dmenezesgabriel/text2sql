from __future__ import annotations

from typing import Protocol

from src.shared.domain.base import EntityId, QueryResult


class IQueryExecutor(Protocol):
    async def execute(self, sql: str, dataset_id: EntityId) -> QueryResult: ...
