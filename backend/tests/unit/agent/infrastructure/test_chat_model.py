from __future__ import annotations

from src.agent.infrastructure.chat_model import build_chat_model


class TestBuildChatModel:
    def test_sets_model_name(self) -> None:
        model = build_chat_model("openrouter/openai/gpt-oss-120b:free")
        assert model.model == "openrouter/openai/gpt-oss-120b:free"

    def test_defaults_temperature_to_zero(self) -> None:
        model = build_chat_model("gpt-4o")
        assert model.temperature == 0.0

    def test_accepts_custom_temperature(self) -> None:
        model = build_chat_model("gpt-4o", temperature=0.5)
        assert model.temperature == 0.5
