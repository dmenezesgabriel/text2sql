from __future__ import annotations

from src.dashboards.domain.entities import Dashboard
from src.dashboards.infrastructure.fastapi.router import create_dashboards_router
from src.shared.domain.base import EntityId


class _FakeRepo:
    def save(self, dashboard: Dashboard) -> None:
        pass

    def load(self, dashboard_id: EntityId) -> Dashboard | None:
        return None

    def delete(self, dashboard_id: EntityId) -> None:
        pass

    def find_all(self) -> list[Dashboard]:
        return []


class _FakeComposeUseCase:
    pass


class _FakeFilterUseCase:
    pass


def _make_router():
    return create_dashboards_router(
        dashboard_repo=_FakeRepo(),  # type: ignore[arg-type]
        compose_use_case=_FakeComposeUseCase(),  # type: ignore[arg-type]
        filter_use_case=_FakeFilterUseCase(),  # type: ignore[arg-type]
    )


class TestCreateDashboardsRouter:
    def test_router_is_created(self) -> None:
        router = _make_router()
        assert router is not None

    def test_router_prefix(self) -> None:
        router = _make_router()
        assert router.prefix == "/api/v1/dashboards"

    def test_router_has_expected_routes(self) -> None:
        router = _make_router()
        paths = [r.path for r in router.routes]
        assert "/api/v1/dashboards" in paths
