from __future__ import annotations

from src.agent.domain.value_objects import QueryResult
from src.datasets.application.ports.i_query_engine import IQueryEngine
from src.questions.application.ports.i_query_executor import IQueryExecutor
from src.questions.domain.value_objects import SqlQuery
from src.shared.domain.base import EntityId


class DuckDBQueryExecutor(IQueryExecutor):
    def __init__(self, engine: IQueryEngine) -> None:
        self._engine = engine

    async def execute(
        self,
        sql: SqlQuery,
        dataset_id: EntityId,
    ) -> QueryResult:
        return await self._engine.execute(sql.value)
