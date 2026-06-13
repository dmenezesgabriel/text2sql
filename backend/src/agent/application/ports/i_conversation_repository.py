from __future__ import annotations

from typing import Protocol

from src.agent.domain.value_objects import ConversationId
from src.agent.domain.entities import Conversation


class IConversationRepository(Protocol):
    async def save(self, conversation: Conversation) -> None: ...

    async def load(self, conversation_id: ConversationId) -> Conversation | None: ...

    async def delete(self, conversation_id: ConversationId) -> None: ...
