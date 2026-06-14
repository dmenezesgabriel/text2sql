from __future__ import annotations

from src.chat.domain.entities import AgentConfiguration, Message
from src.chat.domain.value_objects import LLMToolResponse
from src.chat.infrastructure.summarizer import LiteLLMSummarizer


class FakeLLMProvider:
    async def generate(self, messages: list[Message], config: AgentConfiguration) -> str:
        return "summary text"

    async def call_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
    ) -> LLMToolResponse:
        return LLMToolResponse(_text="ok", _tool_calls=(), _stop_reason="stop")


class TestLiteLLMSummarizer:
    def test_instantiate_with_fake_llm(self) -> None:
        llm = FakeLLMProvider()
        summarizer = LiteLLMSummarizer(llm=llm)
        assert summarizer is not None

    def test_custom_model_name_stored(self) -> None:
        llm = FakeLLMProvider()
        summarizer = LiteLLMSummarizer(llm=llm, model_name="gpt-4o-mini")
        assert summarizer._model_name == "gpt-4o-mini"

    async def test_summarize_calls_llm(self) -> None:
        llm = FakeLLMProvider()
        summarizer = LiteLLMSummarizer(llm=llm)
        result = await summarizer.summarize("some long text")
        assert result == "summary text"
