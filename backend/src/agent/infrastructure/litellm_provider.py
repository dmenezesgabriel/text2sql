from __future__ import annotations

from typing import AsyncIterator

from src.agent.domain.value_objects import MessageContent
from src.agent.domain.entities import Message, AgentConfiguration
from src.agent.application.ports.i_language_model_provider import ILanguageModelProvider


class LiteLLMProvider(ILanguageModelProvider):
    def __init__(self, model_name: str = "gpt-4o") -> None:
        self._model_name = model_name

    async def generate(
        self,
        messages: list[Message],
        config: AgentConfiguration,
    ) -> str:
        formatted = [
            {"role": m._identity._role.name.lower(), "content": m._body._content.value}
            for m in messages
        ]

        from litellm import acompletion
        response = await acompletion(
            model=self._model_name,
            messages=formatted,
            temperature=config._model._temperature.value,
        )
        return response.choices[0].message.content or ""

    def stream(
        self,
        messages: list[Message],
        config: AgentConfiguration,
    ) -> AsyncIterator[str]:
        formatted = [
            {"role": m._identity._role.name.lower(), "content": m._body._content.value}
            for m in messages
        ]

        from litellm import completion
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
