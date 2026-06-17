from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass
from uuid import UUID

from src.chat.application.ports.i_agent_orchestrator import IAgentOrchestrator
from src.chat.application.ports.i_conversation_repository import IConversationRepository
from src.chat.domain.entities import Conversation
from src.chat.domain.value_objects import (
    AgentEvent,
    ConversationId,
    MessageContent,
    ThinkingEvent,
)
from src.shared.domain.base import EntityId

_logger = logging.getLogger(__name__)


class ProcessMessageRequest:
    def __init__(self, content: str, conversation_id: UUID) -> None:
        self._content = MessageContent(content)
        self._conversation_id = ConversationId(conversation_id)


@dataclass
class AgentConfig:
    """Bundles agent dependencies for the chat use case."""

    _orchestrator: IAgentOrchestrator


class HandleChatMessageUseCase:
    def __init__(
        self,
        conversations: IConversationRepository,
        agent: AgentConfig,
    ) -> None:
        self._conversations = conversations
        self._agent = agent

    async def execute(self, request: ProcessMessageRequest) -> AsyncIterator[AgentEvent]:
        conv_id = request._conversation_id
        _logger.info("chat.start", extra={"conversation_id": str(conv_id.value)})
        conversation = self._load_or_create(conv_id)
        yield ThinkingEvent("Processing your question...")
        async for event in self._agent._orchestrator.run(
            content=request._content.value,
            conversation_id=conv_id,
        ):
            yield event
        self._conversations.save(conversation)
        _logger.info("chat.complete", extra={"conversation_id": str(conv_id.value)})

    def _load_or_create(self, conversation_id: ConversationId) -> Conversation:
        existing = self._conversations.load(conversation_id)
        if existing is not None:
            return existing
        return Conversation(identity=EntityId(conversation_id.value))
