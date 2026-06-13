from __future__ import annotations


class TestLiteLLMProvider:
    def test_module_imports(self) -> None:
        from src.agent.infrastructure.litellm_provider import LiteLLMProvider

        assert LiteLLMProvider is not None

    def test_instantiate_with_model_name(self) -> None:
        from src.agent.infrastructure.litellm_provider import LiteLLMProvider

        provider = LiteLLMProvider(model_name="gpt-4o")
        assert provider._model_name == "gpt-4o"

    def test_default_model_name(self) -> None:
        from src.agent.infrastructure.litellm_provider import LiteLLMProvider

        provider = LiteLLMProvider()
        assert provider._model_name == "gpt-4o"
