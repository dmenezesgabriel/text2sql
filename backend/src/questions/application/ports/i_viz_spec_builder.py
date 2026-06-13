from __future__ import annotations

from typing import Protocol

from src.agent.domain.value_objects import QueryResult
from src.questions.domain.value_objects import VizDecision, VizSpec


class IVizSpecBuilder(Protocol):
    async def build(
        self,
        result: QueryResult,
        decision: VizDecision,
    ) -> VizSpec: ...
