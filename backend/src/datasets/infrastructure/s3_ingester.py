from __future__ import annotations

from typing import AsyncIterator
from src.datasets.application.ports.i_storage_ingestion import IStorageIngestion
from src.datasets.domain.value_objects import ColumnDefinition, FileFormat, StorageUri


class S3Ingester(IStorageIngestion):
    async def ingest(
        self, uri: StorageUri, format: FileFormat
    ) -> AsyncIterator[ColumnDefinition]:
        yield ColumnDefinition(_name="placeholder", _dtype="VARCHAR", _nullable=True)
