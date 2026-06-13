from __future__ import annotations

from src.shared.domain.base import EntityId
from src.shared.infrastructure.mongo_client import MongoClientSingleton
from src.datasets.application.ports.i_dataset_repository import IDatasetRepository
from src.datasets.domain.entities import Dataset, Datasets


class MongoDatasetRepository(IDatasetRepository):
    def __init__(self, mongo: MongoClientSingleton) -> None:
        self._collection = mongo.database["datasets"]

    async def save(self, dataset: Dataset) -> None:
        doc = {
            "_id": str(dataset._identity._id.value),
            "name": dataset._configuration._name.value,
            "kind": dataset._configuration._kind.value,
            "created_at": dataset._identity._audit._created.value.isoformat(),
            "updated_at": dataset._identity._audit._updated.value.isoformat(),
        }
        await self._collection.replace_one(
            {"_id": doc["_id"]}, doc, upsert=True
        )

    async def load(self, dataset_id: EntityId) -> Dataset | None:
        doc = await self._collection.find_one(
            {"_id": str(dataset_id.value)}
        )
        if doc is None:
            return None
        return self._doc_to_dataset(doc)

    async def delete(self, dataset_id: EntityId) -> None:
        await self._collection.delete_one(
            {"_id": str(dataset_id.value)}
        )

    async def find_all(self) -> Datasets:
        cursor = self._collection.find()
        docs = await cursor.to_list(length=1000)
        return Datasets([self._doc_to_dataset(doc) for doc in docs])

    def _doc_to_dataset(self, doc: dict) -> Dataset:
        from uuid import UUID
        from datetime import datetime
        from shared.domain.base import AuditRecord, CreatedAt, UpdatedAt
        from datasets.domain.value_objects import (
            DatasetName, DatasetKind, DatasetConfiguration, SchemaDefinition,
            StorageUri,
        )

        return Dataset(
            identity=DatasetIdentity(
                id=EntityId(UUID(doc["_id"])),
                audit=AuditRecord(
                    _created=CreatedAt(
                        datetime.fromisoformat(doc["created_at"])
                    ),
                    _updated=UpdatedAt(
                        datetime.fromisoformat(doc["updated_at"])
                    ),
                ),
            ),
            configuration=DatasetConfiguration(
                _name=DatasetName(doc["name"]),
                _kind=DatasetKind(doc["kind"]),
                _schema=SchemaDefinition(_columns=()),
                _location=StorageUri(""),
            ),
        )
