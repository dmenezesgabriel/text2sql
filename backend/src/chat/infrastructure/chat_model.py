from __future__ import annotations

from langchain_litellm import ChatLiteLLM


def build_chat_model(model_name: str, temperature: float = 0.0) -> ChatLiteLLM:
    """Build a LangChain chat model backed by LiteLLM.

    Accepts LiteLLM model strings (e.g. "openrouter/openai/gpt-oss-120b:free")
    and exposes the BaseChatModel interface expected by create_react_agent.
    """
    return ChatLiteLLM(model=model_name, temperature=temperature)
