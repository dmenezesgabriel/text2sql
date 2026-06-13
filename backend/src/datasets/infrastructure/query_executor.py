from __future__ import annotations

from src.datasets.application.ports.i_query_engine import IQueryEngine
from src.shared.domain.base import EntityId, QueryResult


class DuckDBQueryExecutor:
    """Adapts IQueryEngine to the IQueryExecutor protocol used by questions use cases."""

    def __init__(self, engine: IQueryEngine) -> None:
        self._engine = engine

    async def execute(self, sql: str, dataset_id: EntityId) -> QueryResult:
        return await self._engine.execute(sql)
