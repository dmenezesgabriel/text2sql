from __future__ import annotations

from collections.abc import AsyncIterator

from src.agent.application.ports.i_agent_orchestrator import IAgentOrchestrator
from src.agent.application.ports.i_conversation_repository import (
    IConversationRepository,
)
from src.agent.application.ports.i_tool_kit import IToolKit
from src.agent.domain.entities import (
    AgentConfiguration,
    MessageRole,
)
from src.agent.domain.value_objects import (
    AgentEvent,
    ConversationId,
)


class ReplayConversationUseCase:
    def __init__(
        self,
        conversations: IConversationRepository,
        orchestrator: IAgentOrchestrator,
        toolkit: IToolKit,
    ) -> None:
        self._conversations = conversations
        self._orchestrator = orchestrator
        self._toolkit = toolkit

    async def execute(
        self,
        conversation_id: ConversationId,
        new_config: AgentConfiguration,
    ) -> AsyncIterator[AgentEvent]:
        conversation = await self._conversations.load(conversation_id)
        if conversation is None:
            raise ValueError(
                f"Conversation {conversation_id.value} not found",
            )

        user_messages = [m for m in conversation._history.to_list() if m.is_from(MessageRole.USER)]
        for msg in user_messages:
            async for event in self._orchestrator.run(
                message=msg,
                conversation=conversation,
                toolkit=self._toolkit,
            ):
                yield event
