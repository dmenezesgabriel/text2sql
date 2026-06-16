from __future__ import annotations

from src.datasets.domain.entities import Dataset, Datasets
from src.datasets.domain.value_objects import SchemaDefinition
from src.shared.domain.base import EntityId


class FakeRegisterUseCase:
    async def execute(self, request: object) -> object:
        return None


class FakeDatasetRepository:
    def find_all(self) -> Datasets:
        return Datasets()

    def save(self, dataset: Dataset) -> None:
        pass

    def load(self, dataset_id: EntityId) -> Dataset | None:
        return None

    def delete(self, dataset_id: EntityId) -> None:
        pass


class FakeQueryEngine:
    async def execute(self, sql: str) -> object:
        return None

    async def create_view_from_s3(self, dataset_id: EntityId, s3_uri: str) -> SchemaDefinition:
        return SchemaDefinition(_columns=())

    async def preview(self, dataset_id: EntityId, limit: int) -> object:
        return None


class TestCreateDatasetsRouter:
    def test_router_is_created(self) -> None:
        from src.datasets.application.use_cases.register_s3_dataset import RegisterS3DatasetUseCase
        from src.datasets.infrastructure.fastapi.router import create_datasets_router

        repo = FakeDatasetRepository()
        engine = FakeQueryEngine()
        use_case = RegisterS3DatasetUseCase(datasets=repo, engine=engine)  # type: ignore[arg-type]
        router = create_datasets_router(
            register_use_case=use_case,
            dataset_repo=repo,  # type: ignore[arg-type]
            engine=engine,  # type: ignore[arg-type]
        )
        assert router is not None

    def test_router_prefix(self) -> None:
        from src.datasets.application.use_cases.register_s3_dataset import RegisterS3DatasetUseCase
        from src.datasets.infrastructure.fastapi.router import create_datasets_router

        repo = FakeDatasetRepository()
        engine = FakeQueryEngine()
        use_case = RegisterS3DatasetUseCase(datasets=repo, engine=engine)  # type: ignore[arg-type]
        router = create_datasets_router(
            register_use_case=use_case,
            dataset_repo=repo,  # type: ignore[arg-type]
            engine=engine,  # type: ignore[arg-type]
        )
        assert router.prefix == "/api/v1/datasets"
