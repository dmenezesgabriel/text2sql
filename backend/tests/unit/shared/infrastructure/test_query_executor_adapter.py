from __future__ import annotations


class TestQueryExecutorAdapter:
    def test_module_imports(self) -> None:
        import src.shared.infrastructure.query_executor_adapter as module

        assert module is not None
