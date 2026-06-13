from __future__ import annotations

from typing import Protocol

from src.shared.domain.base import EntityId
from src.datasets.domain.value_objects import SchemaDefinition
from src.agent.domain.value_objects import QueryResult


class IQueryEngine(Protocol):
    async def register_schema(
        self, dataset_id: EntityId, schema: SchemaDefinition
    ) -> None: ...

    async def execute(self, sql: str) -> QueryResult: ...

    async def preview(
        self, dataset_id: EntityId, limit: int
    ) -> QueryResult: ...
