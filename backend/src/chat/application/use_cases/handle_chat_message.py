from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass
from uuid import UUID

from src.chat.application.ports.i_agent_orchestrator import IAgentOrchestrator
from src.chat.application.ports.i_conversation_repository import IConversationRepository
from src.chat.application.ports.i_summarizer import ISummarizer
from src.chat.application.ports.i_tool_kit import IToolKit
from src.chat.domain.entities import Conversation, EntityId, Messages
from src.chat.domain.value_objects import (
    AgentEvent,
    ConversationId,
    MessageContent,
    SpecFragmentEvent,
    ThinkingEvent,
    TokenCount,
)

_logger = logging.getLogger(__name__)


class ProcessMessageRequest:
    def __init__(self, content: str, conversation_id: UUID) -> None:
        self._content = MessageContent(content)
        self._conversation_id = ConversationId(conversation_id)


@dataclass
class AgentConfig:
    """Bundles all agent dependencies for chat use cases."""

    _orchestrator: IAgentOrchestrator
    _toolkit: IToolKit
    _summarizer: ISummarizer
    _token_limit: TokenCount


class HandleChatMessageUseCase:
    def __init__(
        self,
        conversations: IConversationRepository,
        agent: AgentConfig,
    ) -> None:
        self._conversations = conversations
        self._agent = agent

    async def execute(self, request: ProcessMessageRequest) -> AsyncIterator[AgentEvent]:
        conv_id = str(request._conversation_id.value)
        _logger.info("chat.start", extra={"conversation_id": conv_id})
        conversation = self._load_or_create(request._conversation_id)
        message = conversation.add_user_message(request._content.value)
        yield ThinkingEvent("Processing your question...")

        async for event in self._maybe_summarize(conversation):
            yield event

        final_spec: dict[str, object] | None = None
        async for event in self._agent._orchestrator.run(
            message=message,
            conversation=conversation,
            toolkit=self._agent._toolkit,
        ):
            if isinstance(event, SpecFragmentEvent):
                final_spec = event._payload
            yield event

        self._finalize(conversation, final_spec)
        _logger.info("chat.complete", extra={"conversation_id": conv_id})

    async def _maybe_summarize(self, conversation: Conversation) -> AsyncIterator[AgentEvent]:
        if not conversation.should_summarize(self._agent._token_limit):
            return
        recent = conversation.recent_messages(window=10)
        summary = await self._agent._summarizer.summarize(conversation.history_text())
        conversation.apply_summary(summary, recent)
        yield ThinkingEvent("Summarizing conversation context...")

    def _finalize(
        self,
        conversation: Conversation,
        final_spec: dict[str, object] | None,
    ) -> None:
        content = json.dumps(final_spec) if final_spec else "(no result)"
        conversation.add_assistant_response(content=content, tool_call=None)
        self._conversations.save(conversation)

    def _load_or_create(self, conversation_id: ConversationId) -> Conversation:
        existing = self._conversations.load(conversation_id)
        if existing is not None:
            return existing
        return Conversation(
            identity=EntityId(conversation_id.value),
            history=Messages(),
        )
