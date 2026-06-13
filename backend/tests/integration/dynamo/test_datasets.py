from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from pytest_bdd import given, parsers, scenarios, then, when

from src.datasets.domain.entities import Dataset, DatasetConfiguration, DatasetIdentity
from src.datasets.domain.value_objects import (
    ColumnDefinition,
    DatasetKind,
    DatasetName,
    SchemaDefinition,
    StorageUri,
)
from src.datasets.infrastructure.dynamo_repository import DynamoDatasetRepository
from src.shared.domain.base import AuditRecord, CreatedAt, EntityId, UpdatedAt

scenarios("features/datasets.feature")


# ── helpers ──────────────────────────────────────────────────────────────────


def _make_dataset(
    name: str = "test",
    kind: DatasetKind = DatasetKind.TABLE,
    location: str = "s3://bucket/test.parquet",
    columns: tuple[ColumnDefinition, ...] = (),
) -> Dataset:
    now = datetime.now(UTC)
    return Dataset(
        identity=DatasetIdentity(
            entity_id=EntityId(uuid4()),
            audit=AuditRecord(_created=CreatedAt(now), _updated=UpdatedAt(now)),
        ),
        configuration=DatasetConfiguration(
            _name=DatasetName(name),
            _kind=kind,
            _schema=SchemaDefinition(_columns=columns),
            _location=StorageUri(location),
        ),
    )


# ── given ─────────────────────────────────────────────────────────────────────


@given(parsers.parse('a dataset named "{name}" of kind TABLE at "{location}"'))
def dataset_with_name_and_location(ctx: dict, name: str, location: str) -> None:
    ctx["dataset"] = _make_dataset(name=name, location=location)


@given(parsers.parse('a dataset with a column "{col_name}" of type "{col_type}"'))
def dataset_with_column(ctx: dict, col_name: str, col_type: str) -> None:
    col = ColumnDefinition(_name=col_name, _dtype=col_type, _nullable=False)
    ctx["dataset"] = _make_dataset(columns=(col,))


@given("a saved dataset")
def a_saved_dataset(ctx: dict, dataset_repo: DynamoDatasetRepository) -> None:
    dataset = _make_dataset()
    dataset_repo.save(dataset)
    ctx["dataset"] = dataset


@given(parsers.parse("{count:d} saved datasets"))
def n_saved_datasets(ctx: dict, count: int, dataset_repo: DynamoDatasetRepository) -> None:
    datasets = [_make_dataset(name=f"ds_{i}") for i in range(count)]
    for d in datasets:
        dataset_repo.save(d)
    ctx["datasets"] = datasets


# ── when ──────────────────────────────────────────────────────────────────────


@when("the dataset is saved")
def save_dataset(ctx: dict, dataset_repo: DynamoDatasetRepository) -> None:
    dataset_repo.save(ctx["dataset"])


@when("the dataset is reloaded by its ID")
def reload_dataset(ctx: dict, dataset_repo: DynamoDatasetRepository) -> None:
    ctx["reloaded"] = dataset_repo.load(ctx["dataset"]._identity._id)


@when("a random dataset ID is loaded")
def load_missing_dataset(ctx: dict, dataset_repo: DynamoDatasetRepository) -> None:
    ctx["reloaded"] = dataset_repo.load(EntityId(uuid4()))


@when("the dataset is deleted")
def delete_dataset(ctx: dict, dataset_repo: DynamoDatasetRepository) -> None:
    dataset_repo.delete(ctx["dataset"]._identity._id)


@when("all datasets are listed")
def list_all_datasets(ctx: dict, dataset_repo: DynamoDatasetRepository) -> None:
    ctx["all_results"] = dataset_repo.find_all()


# ── then ──────────────────────────────────────────────────────────────────────


@then(parsers.parse('the reloaded dataset name is "{name}"'))
def check_dataset_name(ctx: dict, name: str) -> None:
    assert ctx["reloaded"]._configuration._name.value == name


@then(parsers.parse('the reloaded dataset location is "{location}"'))
def check_dataset_location(ctx: dict, location: str) -> None:
    assert ctx["reloaded"]._configuration._location.value == location


@then(parsers.parse("the reloaded schema has {count:d} column"))
def check_schema_column_count(ctx: dict, count: int) -> None:
    assert len(ctx["reloaded"]._configuration._schema._columns) == count


@then(parsers.parse('the first column is "{col_name}" of type "{col_type}"'))
def check_first_column(ctx: dict, col_name: str, col_type: str) -> None:
    col = ctx["reloaded"]._configuration._schema._columns[0]
    assert col._name == col_name
    assert col._dtype == col_type


@then("the dataset result is None")
def check_dataset_none(ctx: dict) -> None:
    assert ctx["reloaded"] is None


@then(parsers.parse("{count:d} datasets are returned"))
def check_dataset_count(ctx: dict, count: int) -> None:
    assert len(ctx["all_results"].to_list()) == count
