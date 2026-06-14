from __future__ import annotations

from langchain_litellm import ChatLiteLLM


def build_chat_model(model_name: str, temperature: float = 0.0) -> ChatLiteLLM:
    """Build a LangChain chat model backed by LiteLLM for the deep agent.

    Keeps the project on its LiteLLM model strings (e.g.
    "openrouter/openai/gpt-oss-120b:free") while exposing the BaseChatModel
    interface that deepagents' create_deep_agent expects.
    """
    return ChatLiteLLM(model=model_name, temperature=temperature)
