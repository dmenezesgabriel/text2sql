from __future__ import annotations

from typing import AsyncIterator, Protocol

from src.agent.domain.value_objects import AgentEvent
from src.agent.domain.entities import Message, Conversation
from src.agent.application.ports.i_tool_kit import IToolKit


class IAgentOrchestrator(Protocol):
    def run(
        self,
        message: Message,
        conversation: Conversation,
        toolkit: IToolKit,
    ) -> AsyncIterator[AgentEvent]: ...
