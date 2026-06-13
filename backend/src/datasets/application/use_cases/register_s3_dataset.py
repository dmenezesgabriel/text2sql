from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from src.datasets.application.ports.i_dataset_repository import IDatasetRepository
from src.datasets.application.ports.i_query_engine import IQueryEngine
from src.datasets.domain.entities import Dataset, DatasetConfiguration, DatasetIdentity
from src.datasets.domain.value_objects import DatasetKind, DatasetName, StorageUri
from src.datasets.exceptions.duplicate_dataset_name_error import DuplicateDatasetNameError
from src.shared.domain.base import AuditRecord, CreatedAt, EntityId, UpdatedAt


@dataclass(frozen=True)
class RegisterS3DatasetRequest:
    _name: DatasetName
    _s3_uri: StorageUri


class RegisterS3DatasetUseCase:
    """Register a Parquet file stored in S3/MinIO as a queryable DuckDB view."""

    def __init__(self, datasets: IDatasetRepository, engine: IQueryEngine) -> None:
        self._datasets = datasets
        self._engine = engine

    async def execute(self, request: RegisterS3DatasetRequest) -> Dataset:
        if self._datasets.find_all().find_by_name(request._name):
            msg = f"Dataset '{request._name.value}' already exists"
            raise DuplicateDatasetNameError(msg)

        dataset_id = EntityId(uuid4())
        schema = await self._engine.create_view_from_s3(dataset_id, request._s3_uri.value)

        now = datetime.now(UTC)
        dataset = Dataset(
            identity=DatasetIdentity(
                entity_id=dataset_id,
                audit=AuditRecord(
                    _created=CreatedAt(now),
                    _updated=UpdatedAt(now),
                ),
            ),
            configuration=DatasetConfiguration(
                _name=request._name,
                _kind=DatasetKind.FILE,
                _schema=schema,
                _location=request._s3_uri,
            ),
        )
        self._datasets.save(dataset)
        return dataset
