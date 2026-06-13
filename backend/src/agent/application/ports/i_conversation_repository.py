from __future__ import annotations

from typing import Protocol

from src.agent.domain.entities import Conversation
from src.agent.domain.value_objects import ConversationId


class IConversationRepository(Protocol):
    def save(self, conversation: Conversation) -> None: ...

    def load(self, conversation_id: ConversationId) -> Conversation | None: ...

    def delete(self, conversation_id: ConversationId) -> None: ...
