from __future__ import annotations

from typing import AsyncIterator, Protocol

from src.datasets.domain.value_objects import ColumnDefinition, FileFormat, StorageUri


class IStorageIngestion(Protocol):
    async def ingest(
        self, uri: StorageUri, format: FileFormat
    ) -> AsyncIterator[ColumnDefinition]: ...
