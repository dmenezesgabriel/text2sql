from __future__ import annotations

import duckdb
from collections.abc import Generator
from contextlib import contextmanager


class DuckDBPool:
    _connection: duckdb.DuckDBPyConnection | None = None

    def __init__(self, database_path: str = ":memory:") -> None:
        self._database_path = database_path

    def connect(self) -> None:
        if DuckDBPool._connection is None:
            DuckDBPool._connection = duckdb.connect(self._database_path)

    def disconnect(self) -> None:
        if DuckDBPool._connection is not None:
            DuckDBPool._connection.close()
            DuckDBPool._connection = None

    @contextmanager
    def connection(self) -> Generator[duckdb.DuckDBPyConnection, None, None]:
        if DuckDBPool._connection is None:
            raise RuntimeError("DuckDB not connected. Call connect() first.")
        yield DuckDBPool._connection
