from __future__ import annotations

import json
from collections.abc import AsyncIterator

from litellm import acompletion, completion

from src.agent.application.ports.i_language_model_provider import ILanguageModelProvider
from src.agent.domain.entities import AgentConfiguration, Message
from src.agent.domain.value_objects import LLMToolCall, LLMToolResponse


class LiteLLMProvider(ILanguageModelProvider):
    def __init__(self, model_name: str = "gpt-4o") -> None:
        self._model_name = model_name

    async def generate(self, messages: list[Message], config: AgentConfiguration) -> str:
        formatted = [
            {"role": m._identity._role.name.lower(), "content": m._body._content.value}
            for m in messages
        ]
        response = await acompletion(
            model=self._model_name,
            messages=formatted,
            temperature=config._model._temperature.value,
        )
        return response.choices[0].message.content or ""

    def stream(self, messages: list[Message], config: AgentConfiguration) -> AsyncIterator[str]:
        formatted = [
            {"role": m._identity._role.name.lower(), "content": m._body._content.value}
            for m in messages
        ]
        response = completion(
            model=self._model_name,
            messages=formatted,
            temperature=config._model._temperature.value,
            stream=True,
        )
        for chunk in response:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                yield delta

    async def call_with_tools(self, messages: list[dict], tools: list[dict]) -> LLMToolResponse:
        response = await acompletion(
            model=self._model_name,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        choice = response.choices[0]
        msg = choice.message
        if choice.finish_reason == "tool_calls" and msg.tool_calls:
            calls = tuple(
                LLMToolCall(
                    _id=tc.id,
                    _name=tc.function.name,
                    _arguments=json.loads(tc.function.arguments),
                )
                for tc in msg.tool_calls
            )
            return LLMToolResponse(_text=None, _tool_calls=calls, _stop_reason="tool_calls")
        return LLMToolResponse(_text=msg.content or "", _tool_calls=(), _stop_reason="stop")
