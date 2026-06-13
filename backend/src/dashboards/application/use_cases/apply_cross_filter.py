from __future__ import annotations

from dataclasses import dataclass

from src.agent.domain.value_objects import QueryResult
from src.dashboards.application.ports.i_dashboard_repository import (
    IDashboardRepository,
)
from src.dashboards.application.ports.i_query_executor import IQueryExecutor
from src.dashboards.exceptions.dashboard_not_found_error import (
    DashboardNotFoundError,
)
from src.shared.domain.base import EntityId


@dataclass(frozen=True)
class CrossFilterRequest:
    _dashboard_id: EntityId
    _source_tile_id: EntityId
    _column: str
    _value: str


@dataclass(frozen=True)
class CrossFilterResult:
    _source_tile: EntityId
    _filter_column: str
    _filter_value: str
    _tile_results: dict[EntityId, QueryResult]


class ApplyCrossFilterUseCase:
    def __init__(
        self,
        dashboards: IDashboardRepository,
        executor: IQueryExecutor,
    ) -> None:
        self._dashboards = dashboards
        self._executor = executor

    async def execute(
        self,
        request: CrossFilterRequest,
    ) -> CrossFilterResult:
        dashboard = self._dashboards.load(request._dashboard_id)
        if dashboard is None:
            msg = f"Dashboard {request._dashboard_id.value} not found"
            raise DashboardNotFoundError(msg)

        affected = dashboard._layout.tiles_affected_by(
            source_tile_id=request._source_tile_id,
            column=request._column,
        )

        results: dict[EntityId, QueryResult] = {}
        for tile in affected:
            query = tile._source._specification._description._query
            filtered = query.with_filter(
                column=request._column,
                operator="=",
                value=request._value,
            )
            results[tile._identity._id] = await self._executor.execute(
                sql=filtered._sql,
                dataset_id=query._source._id,
            )

        return CrossFilterResult(
            _source_tile=request._source_tile_id,
            _filter_column=request._column,
            _filter_value=request._value,
            _tile_results=results,
        )
