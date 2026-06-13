from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass

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


@dataclass
class AgentRuntime:
    """Bundles orchestrator and toolkit for replay use cases."""

    _orchestrator: IAgentOrchestrator
    _toolkit: IToolKit


class ReplayConversationUseCase:
    def __init__(
        self,
        conversations: IConversationRepository,
        orchestrator: IAgentOrchestrator,
        toolkit: IToolKit,
    ) -> None:
        self._conversations = conversations
        self._runtime = AgentRuntime(_orchestrator=orchestrator, _toolkit=toolkit)

    async def execute(
        self,
        conversation_id: ConversationId,
        new_config: AgentConfiguration,
    ) -> AsyncIterator[AgentEvent]:
        conversation = await self._conversations.load(conversation_id)
        if conversation is None:
            msg = f"Conversation {conversation_id.value} not found"
            raise ValueError(msg)

        user_messages = [m for m in conversation._history.to_list() if m.is_from(MessageRole.USER)]
        for msg in user_messages:
            async for event in self._runtime._orchestrator.run(
                message=msg,
                conversation=conversation,
                toolkit=self._runtime._toolkit,
            ):
                yield event
