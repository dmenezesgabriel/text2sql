from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.shared.domain.base import ValueObject


class DatasetKind(Enum):
    TABLE = "table"
    FILE = "file"
    DATABASE = "database"


class FileFormat(Enum):
    CSV = "csv"
    PARQUET = "parquet"
    JSON = "json"


@dataclass(frozen=True)
class DatasetName(ValueObject):
    value: str


@dataclass(frozen=True)
class ColumnDefinition(ValueObject):
    _name: str
    _dtype: str
    _nullable: bool


@dataclass(frozen=True)
class SchemaDefinition(ValueObject):
    _columns: tuple[ColumnDefinition, ...]


@dataclass(frozen=True)
class StorageUri(ValueObject):
    value: str


@dataclass(frozen=True)
class ConnectionString(ValueObject):
    value: str
