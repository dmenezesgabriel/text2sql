from __future__ import annotations

from typing import Protocol

from src.dashboards.domain.entities import DashboardTile
from src.dashboards.domain.value_objects import FilterBinding
from src.agent.domain.value_objects import QueryResult


class ICrossFilterService(Protocol):
    async def apply(
        self,
        filters: tuple[FilterBinding, ...],
        tile: DashboardTile,
        value: str,
    ) -> QueryResult: ...
