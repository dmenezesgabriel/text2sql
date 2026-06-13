from __future__ import annotations

from fastapi import APIRouter

from src.datasets.application.use_cases.ingest_file import IngestFileUseCase


def create_datasets_router(
    ingest_use_case: IngestFileUseCase | None = None,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/datasets", tags=["datasets"])

    @router.get("")
    async def list_datasets():
        return {"datasets": []}

    @router.post("")
    async def register_dataset(body: dict):
        return {"status": "registered"}

    @router.post("/ingest")
    async def ingest_file(body: dict):
        return {"status": "ingesting"}

    @router.get("/{dataset_id}/preview")
    async def preview_dataset(dataset_id: str):
        return {"id": dataset_id}

    @router.delete("/{dataset_id}")
    async def delete_dataset(dataset_id: str):
        return {"status": "deleted"}

    return router
