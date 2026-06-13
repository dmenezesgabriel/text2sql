from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol

from src.agent.application.ports.i_tool_kit import IToolKit
from src.agent.domain.entities import Conversation, Message
from src.agent.domain.value_objects import AgentEvent


class IAgentOrchestrator(Protocol):
    def run(
        self,
        message: Message,
        conversation: Conversation,
        toolkit: IToolKit,
    ) -> AsyncIterator[AgentEvent]: ...
