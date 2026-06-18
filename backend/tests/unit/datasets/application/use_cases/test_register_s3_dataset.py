from __future__ import annotations

import uuid

import pytest

from src.datasets.application.use_cases.register_s3_dataset import (
    RegisterS3DatasetRequest,
    RegisterS3DatasetUseCase,
)
from src.datasets.domain.entities import Dataset, Datasets
from src.datasets.domain.value_objects import DatasetKind, DatasetName, SchemaDefinition, StorageUri
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
    def __init__(self) -> None:
        self.last_dataset_id: EntityId | None = None
        self.last_s3_uri: str | None = None

    async def create_view_from_s3(self, dataset_id: EntityId, s3_uri: str) -> SchemaDefinition:
        self.last_dataset_id = dataset_id
        self.last_s3_uri = s3_uri
        return SchemaDefinition(_columns=())

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

    async def test_duplicate_error_message_contains_name(self) -> None:
        request = RegisterS3DatasetRequest(
            _name=DatasetName("my_dataset"),
            _s3_uri=StorageUri("s3://bucket/data.parquet"),
        )
        await self.use_case.execute(request)
        with pytest.raises(DuplicateDatasetNameError) as exc:
            await self.use_case.execute(request)
        assert "my_dataset" in str(exc.value)

    async def test_saved_dataset_identity_is_not_none(self) -> None:
        request = RegisterS3DatasetRequest(
            _name=DatasetName("orders"),
            _s3_uri=StorageUri("s3://bucket/orders.parquet"),
        )
        await self.use_case.execute(request)
        saved = self.repo._datasets[-1]
        assert saved._identity is not None
        assert saved._identity._id is not None
        assert isinstance(saved._identity._id.value, uuid.UUID)

    async def test_saved_dataset_identity_audit_is_not_none(self) -> None:
        request = RegisterS3DatasetRequest(
            _name=DatasetName("orders"),
            _s3_uri=StorageUri("s3://bucket/orders.parquet"),
        )
        await self.use_case.execute(request)
        saved = self.repo._datasets[-1]
        assert saved._identity._audit is not None
        assert saved._identity._audit._created is not None
        assert saved._identity._audit._updated is not None

    async def test_engine_called_with_correct_s3_uri(self) -> None:
        request = RegisterS3DatasetRequest(
            _name=DatasetName("sales"),
            _s3_uri=StorageUri("s3://bucket/sales.parquet"),
        )
        await self.use_case.execute(request)
        assert self.engine.last_s3_uri == "s3://bucket/sales.parquet"

    async def test_engine_called_with_valid_non_none_dataset_id(self) -> None:
        request = RegisterS3DatasetRequest(
            _name=DatasetName("sales"),
            _s3_uri=StorageUri("s3://bucket/sales.parquet"),
        )
        await self.use_case.execute(request)
        assert self.engine.last_dataset_id is not None
        assert isinstance(self.engine.last_dataset_id.value, uuid.UUID)

    async def test_saved_dataset_kind_is_file(self) -> None:
        request = RegisterS3DatasetRequest(
            _name=DatasetName("sales"),
            _s3_uri=StorageUri("s3://bucket/sales.parquet"),
        )
        await self.use_case.execute(request)
        saved = self.repo._datasets[-1]
        assert saved._configuration._kind == DatasetKind.FILE

    async def test_saved_dataset_location_matches_s3_uri(self) -> None:
        request = RegisterS3DatasetRequest(
            _name=DatasetName("sales"),
            _s3_uri=StorageUri("s3://bucket/sales.parquet"),
        )
        await self.use_case.execute(request)
        saved = self.repo._datasets[-1]
        assert saved._configuration._location.value == "s3://bucket/sales.parquet"

    async def test_saved_dataset_schema_is_not_none(self) -> None:
        request = RegisterS3DatasetRequest(
            _name=DatasetName("sales"),
            _s3_uri=StorageUri("s3://bucket/sales.parquet"),
        )
        await self.use_case.execute(request)
        saved = self.repo._datasets[-1]
        assert saved._configuration._schema is not None

    async def test_saved_dataset_created_is_utc_aware(self) -> None:
        # Kills mutmut_11 (now=None), mutmut_12 (now=datetime.now(None)), mutmut_26 (_created=CreatedAt(None))
        request = RegisterS3DatasetRequest(
            _name=DatasetName("audit_test"),
            _s3_uri=StorageUri("s3://bucket/audit.parquet"),
        )
        dataset = await self.use_case.execute(request)
        created = dataset._identity._audit._created.value
        assert created is not None
        assert created.tzinfo is not None

    async def test_saved_dataset_updated_is_utc_aware(self) -> None:
        # Kills mutmut_11 (now=None), mutmut_12 (now=datetime.now(None)), mutmut_27 (_updated=UpdatedAt(None))
        request = RegisterS3DatasetRequest(
            _name=DatasetName("audit_test2"),
            _s3_uri=StorageUri("s3://bucket/audit2.parquet"),
        )
        dataset = await self.use_case.execute(request)
        updated = dataset._identity._audit._updated.value
        assert updated is not None
        assert updated.tzinfo is not None
