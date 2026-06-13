from __future__ import annotations

from fastapi import APIRouter

from src.dashboards.application.use_cases.apply_cross_filter import (
    ApplyCrossFilterUseCase,
)
from src.dashboards.application.use_cases.compose_dashboard import (
    ComposeDashboardFromQuestionsUseCase,
)


def create_dashboards_router(
    filter_use_case: ApplyCrossFilterUseCase | None = None,
    compose_use_case: ComposeDashboardFromQuestionsUseCase | None = None,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/dashboards", tags=["dashboards"])

    @router.get("")
    async def list_dashboards():
        return {"dashboards": []}

    @router.post("")
    async def create_dashboard(body: dict):
        return {"status": "created"}

    @router.get("/{dashboard_id}")
    async def get_dashboard(dashboard_id: str):
        return {"id": dashboard_id}

    @router.post("/{dashboard_id}/filter")
    async def filter_dashboard(dashboard_id: str, body: dict):
        return {"status": "filtered"}

    @router.delete("/{dashboard_id}")
    async def delete_dashboard(dashboard_id: str):
        return {"status": "deleted"}

    return router
