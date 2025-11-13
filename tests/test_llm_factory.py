"""
Comprehensive tests for LLM factory.
"""
import pytest
from unittest.mock import Mock, patch

from resoftai.llm.factory import LLMFactory
from resoftai.llm.base import LLMConfig, ModelProvider, LLMProvider


@pytest.fixture
def deepseek_config():
    """Create DeepSeek config."""
    return LLMConfig(
        provider=ModelProvider.DEEPSEEK,
        model_name="deepseek-chat",
        api_key="test-api-key",
        max_tokens=4096,
        temperature=0.7
    )


@pytest.fixture
def anthropic_config():
    """Create Anthropic config."""
    return LLMConfig(
        provider=ModelProvider.ANTHROPIC,
        model_name="claude-3-5-sonnet-20241022",
        api_key="test-api-key",
        max_tokens=4096,
        temperature=0.7
    )


class TestLLMFactoryCreate:
    """Test LLM factory create method."""

    def test_create_deepseek_provider(self, deepseek_config):
        """Test creating DeepSeek provider."""
        provider = LLMFactory.create(deepseek_config)

        assert provider is not None
        assert provider.provider_name == "DeepSeek"
        assert provider.config == deepseek_config

    def test_create_anthropic_provider(self, anthropic_config):
        """Test creating Anthropic provider."""
        provider = LLMFactory.create(anthropic_config)

        assert provider is not None
        assert provider.provider_name == "Anthropic Claude"
        assert provider.config == anthropic_config

    def test_create_zhipu_provider(self):
        """Test creating Zhipu provider."""
        config = LLMConfig(
            provider=ModelProvider.ZHIPU,
            model_name="glm-4-plus",
            api_key="test-api-key"
        )
        provider = LLMFactory.create(config)

        assert provider is not None
        assert provider.provider_name == "智谱AI GLM"
        assert provider.config == config

    def test_create_moonshot_provider(self):
        """Test creating Moonshot provider."""
        config = LLMConfig(
            provider=ModelProvider.MOONSHOT,
            model_name="moonshot-v1-8k",
            api_key="test-api-key"
        )
        provider = LLMFactory.create(config)

        assert provider is not None
        assert provider.provider_name == "Moonshot (Kimi)"
        assert provider.config == config

    def test_create_minimax_provider(self):
        """Test creating Minimax provider."""
        config = LLMConfig(
            provider=ModelProvider.MINIMAX,
            model_name="abab6.5-chat",
            api_key="test-api-key"
        )
        provider = LLMFactory.create(config)

        assert provider is not None
        assert provider.provider_name == "Minimax"
        assert provider.config == config

    def test_create_google_provider(self):
        """Test creating Google provider."""
        config = LLMConfig(
            provider=ModelProvider.GOOGLE,
            model_name="gemini-pro",
            api_key="test-api-key"
        )
        provider = LLMFactory.create(config)

        assert provider is not None
        assert provider.provider_name == "Google Gemini"
        assert provider.config == config

    def test_create_unsupported_provider(self):
        """Test creating unsupported provider raises error."""
        config = LLMConfig(
            provider="unsupported_provider",
            model_name="test-model",
            api_key="test-api-key"
        )

        with pytest.raises(ValueError, match="Unsupported provider"):
            LLMFactory.create(config)

    def test_get_available_providers(self):
        """Test getting available providers."""
        providers = LLMFactory.get_available_providers()

        assert isinstance(providers, dict)
        assert len(providers) == 6
        assert "anthropic" in providers
        assert "zhipu" in providers
        assert "deepseek" in providers
        assert "moonshot" in providers
        assert "minimax" in providers
        assert "google" in providers

    def test_get_default_models(self):
        """Test getting default models."""
        models = LLMFactory.get_default_models()

        assert isinstance(models, dict)
        assert len(models) == 6
        assert models[ModelProvider.DEEPSEEK] == "deepseek-chat"
        assert models[ModelProvider.ANTHROPIC] == "claude-3-5-sonnet-20241022"
        assert models[ModelProvider.ZHIPU] == "glm-4-plus"
        assert models[ModelProvider.MOONSHOT] == "moonshot-v1-8k"
        assert models[ModelProvider.MINIMAX] == "abab6.5-chat"
        assert models[ModelProvider.GOOGLE] == "gemini-1.5-pro"


class TestLLMFactoryCustomProvider:
    """Test custom provider registration."""

    def test_register_custom_provider(self):
        """Test registering custom provider."""
        # Create mock custom provider
        class CustomProvider(LLMProvider):
            @property
            def provider_name(self) -> str:
                return "Custom"

            async def generate(self, prompt: str, system_prompt=None, **kwargs):
                pass

            async def generate_stream(self, prompt: str, system_prompt=None, **kwargs):
                pass

            def validate_config(self) -> bool:
                return True

        # Register custom provider
        LLMFactory.register_custom_provider("custom", CustomProvider)

        # Verify registration
        assert "custom" in LLMFactory._custom_providers
        assert LLMFactory._custom_providers["custom"] == CustomProvider


class TestLLMFactoryIntegration:
    """Integration tests for LLM factory."""

    def test_create_all_builtin_providers(self):
        """Test creating all built-in providers."""
        providers_config = [
            (ModelProvider.DEEPSEEK, "deepseek-chat"),
            (ModelProvider.ANTHROPIC, "claude-3-5-sonnet-20241022"),
            (ModelProvider.ZHIPU, "glm-4-plus"),
            (ModelProvider.MOONSHOT, "moonshot-v1-8k"),
            (ModelProvider.MINIMAX, "abab6.5-chat"),
            (ModelProvider.GOOGLE, "gemini-1.5-pro"),
        ]

        for provider_type, model_name in providers_config:
            config = LLMConfig(
                provider=provider_type,
                model_name=model_name,
                api_key="test-api-key"
            )

            provider = LLMFactory.create(config)
            assert provider is not None
            assert isinstance(provider, LLMProvider)
            assert provider.config.provider == provider_type

    def test_provider_config_inheritance(self):
        """Test provider inherits all config parameters."""
        config = LLMConfig(
            provider=ModelProvider.DEEPSEEK,
            model_name="deepseek-chat",
            api_key="test-api-key",
            api_base="https://custom.api.com",
            max_tokens=8192,
            temperature=0.9,
            top_p=0.95
        )

        provider = LLMFactory.create(config)

        assert provider.config.api_base == "https://custom.api.com"
        assert provider.config.max_tokens == 8192
        assert provider.config.temperature == 0.9
        assert provider.config.top_p == 0.95
