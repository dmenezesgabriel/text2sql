from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.chat.domain.entities import Conversation
from src.chat.domain.value_objects import ConversationId


@dataclass
class ConversationSummary:
    id: str
    title: str
    updated_at: str


class IConversationRepository(Protocol):
    def save(self, conversation: Conversation) -> None: ...

    def load(self, conversation_id: ConversationId) -> Conversation | None: ...

    def delete(self, conversation_id: ConversationId) -> None: ...

    def find_all(self) -> list[ConversationSummary]: ...
