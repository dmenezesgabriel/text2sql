from __future__ import annotations

from typing import Protocol

from src.shared.domain.base import EntityId, QueryResult


class IQueryEngine(Protocol):
    """Port for executing SQL queries and previewing dataset contents."""

    async def execute(self, sql: str) -> QueryResult: ...

    async def preview(
        self,
        dataset_id: EntityId,
        limit: int,
    ) -> QueryResult: ...
