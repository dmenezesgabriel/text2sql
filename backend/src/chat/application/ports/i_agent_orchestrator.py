from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol

from src.chat.application.ports.i_tool_kit import IToolKit
from src.chat.domain.entities import Conversation, Message
from src.chat.domain.value_objects import AgentEvent


class IAgentOrchestrator(Protocol):
    def run(
        self,
        message: Message,
        conversation: Conversation,
        toolkit: IToolKit,
    ) -> AsyncIterator[AgentEvent]: ...
