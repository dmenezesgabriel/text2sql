from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.dashboards.application.use_cases.apply_cross_filter import (
    ApplyCrossFilterUseCase,
    CrossFilterRequest,
)
from src.dashboards.domain.entities import Dashboard, DashboardIdentity, DashboardLayout, Tiles
from src.dashboards.domain.value_objects import DashboardTitle
from src.dashboards.exceptions.dashboard_not_found_error import DashboardNotFoundError
from src.shared.domain.base import AuditRecord, CreatedAt, EntityId, QueryResult, UpdatedAt


def _make_dashboard(dashboard_id: EntityId) -> Dashboard:
    return Dashboard(
        identity=DashboardIdentity(
            entity_id=dashboard_id,
            audit=AuditRecord(
                _created=CreatedAt(datetime.now(UTC)),
                _updated=UpdatedAt(datetime.now(UTC)),
            ),
        ),
        layout=DashboardLayout(
            title=DashboardTitle("Test Dashboard"),
            tiles=Tiles(),
        ),
    )


class FakeDashboardRepository:
    def __init__(self, dashboard: Dashboard | None = None) -> None:
        self._dashboard = dashboard

    def load(self, dashboard_id: EntityId) -> Dashboard | None:
        if self._dashboard and self._dashboard._identity._id == dashboard_id:
            return self._dashboard
        return None

    def save(self, dashboard: Dashboard) -> None:
        self._dashboard = dashboard

    def delete(self, dashboard_id: EntityId) -> None:
        pass

    def find_all(self) -> list[Dashboard]:
        return [self._dashboard] if self._dashboard else []


class FakeQueryExecutor:
    async def execute(self, sql: str, dataset_id: EntityId) -> QueryResult:
        return QueryResult(_columns=("col",), _rows=({"col": "val"},))


class TestApplyCrossFilterUseCase:
    async def test_raises_when_dashboard_not_found(self) -> None:
        repo = FakeDashboardRepository(dashboard=None)
        use_case = ApplyCrossFilterUseCase(dashboards=repo, executor=FakeQueryExecutor())
        request = CrossFilterRequest(
            _dashboard_id=EntityId(uuid4()),
            _source_tile_id=EntityId(uuid4()),
            _column="status",
            _value="active",
        )
        with pytest.raises(DashboardNotFoundError):
            await use_case.execute(request)

    async def test_returns_empty_results_when_no_bound_tiles(self) -> None:
        dashboard_id = EntityId(uuid4())
        source_tile_id = EntityId(uuid4())
        dashboard = _make_dashboard(dashboard_id)
        repo = FakeDashboardRepository(dashboard=dashboard)
        use_case = ApplyCrossFilterUseCase(dashboards=repo, executor=FakeQueryExecutor())

        request = CrossFilterRequest(
            _dashboard_id=dashboard_id,
            _source_tile_id=source_tile_id,
            _column="status",
            _value="active",
        )
        result = await use_case.execute(request)
        assert result._tile_results == {}
        assert result._filter_column == "status"
        assert result._filter_value == "active"
