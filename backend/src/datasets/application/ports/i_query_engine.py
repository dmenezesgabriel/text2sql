from __future__ import annotations

from typing import Protocol

from src.datasets.domain.value_objects import SchemaDefinition
from src.shared.domain.base import EntityId, QueryResult


class IQueryEngine(Protocol):
    async def register_schema(
        self,
        dataset_id: EntityId,
        schema: SchemaDefinition,
    ) -> None: ...

    async def create_view_from_s3(
        self,
        dataset_id: EntityId,
        s3_uri: str,
    ) -> SchemaDefinition: ...

    async def execute(self, sql: str) -> QueryResult: ...

    async def preview(
        self,
        dataset_id: EntityId,
        limit: int,
    ) -> QueryResult: ...
