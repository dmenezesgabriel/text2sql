from __future__ import annotations

from typing import AsyncIterator

from src.agent.domain.value_objects import (
    AgentEvent, ThinkingEvent, ToolCallEvent, SpecFragmentEvent,
    ToolName, Parameters,
)
from src.agent.domain.entities import Message, Conversation, AgentConfiguration
from src.agent.application.ports.i_agent_orchestrator import IAgentOrchestrator
from src.agent.application.ports.i_tool_kit import IToolKit
from src.agent.application.ports.i_language_model_provider import ILanguageModelProvider


class DeepAgentsOrchestrator(IAgentOrchestrator):
    def __init__(self, llm: ILanguageModelProvider) -> None:
        self._llm = llm

    async def run(
        self,
        message: Message,
        conversation: Conversation,
        toolkit: IToolKit,
    ) -> AsyncIterator[AgentEvent]:
        yield ThinkingEvent("Analyzing query...")
        yield ThinkingEvent("Generating SQL...")

        yield ToolCallEvent(
            _tool_name=ToolName("sql_generator"),
            _parameters=Parameters({"query": message._body._content.value}),
        )

        yield ThinkingEvent("Building visualization...")
        yield SpecFragmentEvent(_payload={"root": "response", "elements": {}})

        yield ThinkingEvent("Done")
