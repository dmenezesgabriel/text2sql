from __future__ import annotations

import json
from collections.abc import AsyncIterator
from uuid import UUID

from src.agent.application.ports.i_agent_orchestrator import IAgentOrchestrator
from src.agent.application.ports.i_conversation_repository import IConversationRepository
from src.agent.application.ports.i_summarizer import ISummarizer
from src.agent.application.ports.i_tool_kit import IToolKit
from src.agent.domain.entities import Conversation, EntityId, Messages
from src.agent.domain.value_objects import (
    AgentEvent,
    ConversationId,
    MessageContent,
    SpecFragmentEvent,
    ThinkingEvent,
    TokenCount,
)


class ProcessMessageRequest:
    def __init__(self, content: str, conversation_id: UUID) -> None:
        self._content = MessageContent(content)
        self._conversation_id = ConversationId(conversation_id)

    def is_valid(self) -> bool:
        return not self._content.is_empty()


class HandleChatMessageUseCase:
    def __init__(  # noqa: PLR0913
        self,
        conversations: IConversationRepository,
        orchestrator: IAgentOrchestrator,
        toolkit: IToolKit,
        summarizer: ISummarizer,
        token_limit: TokenCount,
    ) -> None:
        self._conversations = conversations
        self._orchestrator = orchestrator
        self._toolkit = toolkit
        self._summarizer = summarizer
        self._token_limit = token_limit

    async def execute(self, request: ProcessMessageRequest) -> AsyncIterator[AgentEvent]:
        conversation = self._load_or_create(request._conversation_id)

        message = conversation.add_user_message(request._content.value)
        yield ThinkingEvent("Processing your question...")

        if conversation.should_summarize(self._token_limit):
            conversation.summarize_oldest(self._summarizer)
            yield ThinkingEvent("Summarizing conversation context...")

        final_spec: dict | None = None
        async for event in self._orchestrator.run(
            message=message,
            conversation=conversation,
            toolkit=self._toolkit,
        ):
            if isinstance(event, SpecFragmentEvent):
                final_spec = event._payload
            yield event

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
