from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException

from src.datasets.application.ports.i_dataset_repository import IDatasetRepository
from src.datasets.application.ports.i_query_engine import IQueryEngine
from src.datasets.application.use_cases.register_s3_dataset import (
    RegisterS3DatasetRequest,
    RegisterS3DatasetUseCase,
)
from src.datasets.domain.entities import Dataset
from src.datasets.domain.value_objects import DatasetName, StorageUri
from src.datasets.exceptions.duplicate_dataset_name_error import DuplicateDatasetNameError
from src.shared.domain.base import EntityId


def _dataset_to_dict(dataset: Dataset) -> dict:
    return {
        "id": str(dataset._identity._id.value),
        "name": dataset._configuration._name.value,
        "kind": dataset._configuration._kind.value,
        "location": dataset._configuration._location.value,
        "columns": [
            {"name": col._name, "dtype": col._dtype, "nullable": col._nullable}
            for col in dataset._configuration._schema._columns
        ],
    }


def create_datasets_router(
    register_use_case: RegisterS3DatasetUseCase,
    dataset_repo: IDatasetRepository,
    engine: IQueryEngine,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/datasets", tags=["datasets"])

    @router.get("")
    async def list_datasets():
        datasets = dataset_repo.find_all()
        return {"datasets": [_dataset_to_dict(ds) for ds in datasets.to_list()]}

    @router.post("/register-s3", status_code=201)
    async def register_s3_dataset(body: dict):
        name = body.get("name", "").strip()
        s3_uri = body.get("s3_uri", "").strip()
        if not name or not s3_uri:
            raise HTTPException(status_code=400, detail="'name' and 's3_uri' are required")
        try:
            dataset = await register_use_case.execute(
                RegisterS3DatasetRequest(
                    _name=DatasetName(name),
                    _s3_uri=StorageUri(s3_uri),
                ),
            )
            return _dataset_to_dict(dataset)
        except DuplicateDatasetNameError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @router.get("/{dataset_id}/preview")
    async def preview_dataset(dataset_id: str):
        try:
            uid = UUID(dataset_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid dataset id") from exc
        try:
            result = await engine.preview(EntityId(uid), limit=100)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        return {
            "columns": list(result._columns),
            "rows": [_make_serializable(row) for row in result._rows],
        }

    @router.delete("/{dataset_id}", status_code=204)
    async def delete_dataset(dataset_id: str):
        try:
            uid = UUID(dataset_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid dataset id") from exc
        dataset_repo.delete(EntityId(uid))

    return router


def _make_serializable(row: dict) -> dict:
    return {
        k: v if isinstance(v, (int, float, str, bool, type(None))) else str(v)
        for k, v in row.items()
    }
