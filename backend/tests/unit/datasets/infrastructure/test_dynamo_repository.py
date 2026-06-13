from __future__ import annotations


class TestDynamoDatasetRepository:
    def test_module_imports(self) -> None:
        from src.datasets.infrastructure.dynamo_repository import DynamoDatasetRepository

        assert DynamoDatasetRepository is not None

    def test_class_is_instantiable(self) -> None:
        from src.datasets.infrastructure.dynamo_repository import DynamoDatasetRepository

        repo = DynamoDatasetRepository()
        assert repo is not None
