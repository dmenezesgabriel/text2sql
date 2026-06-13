from __future__ import annotations

from typing import Protocol

from src.questions.domain.value_objects import VizDecision, VizSpec
from src.shared.domain.base import QueryResult


class IVizSpecBuilder(Protocol):
    async def build(
        self,
        result: QueryResult,
        decision: VizDecision,
    ) -> VizSpec: ...
