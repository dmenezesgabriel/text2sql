from __future__ import annotations

from typing import AsyncIterator, Protocol

from src.agent.domain.entities import Message, AgentConfiguration


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
