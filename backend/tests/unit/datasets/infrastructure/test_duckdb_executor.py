from __future__ import annotations


class TestDuckDBExecutor:
    def test_module_imports(self) -> None:
        from src.datasets.infrastructure.duckdb_executor import DuckDBExecutor

        assert DuckDBExecutor is not None

    def test_instantiate_with_fake_pool(self) -> None:
        from src.datasets.infrastructure.duckdb_executor import DuckDBExecutor

        class FakeDuckDBPool:
            pass

        executor = DuckDBExecutor(pool=FakeDuckDBPool())  # type: ignore[arg-type]
        assert executor is not None
        assert executor._pool is not None
