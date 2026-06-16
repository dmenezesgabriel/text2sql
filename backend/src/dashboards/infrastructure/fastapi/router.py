from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.dashboards.application.ports.i_dashboard_repository import IDashboardRepository
from src.dashboards.application.use_cases.apply_cross_filter import (
    ApplyCrossFilterUseCase,
    CrossFilterRequest,
)
from src.dashboards.application.use_cases.compose_dashboard import (
    ComposeDashboardFromQuestionsUseCase,
    ComposeDashboardRequest,
)
from src.dashboards.domain.entities import Dashboard
from src.dashboards.domain.value_objects import DashboardTitle
from src.dashboards.exceptions.dashboard_not_found_error import DashboardNotFoundError
from src.shared.domain.base import EntityId


def _dashboard_to_dict(d: Dashboard) -> dict[str, object]:
    tiles = [
        {
            "id": str(t._identity._id.value),
            "questionId": str(t._source._identity._id.value),
            "position": {
                "row": t._identity._position._row,
                "col": t._identity._position._col,
                "width": t._identity._position._width,
                "height": t._identity._position._height,
            },
        }
        for t in d._layout._tiles.to_list()
    ]
    filters = [
        {
            "sourceTileId": str(source_id.value),
            "column": b._column,
            "targetTileIds": [str(tid.value) for tid in b._target_tiles],
        }
        for source_id, bindings in d._layout._filters.items()
        for b in bindings
    ]
    return {
        "id": str(d._identity._id.value),
        "title": d._layout._title.value,
        "tiles": tiles,
        "filters": filters,
        "createdAt": d._identity._audit._created.value.isoformat(),
        "updatedAt": d._identity._audit._updated.value.isoformat(),
    }


def _build_compose_request(body: dict[str, object]) -> ComposeDashboardRequest:
    title = DashboardTitle(str(body.get("title", "Untitled dashboard")))
    raw_ids = body.get("question_ids") or []
    question_ids = [
        EntityId(UUID(str(qid))) for qid in (raw_ids if isinstance(raw_ids, list) else [])
    ]
    return ComposeDashboardRequest(
        _title=title,
        _question_ids=question_ids,
        _auto_bind_filters=bool(body.get("auto_bind_filters", False)),
    )


def _load_or_404(
    dashboard_repo: IDashboardRepository,
    dashboard_id: str,
) -> Dashboard | JSONResponse:
    try:
        entity_id = EntityId(UUID(dashboard_id))
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={"error": f"Invalid dashboard ID: {dashboard_id!r}"},
        )
    dashboard = dashboard_repo.load(entity_id)
    if dashboard is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Dashboard {dashboard_id!r} not found"},
        )
    return dashboard


async def _apply_filter(
    filter_use_case: ApplyCrossFilterUseCase,
    dashboard_id: str,
    body: dict[str, object],
) -> dict[str, object]:
    column = str(body.get("column", "")).strip()
    value = str(body.get("value", "")).strip()
    if not column or not value:
        msg = "'column' and 'value' are required"
        raise ValueError(msg)
    result = await filter_use_case.execute(
        CrossFilterRequest(
            _dashboard_id=EntityId(UUID(dashboard_id)),
            _source_tile_id=EntityId(UUID(str(body.get("source_tile", "")))),
            _column=column,
            _value=value,
        ),
    )
    return {
        "sourceTile": str(result._source_tile.value),
        "column": result._filter_column,
        "value": result._filter_value,
        "tileResults": {
            str(tid.value): {
                "columns": list(qr._columns),
                "rows": [dict(r) for r in qr._rows],
            }
            for tid, qr in result._tile_results.items()
        },
    }


def create_dashboards_router(
    dashboard_repo: IDashboardRepository,
    compose_use_case: ComposeDashboardFromQuestionsUseCase,
    filter_use_case: ApplyCrossFilterUseCase,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/dashboards", tags=["dashboards"])

    @router.get("")
    async def list_dashboards():
        return {"dashboards": [_dashboard_to_dict(d) for d in dashboard_repo.find_all()]}

    @router.post("")
    async def create_dashboard(body: dict[str, object]):
        try:
            request = _build_compose_request(body)
            dashboard = compose_use_case.execute(request)
        except (ValueError, KeyError) as exc:
            return JSONResponse(status_code=400, content={"error": str(exc)})
        except Exception as exc:
            return JSONResponse(status_code=500, content={"error": str(exc)})
        return _dashboard_to_dict(dashboard)

    @router.get("/{dashboard_id}")
    async def get_dashboard(dashboard_id: str):
        result = _load_or_404(dashboard_repo, dashboard_id)
        if isinstance(result, JSONResponse):
            return result
        return _dashboard_to_dict(result)

    @router.delete("/{dashboard_id}")
    async def delete_dashboard(dashboard_id: str):
        try:
            entity_id = EntityId(UUID(dashboard_id))
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid dashboard ID: {dashboard_id!r}"},
            )
        dashboard_repo.delete(entity_id)
        return {"status": "deleted"}

    @router.post("/{dashboard_id}/filter")
    async def filter_dashboard(dashboard_id: str, body: dict[str, object]):
        try:
            result = await _apply_filter(filter_use_case, dashboard_id, body)
        except (ValueError, KeyError, DashboardNotFoundError) as exc:
            status = 404 if isinstance(exc, DashboardNotFoundError) else 400
            return JSONResponse(status_code=status, content={"error": str(exc)})
        return result

    return router
