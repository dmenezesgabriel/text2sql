from __future__ import annotations

from dataclasses import dataclass

from src.datasets.domain.value_objects import (
    ConnectionString,
    DatasetKind,
    DatasetName,
    SchemaDefinition,
    StorageUri,
)
from src.shared.domain.base import AuditRecord, Entity, EntityId, ValueObject


class DatasetIdentity:
    def __init__(self, entity_id: EntityId, audit: AuditRecord) -> None:
        self._id = entity_id
        self._audit = audit


@dataclass(frozen=True)
class DatasetConfiguration(ValueObject):
    _name: DatasetName
    _kind: DatasetKind
    _schema: SchemaDefinition
    _location: StorageUri | ConnectionString


class Dataset(Entity):
    def __init__(
        self,
        identity: DatasetIdentity,
        configuration: DatasetConfiguration,
    ) -> None:
        self._identity = identity
        self._configuration = configuration


class Datasets:
    def __init__(self, items: list[Dataset] | None = None) -> None:
        self._items: list[Dataset] = items or []

    def add(self, dataset: Dataset) -> None:
        self._items.append(dataset)

    def remove(self, dataset_id: EntityId) -> None:
        self._items = [d for d in self._items if d._identity._id != dataset_id]

    def find_by_name(self, name: DatasetName) -> Dataset | None:
        for dataset in self._items:
            if dataset._configuration._name == name:
                return dataset
        return None

    def to_list(self) -> list[Dataset]:
        return list(self._items)
