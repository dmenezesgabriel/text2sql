from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol

from src.datasets.domain.value_objects import ColumnDefinition, FileFormat, StorageUri


class IStorageIngestion(Protocol):
    async def ingest(
        self,
        uri: StorageUri,
        file_format: FileFormat,
    ) -> AsyncIterator[ColumnDefinition]: ...
