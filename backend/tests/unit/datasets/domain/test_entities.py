from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from src.datasets.domain.entities import Dataset, DatasetConfiguration, DatasetIdentity, Datasets
from src.datasets.domain.value_objects import (
    ColumnDefinition,
    DatasetKind,
    DatasetName,
    SchemaDefinition,
    StorageUri,
)
from src.shared.domain.base import AuditRecord, CreatedAt, EntityId, UpdatedAt


def _make_dataset(name: str = "test") -> Dataset:
    return Dataset(
        identity=DatasetIdentity(
            entity_id=EntityId(uuid4()),
            audit=AuditRecord(
                _created=CreatedAt(datetime.utcnow()),
                _updated=UpdatedAt(datetime.utcnow()),
            ),
        ),
        configuration=DatasetConfiguration(
            _name=DatasetName(name),
            _kind=DatasetKind.FILE,
            _schema=SchemaDefinition(_columns=()),
            _location=StorageUri("s3://bucket/file.parquet"),
        ),
    )


class TestDatasets:
    def test_add_and_find_by_name(self) -> None:
        dataset = _make_dataset("orders")
        datasets = Datasets()
        datasets.add(dataset)
        found = datasets.find_by_name(DatasetName("orders"))
        assert found is dataset

    def test_find_by_name_returns_none_when_missing(self) -> None:
        datasets = Datasets()
        assert datasets.find_by_name(DatasetName("missing")) is None

    def test_remove(self) -> None:
        dataset = _make_dataset("sales")
        datasets = Datasets([dataset])
        datasets.remove(dataset._identity._id)
        assert datasets.to_list() == []

    def test_to_list_returns_all(self) -> None:
        d1 = _make_dataset("a")
        d2 = _make_dataset("b")
        datasets = Datasets([d1, d2])
        assert len(datasets.to_list()) == 2


class TestDatasetConfiguration:
    def test_fields_stored(self) -> None:
        schema = SchemaDefinition(
            _columns=(ColumnDefinition(_name="id", _dtype="INTEGER", _nullable=False),),
        )
        config = DatasetConfiguration(
            _name=DatasetName("test"),
            _kind=DatasetKind.TABLE,
            _schema=schema,
            _location=StorageUri("s3://b/f.parquet"),
        )
        assert config._name == DatasetName("test")
        assert config._kind == DatasetKind.TABLE
