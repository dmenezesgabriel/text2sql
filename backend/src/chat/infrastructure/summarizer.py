from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from src.chat.application.ports.i_language_model_provider import (
    ILanguageModelProvider,
)
from src.chat.application.ports.i_summarizer import ISummarizer
from src.chat.domain.entities import (
    AgentConfiguration,
    AgentDirectives,
    Message,
    MessageBody,
    MessageIdentity,
    ModelConfig,
)
from src.chat.domain.value_objects import (
    MessageContent,
    MessageRole,
    ModelProvider,
    SystemPrompt,
    Temperature,
    TokenCount,
)
from src.shared.domain.base import CreatedAt, EntityId


class LiteLLMSummarizer(ISummarizer):
    def __init__(
        self,
        llm: ILanguageModelProvider,
        model_name: str = "gpt-4o-mini",
    ) -> None:
        self._llm = llm
        self._model_name = model_name

    async def summarize(self, text: str) -> str:
        messages = [
            Message(
                identity=MessageIdentity(
                    _id=EntityId(uuid4()),
                    _role=MessageRole.SYSTEM,
                    _timestamp=CreatedAt(datetime.now(UTC)),
                ),
                body=MessageBody(
                    _content=MessageContent(
                        "Summarize the following conversation concisely, "
                        "keeping all important details, SQL queries, "
                        "and decisions made.",
                    ),
                    _tool_call=None,
                ),
            ),
            Message(
                identity=MessageIdentity(
                    _id=EntityId(uuid4()),
                    _role=MessageRole.USER,
                    _timestamp=CreatedAt(datetime.now(UTC)),
                ),
                body=MessageBody(
                    _content=MessageContent(text),
                    _tool_call=None,
                ),
            ),
        ]
        config = AgentConfiguration(
            identity=EntityId(uuid4()),
            model=ModelConfig(
                _provider=ModelProvider(self._model_name),
                _temperature=Temperature(0.3),
            ),
            directives=AgentDirectives(
                _system=SystemPrompt(""),
                _max_tokens=TokenCount(500),
            ),
        )
        return await self._llm.generate(messages, config)
