from __future__ import annotations

from collections.abc import AsyncIterator

from src.datasets.application.ports.i_storage_ingestion import IStorageIngestion
from src.datasets.domain.value_objects import ColumnDefinition, FileFormat, StorageUri


class S3Ingester(IStorageIngestion):
    async def ingest(
        self,
        uri: StorageUri,
        file_format: FileFormat,
    ) -> AsyncIterator[ColumnDefinition]:
        yield ColumnDefinition(_name="placeholder", _dtype="VARCHAR", _nullable=True)
