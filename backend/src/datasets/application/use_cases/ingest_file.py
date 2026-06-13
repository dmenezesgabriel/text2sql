from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from src.datasets.application.ports.i_dataset_repository import IDatasetRepository
from src.datasets.application.ports.i_query_engine import IQueryEngine
from src.datasets.application.ports.i_storage_ingestion import IStorageIngestion
from src.datasets.domain.entities import (
    Dataset,
    DatasetConfiguration,
    DatasetIdentity,
    DatasetKind,
)
from src.datasets.domain.value_objects import (
    ColumnDefinition,
    DatasetName,
    FileFormat,
    SchemaDefinition,
    StorageUri,
)
from src.datasets.exceptions.duplicate_dataset_name_error import DuplicateDatasetNameError
from src.datasets.exceptions.unsupported_format_error import UnsupportedFormatError
from src.shared.domain.base import AuditRecord, CreatedAt, EntityId, UpdatedAt


@dataclass(frozen=True)
class IngestFileRequest:
    _name: DatasetName
    _uri: StorageUri
    _format: FileFormat


class IngestFileUseCase:
    def __init__(
        self,
        datasets: IDatasetRepository,
        storage: IStorageIngestion,
        engine: IQueryEngine,
    ) -> None:
        self._datasets = datasets
        self._storage = storage
        self._engine = engine

    async def execute(self, request: IngestFileRequest) -> Dataset:
        if request._format not in (FileFormat.CSV, FileFormat.PARQUET):
            msg = f"Format {request._format.value} not supported"
            raise UnsupportedFormatError(msg)

        existing = self._datasets.find_all()
        if existing.find_by_name(request._name):
            msg = f"Dataset '{request._name.value}' already exists"
            raise DuplicateDatasetNameError(msg)

        columns: list[ColumnDefinition] = []
        async for column in self._storage.ingest(
            request._uri,
            request._format,
        ):
            columns.append(column)

        schema = SchemaDefinition(_columns=tuple(columns))

        dataset_id = EntityId(uuid4())
        await self._engine.register_schema(dataset_id, schema)

        dataset = Dataset(
            identity=DatasetIdentity(
                entity_id=dataset_id,
                audit=AuditRecord(
                    _created=CreatedAt(datetime.utcnow()),
                    _updated=UpdatedAt(datetime.utcnow()),
                ),
            ),
            configuration=DatasetConfiguration(
                _name=request._name,
                _kind=DatasetKind.FILE,
                _schema=schema,
                _location=request._uri,
            ),
        )
        self._datasets.save(dataset)
        return dataset
