from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

import duckdb


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

    def configure_s3(self, endpoint: str, key: str, secret: str, use_ssl: bool = False) -> None:  # noqa: PLR0913
        host = endpoint.replace("https://", "").replace("http://", "")
        with self.connection() as conn:
            conn.execute("LOAD httpfs;")
            conn.execute(f"SET s3_endpoint = '{host}';")
            conn.execute(f"SET s3_access_key_id = '{key}';")
            conn.execute(f"SET s3_secret_access_key = '{secret}';")
            conn.execute(f"SET s3_use_ssl = {str(use_ssl).lower()};")
            conn.execute("SET s3_url_style = 'path';")

    @contextmanager
    def connection(self) -> Generator[duckdb.DuckDBPyConnection, None, None]:
        if DuckDBPool._connection is None:
            msg = "DuckDB not connected. Call connect() first."
            raise RuntimeError(msg)
        yield DuckDBPool._connection
