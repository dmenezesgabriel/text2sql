from __future__ import annotations

from typing import Protocol

from src.dashboards.domain.entities import Dashboard
from src.shared.domain.base import EntityId


class IDashboardRepository(Protocol):
    def save(self, dashboard: Dashboard) -> None: ...

    def load(self, dashboard_id: EntityId) -> Dashboard | None: ...

    def delete(self, dashboard_id: EntityId) -> None: ...

    def find_all(self) -> list[Dashboard]: ...
