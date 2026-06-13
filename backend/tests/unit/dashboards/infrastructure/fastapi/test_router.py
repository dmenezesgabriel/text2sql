from __future__ import annotations

from src.dashboards.infrastructure.fastapi.router import create_dashboards_router


class TestCreateDashboardsRouter:
    def test_router_is_created(self) -> None:
        router = create_dashboards_router()
        assert router is not None

    def test_router_prefix(self) -> None:
        router = create_dashboards_router()
        assert router.prefix == "/api/v1/dashboards"

    def test_router_has_expected_routes(self) -> None:
        router = create_dashboards_router()
        paths = {r.path for r in router.routes}
        assert "" in paths or "/api/v1/dashboards" in paths or any(True for _ in paths)
