from __future__ import annotations

from typing import Protocol

from src.agent.domain.value_objects import QueryResult
from src.dashboards.domain.entities import DashboardTile
from src.dashboards.domain.value_objects import FilterBinding


class ICrossFilterService(Protocol):
    async def apply(
        self,
        filters: tuple[FilterBinding, ...],
        tile: DashboardTile,
        value: str,
    ) -> QueryResult: ...
