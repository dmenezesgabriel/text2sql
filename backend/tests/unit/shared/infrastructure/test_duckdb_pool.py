from __future__ import annotations

import pytest

from src.shared.infrastructure.duckdb_pool import DuckDBPool


class TestDuckDBPool:
    def setup_method(self) -> None:
        # Reset class-level singleton between tests
        DuckDBPool._connection = None

    def teardown_method(self) -> None:
        DuckDBPool._connection = None

    def test_connect_and_disconnect(self) -> None:
        pool = DuckDBPool(":memory:")
        pool.connect()
        assert DuckDBPool._connection is not None
        pool.disconnect()
        assert DuckDBPool._connection is None

    def test_connection_raises_when_not_connected(self) -> None:
        pool = DuckDBPool(":memory:")
        with pytest.raises(RuntimeError, match="not connected"), pool.connection():
            pass

    def test_connection_yields_connection_when_connected(self) -> None:
        pool = DuckDBPool(":memory:")
        pool.connect()
        with pool.connection() as conn:
            assert conn is not None
        pool.disconnect()

    def test_default_database_path_is_memory(self) -> None:
        pool = DuckDBPool()
        assert pool._database_path == ":memory:"

    def test_double_connect_is_idempotent(self) -> None:
        pool = DuckDBPool(":memory:")
        pool.connect()
        first = DuckDBPool._connection
        pool.connect()
        assert DuckDBPool._connection is first
        pool.disconnect()
