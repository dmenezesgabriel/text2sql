from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol

from src.chat.domain.value_objects import AgentEvent, ConversationId


class IAgentOrchestrator(Protocol):
    def run(
        self,
        content: str,
        conversation_id: ConversationId,
    ) -> AsyncIterator[AgentEvent]: ...

    async def get_messages(
        self,
        conversation_id: ConversationId,
    ) -> list[dict[str, object]]: ...
