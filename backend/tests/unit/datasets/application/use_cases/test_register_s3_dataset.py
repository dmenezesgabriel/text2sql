from __future__ import annotations

import pytest

from src.datasets.application.use_cases.register_s3_dataset import (
    RegisterS3DatasetRequest,
    RegisterS3DatasetUseCase,
)
from src.datasets.domain.entities import Dataset, Datasets
from src.datasets.domain.value_objects import DatasetName, SchemaDefinition, StorageUri
from src.datasets.exceptions.duplicate_dataset_name_error import DuplicateDatasetNameError
from src.shared.domain.base import EntityId


class FakeDatasetRepository:
    def __init__(self, datasets: list[Dataset] | None = None) -> None:
        self._datasets: list[Dataset] = datasets or []

    def find_all(self) -> Datasets:
        return Datasets(list(self._datasets))

    def save(self, dataset: Dataset) -> None:
        self._datasets.append(dataset)

    def load(self, dataset_id: EntityId) -> Dataset | None:
        return next((d for d in self._datasets if d._identity._id == dataset_id), None)

    def delete(self, dataset_id: EntityId) -> None:
        self._datasets = [d for d in self._datasets if d._identity._id != dataset_id]


class FakeQueryEngine:
    async def create_view_from_s3(self, dataset_id: EntityId, s3_uri: str) -> SchemaDefinition:
        return SchemaDefinition(_columns=())

    async def register_schema(self, dataset_id: EntityId, schema: SchemaDefinition) -> None:
        pass

    async def execute(self, sql: str) -> object:
        return None

    async def preview(self, dataset_id: EntityId, limit: int) -> object:
        return None


class TestRegisterS3DatasetUseCase:
    def setup_method(self) -> None:
        self.repo = FakeDatasetRepository()
        self.engine = FakeQueryEngine()
        self.use_case = RegisterS3DatasetUseCase(datasets=self.repo, engine=self.engine)

    async def test_registers_dataset_successfully(self) -> None:
        request = RegisterS3DatasetRequest(
            _name=DatasetName("orders"),
            _s3_uri=StorageUri("s3://bucket/orders.parquet"),
        )
        dataset = await self.use_case.execute(request)
        assert dataset._configuration._name == DatasetName("orders")
        assert len(self.repo.find_all().to_list()) == 1

    async def test_raises_on_duplicate_name(self) -> None:
        request = RegisterS3DatasetRequest(
            _name=DatasetName("sales"),
            _s3_uri=StorageUri("s3://bucket/sales.parquet"),
        )
        await self.use_case.execute(request)
        with pytest.raises(DuplicateDatasetNameError):
            await self.use_case.execute(request)
