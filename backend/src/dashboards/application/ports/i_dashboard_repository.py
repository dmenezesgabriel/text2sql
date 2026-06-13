from __future__ import annotations

from typing import Protocol

from src.shared.domain.base import EntityId
from src.dashboards.domain.entities import Dashboard


class IDashboardRepository(Protocol):
    async def save(self, dashboard: Dashboard) -> None: ...

    async def load(self, dashboard_id: EntityId) -> Dashboard | None: ...

    async def delete(self, dashboard_id: EntityId) -> None: ...

    async def find_all(self) -> list[Dashboard]: ...
