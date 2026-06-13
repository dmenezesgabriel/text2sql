from __future__ import annotations

from collections.abc import AsyncIterator

from src.datasets.application.use_cases.ingest_file import IngestFileRequest, IngestFileUseCase
from src.datasets.domain.entities import Dataset, Datasets
from src.datasets.domain.value_objects import (
    ColumnDefinition,
    DatasetName,
    FileFormat,
    SchemaDefinition,
    StorageUri,
)
from src.shared.domain.base import EntityId


class FakeDatasetRepository:
    def __init__(self, existing: list[Dataset] | None = None) -> None:
        self._datasets: list[Dataset] = existing or []

    def find_all(self) -> Datasets:
        return Datasets(list(self._datasets))

    def save(self, dataset: Dataset) -> None:
        self._datasets.append(dataset)

    def load(self, dataset_id: EntityId) -> Dataset | None:
        return next((d for d in self._datasets if d._identity._id == dataset_id), None)

    def delete(self, dataset_id: EntityId) -> None:
        self._datasets = [d for d in self._datasets if d._identity._id != dataset_id]


class FakeStorageIngestion:
    def __init__(self, columns: list[ColumnDefinition]) -> None:
        self._columns = columns

    async def ingest(
        self,
        uri: StorageUri,
        file_format: FileFormat,
    ) -> AsyncIterator[ColumnDefinition]:
        for col in self._columns:
            yield col


class FakeQueryEngine:
    def __init__(self) -> None:
        self.registered: list[EntityId] = []

    async def register_schema(self, dataset_id: EntityId, schema: SchemaDefinition) -> None:
        self.registered.append(dataset_id)

    async def create_view_from_s3(self, dataset_id: EntityId, s3_uri: str) -> SchemaDefinition:
        return SchemaDefinition(_columns=())

    async def execute(self, sql: str) -> object:
        return None

    async def preview(self, dataset_id: EntityId, limit: int) -> object:
        return None


class TestIngestFileUseCase:
    def setup_method(self) -> None:
        self.columns = [
            ColumnDefinition(_name="id", _dtype="INTEGER", _nullable=False),
            ColumnDefinition(_name="name", _dtype="VARCHAR", _nullable=True),
        ]
        self.repo = FakeDatasetRepository()
        self.storage = FakeStorageIngestion(self.columns)
        self.engine = FakeQueryEngine()
        self.use_case = IngestFileUseCase(
            datasets=self.repo,
            storage=self.storage,
            engine=self.engine,
        )

    async def test_ingests_parquet_file(self) -> None:
        request = IngestFileRequest(
            _name=DatasetName("sales"),
            _uri=StorageUri("s3://bucket/sales.parquet"),
            _format=FileFormat.PARQUET,
        )
        dataset = await self.use_case.execute(request)
        assert dataset._configuration._name == DatasetName("sales")
        assert len(self.repo.find_all().to_list()) == 1

    async def test_registers_schema_with_engine(self) -> None:
        request = IngestFileRequest(
            _name=DatasetName("orders"),
            _uri=StorageUri("s3://bucket/orders.parquet"),
            _format=FileFormat.PARQUET,
        )
        dataset = await self.use_case.execute(request)
        assert dataset._identity._id in self.engine.registered

    async def test_rejects_unsupported_format(self) -> None:
        import pytest

        request = IngestFileRequest(
            _name=DatasetName("data"),
            _uri=StorageUri("s3://bucket/data.json"),
            _format=FileFormat.JSON,
        )
        with pytest.raises(Exception):
            await self.use_case.execute(request)

    async def test_rejects_duplicate_name(self) -> None:
        import pytest

        request = IngestFileRequest(
            _name=DatasetName("sales"),
            _uri=StorageUri("s3://bucket/sales.parquet"),
            _format=FileFormat.PARQUET,
        )
        await self.use_case.execute(request)
        with pytest.raises(Exception):
            await self.use_case.execute(request)
