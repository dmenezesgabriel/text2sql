from __future__ import annotations

from src.datasets.domain.value_objects import (
    ColumnDefinition,
    ConnectionString,
    DatasetKind,
    DatasetName,
    FileFormat,
    SchemaDefinition,
    StorageUri,
)


class TestDatasetKind:
    def test_all_variants(self) -> None:
        assert DatasetKind.TABLE.value == "table"
        assert DatasetKind.FILE.value == "file"
        assert DatasetKind.DATABASE.value == "database"


class TestFileFormat:
    def test_all_variants(self) -> None:
        assert FileFormat.CSV.value == "csv"
        assert FileFormat.PARQUET.value == "parquet"
        assert FileFormat.JSON.value == "json"


class TestDatasetName:
    def test_value_stored(self) -> None:
        name = DatasetName("my_dataset")
        assert name.value == "my_dataset"

    def test_equality(self) -> None:
        assert DatasetName("x") == DatasetName("x")
        assert DatasetName("x") != DatasetName("y")


class TestColumnDefinition:
    def test_fields_stored(self) -> None:
        col = ColumnDefinition(_name="age", _dtype="INTEGER", _nullable=False)
        assert col._name == "age"
        assert col._dtype == "INTEGER"
        assert col._nullable is False


class TestSchemaDefinition:
    def test_empty_columns(self) -> None:
        schema = SchemaDefinition(_columns=())
        assert schema._columns == ()

    def test_with_columns(self) -> None:
        col = ColumnDefinition(_name="id", _dtype="UUID", _nullable=False)
        schema = SchemaDefinition(_columns=(col,))
        assert len(schema._columns) == 1


class TestStorageUri:
    def test_value_stored(self) -> None:
        uri = StorageUri("s3://bucket/file.parquet")
        assert uri.value == "s3://bucket/file.parquet"


class TestConnectionString:
    def test_value_stored(self) -> None:
        conn = ConnectionString("postgresql://localhost/db")
        assert conn.value == "postgresql://localhost/db"
