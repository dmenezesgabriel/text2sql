from __future__ import annotations

from typing import Protocol

from src.questions.domain.value_objects import VizSpec, VizDecision
from src.agent.domain.value_objects import QueryResult


class IVizSpecBuilder(Protocol):
    async def build(
        self, result: QueryResult, decision: VizDecision
    ) -> VizSpec: ...
