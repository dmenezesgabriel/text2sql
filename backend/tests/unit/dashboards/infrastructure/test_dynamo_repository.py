from __future__ import annotations


class TestDynamoDashboardRepository:
    def test_module_imports(self) -> None:
        from src.dashboards.infrastructure.dynamo_repository import DynamoDashboardRepository

        assert DynamoDashboardRepository is not None

    def test_class_is_instantiable(self) -> None:
        from src.dashboards.infrastructure.dynamo_repository import DynamoDashboardRepository

        repo = DynamoDashboardRepository()
        assert repo is not None
