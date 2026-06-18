from __future__ import annotations

import json
import uuid as _uuid
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from moto import mock_aws

from src.datasets.domain.value_objects import DatasetKind
from src.datasets.infrastructure.dynamo_repository import DynamoDatasetRepository
from src.shared.domain.base import EntityId
from src.shared.infrastructure.dynamo_models import BaseModel, DatasetModel


@pytest.fixture(autouse=True)
def dynamo_table():  # type: ignore[return]
    with mock_aws():
        original_host = BaseModel.Meta.host
        BaseModel.Meta.host = None
        if hasattr(DatasetModel, "_connection"):
            DatasetModel._connection = None  # type: ignore[attr-defined]
        DatasetModel.create_table(billing_mode="PAY_PER_REQUEST", wait=True)
        yield
        BaseModel.Meta.host = original_host
        if hasattr(DatasetModel, "_connection"):
            DatasetModel._connection = None  # type: ignore[attr-defined]


def _save_model(
    *,
    name: str = "sales",
    kind: str = "file",
    location: str | None = "s3://bucket/sales.parquet",
    schema: list[dict] | None = None,
) -> str:
    uid = str(uuid4())
    now = datetime.now(UTC).isoformat()
    raw = (
        schema if schema is not None else [{"name": "col1", "dtype": "VARCHAR", "nullable": False}]
    )
    DatasetModel(
        id=uid,
        name=name,
        kind=kind,
        schema=json.dumps(raw),
        location=location,
        created_at=now,
        updated_at=now,
    ).save()
    return uid


class TestDynamoDatasetRepositoryModule:
    def test_module_imports(self) -> None:
        assert DynamoDatasetRepository is not None

    def test_class_is_instantiable(self) -> None:
        assert DynamoDatasetRepository() is not None


class TestDynamoDatasetRepositoryLoad:
    def test_load_returns_none_when_not_found(self) -> None:
        assert DynamoDatasetRepository().load(EntityId(uuid4())) is None

    def test_load_identity_is_not_none(self) -> None:
        uid = _save_model()
        dataset = DynamoDatasetRepository().load(EntityId(_uuid.UUID(uid)))
        assert dataset is not None
        assert dataset._identity is not None

    def test_load_identity_id_matches_stored_uuid(self) -> None:
        uid = _save_model()
        dataset = DynamoDatasetRepository().load(EntityId(_uuid.UUID(uid)))
        assert dataset is not None
        assert str(dataset._identity._id.value) == uid

    def test_load_identity_audit_created_is_not_none(self) -> None:
        uid = _save_model()
        dataset = DynamoDatasetRepository().load(EntityId(_uuid.UUID(uid)))
        assert dataset is not None
        assert dataset._identity._audit is not None
        assert dataset._identity._audit._created is not None

    def test_load_identity_audit_updated_is_not_none(self) -> None:
        uid = _save_model()
        dataset = DynamoDatasetRepository().load(EntityId(_uuid.UUID(uid)))
        assert dataset is not None
        assert dataset._identity._audit._updated is not None

    def test_load_kind_is_not_none_and_correct(self) -> None:
        uid = _save_model(kind="file")
        dataset = DynamoDatasetRepository().load(EntityId(_uuid.UUID(uid)))
        assert dataset is not None
        assert dataset._configuration._kind is not None
        assert dataset._configuration._kind == DatasetKind.FILE

    def test_load_location_matches_stored_uri(self) -> None:
        uid = _save_model(location="s3://my-bucket/data.parquet")
        dataset = DynamoDatasetRepository().load(EntityId(_uuid.UUID(uid)))
        assert dataset is not None
        assert dataset._configuration._location.value == "s3://my-bucket/data.parquet"

    def test_load_columns_tuple_is_not_none(self) -> None:
        uid = _save_model(schema=[{"name": "region", "dtype": "VARCHAR", "nullable": False}])
        dataset = DynamoDatasetRepository().load(EntityId(_uuid.UUID(uid)))
        assert dataset is not None
        assert dataset._configuration._schema._columns is not None
        assert len(dataset._configuration._schema._columns) == 1

    def test_load_column_nullable_field_preserved(self) -> None:
        uid = _save_model(schema=[{"name": "amt", "dtype": "BIGINT", "nullable": True}])
        dataset = DynamoDatasetRepository().load(EntityId(_uuid.UUID(uid)))
        assert dataset is not None
        col = dataset._configuration._schema._columns[0]
        assert col._nullable is True


class TestDynamoDatasetRepositoryFindAll:
    def test_find_all_returns_all_datasets(self) -> None:
        _save_model(name="a")
        _save_model(name="b")
        result = DynamoDatasetRepository().find_all()
        assert len(result.to_list()) == 2

    def test_find_all_datasets_have_non_none_identity(self) -> None:
        _save_model()
        datasets = DynamoDatasetRepository().find_all().to_list()
        for ds in datasets:
            assert ds._identity is not None
            assert ds._identity._id is not None


class TestDynamoDatasetRepositoryDocToDataset:
    def test_load_created_value_is_utc_aware(self) -> None:
        # Kills mutmut_32: _created=CreatedAt(None) instead of CreatedAt(datetime.fromisoformat(...))
        uid = _save_model()
        dataset = DynamoDatasetRepository().load(EntityId(_uuid.UUID(uid)))
        assert dataset is not None
        assert dataset._identity._audit._created.value is not None
        assert dataset._identity._audit._created.value.tzinfo is not None

    def test_load_updated_value_is_utc_aware(self) -> None:
        # Kills mutmut_34: _updated=UpdatedAt(None) instead of UpdatedAt(datetime.fromisoformat(...))
        uid = _save_model()
        dataset = DynamoDatasetRepository().load(EntityId(_uuid.UUID(uid)))
        assert dataset is not None
        assert dataset._identity._audit._updated.value is not None
        assert dataset._identity._audit._updated.value.tzinfo is not None

    def test_load_columns_empty_when_schema_is_null(self) -> None:
        # Kills mutmut_1: cols=None instead of cols=() when model.schema is falsy
        uid = str(uuid4())
        now = datetime.now(UTC).isoformat()
        DatasetModel(
            id=uid,
            name="no_schema",
            kind="file",
            schema=None,
            location="s3://bucket/f.parquet",
            created_at=now,
            updated_at=now,
        ).save()
        dataset = DynamoDatasetRepository().load(EntityId(_uuid.UUID(uid)))
        assert dataset is not None
        assert dataset._configuration._schema._columns == ()
