from __future__ import annotations

from datetime import datetime
from uuid import UUID

from src.datasets.application.ports.i_dataset_repository import IDatasetRepository
from src.datasets.domain.entities import Dataset, DatasetConfiguration, DatasetIdentity, Datasets
from src.datasets.domain.value_objects import (
    DatasetKind,
    DatasetName,
    SchemaDefinition,
    StorageUri,
)
from src.shared.domain.base import AuditRecord, CreatedAt, EntityId, UpdatedAt
from src.shared.infrastructure.dynamo_models import DatasetModel


class DynamoDatasetRepository(IDatasetRepository):
    def save(self, dataset: Dataset) -> None:
        model = DatasetModel(
            id=str(dataset._identity._id.value),
            name=dataset._configuration._name.value,
            kind=dataset._configuration._kind.value,
            created_at=dataset._identity._audit._created.value.isoformat(),
            updated_at=dataset._identity._audit._updated.value.isoformat(),
        )
        model.save()

    def load(self, dataset_id: EntityId) -> Dataset | None:
        try:
            model = DatasetModel.get(str(dataset_id.value))
        except DatasetModel.DoesNotExist:
            return None
        return self._doc_to_dataset(model)

    def delete(self, dataset_id: EntityId) -> None:
        try:
            DatasetModel.get(str(dataset_id.value)).delete()
        except DatasetModel.DoesNotExist:
            return

    def find_all(self) -> Datasets:
        models = list(DatasetModel.scan())
        return Datasets([self._doc_to_dataset(m) for m in models])

    def _doc_to_dataset(self, model: DatasetModel) -> Dataset:
        return Dataset(
            identity=DatasetIdentity(
                id=EntityId(UUID(model.id)),
                audit=AuditRecord(
                    _created=CreatedAt(
                        datetime.fromisoformat(model.created_at),
                    ),
                    _updated=UpdatedAt(
                        datetime.fromisoformat(model.updated_at),
                    ),
                ),
            ),
            configuration=DatasetConfiguration(
                _name=DatasetName(model.name),
                _kind=DatasetKind(model.kind),
                _schema=SchemaDefinition(_columns=()),
                _location=StorageUri(""),
            ),
        )
