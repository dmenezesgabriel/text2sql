from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol

from src.agent.domain.entities import AgentConfiguration, Message
from src.agent.domain.value_objects import LLMToolResponse


class ILanguageModelProvider(Protocol):
    async def generate(
        self,
        messages: list[Message],
        config: AgentConfiguration,
    ) -> str: ...

    def stream(
        self,
        messages: list[Message],
        config: AgentConfiguration,
    ) -> AsyncIterator[str]: ...

    async def call_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
    ) -> LLMToolResponse: ...
