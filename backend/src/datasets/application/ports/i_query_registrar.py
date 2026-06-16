from __future__ import annotations

from typing import Protocol

from src.datasets.domain.value_objects import SchemaDefinition
from src.shared.domain.base import EntityId


class IQueryRegistrar(Protocol):
    """Port for registering S3 views in the query engine."""

    async def create_view_from_s3(
        self,
        dataset_id: EntityId,
        s3_uri: str,
    ) -> SchemaDefinition: ...
