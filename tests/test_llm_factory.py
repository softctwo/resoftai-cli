"""Tests for LLM factory."""
import pytest
from resoftai.llm.factory import LLMFactory
from resoftai.llm.base import LLMConfig, ModelProvider


class TestLLMFactory:
    """Test LLM factory functionality."""

    def test_create_deepseek_provider(self):
        """Test creating DeepSeek provider."""
        config = LLMConfig(
            provider=ModelProvider.DEEPSEEK,
            api_key="test-key",
            model_name="deepseek-chat"
        )

        llm = LLMFactory.create(config)
        assert llm is not None
        assert llm.__class__.__name__ == "DeepSeekProvider"

    def test_create_anthropic_provider(self):
        """Test creating Anthropic provider."""
        config = LLMConfig(
            provider=ModelProvider.ANTHROPIC,
            api_key="test-key",
            model_name="claude-3-5-sonnet-20241022"
        )

        llm = LLMFactory.create(config)
        assert llm is not None
        assert llm.__class__.__name__ == "AnthropicProvider"

    def test_create_with_custom_params(self):
        """Test creating provider with custom parameters."""
        config = LLMConfig(
            provider=ModelProvider.DEEPSEEK,
            api_key="test-key",
            model_name="deepseek-chat",
            max_tokens=4096,
            temperature=0.5,
            top_p=0.9
        )

        llm = LLMFactory.create(config)
        assert llm is not None

    def test_unsupported_provider(self):
        """Test that unsupported provider raises error."""
        config = LLMConfig(
            provider="unsupported",
            api_key="test-key",
            model_name="test-model"
        )

        with pytest.raises((ValueError, KeyError)):
            LLMFactory.create(config)


class TestLLMConfig:
    """Test LLM configuration."""

    def test_config_creation(self):
        """Test creating LLM config."""
        config = LLMConfig(
            provider=ModelProvider.DEEPSEEK,
            api_key="test-key",
            model_name="deepseek-chat"
        )

        assert config.provider == ModelProvider.DEEPSEEK
        assert config.api_key == "test-key"
        assert config.model_name == "deepseek-chat"
        assert config.max_tokens == 8192  # default
        assert config.temperature == 0.7  # default

    def test_config_with_optional_params(self):
        """Test creating config with optional parameters."""
        config = LLMConfig(
            provider=ModelProvider.ANTHROPIC,
            api_key="test-key",
            model_name="claude-3-5-sonnet-20241022",
            api_base="https://custom-api.example.com",
            max_tokens=4096,
            temperature=0.5,
            top_p=0.9,
            extra_params={"custom": "value"}
        )

        assert config.api_base == "https://custom-api.example.com"
        assert config.max_tokens == 4096
        assert config.temperature == 0.5
        assert config.top_p == 0.9
        assert config.extra_params == {"custom": "value"}


@pytest.mark.asyncio
async def test_llm_generate_mock():
    """Test LLM generation with mock (integration test)."""
    # This test would require actual API keys or mocking
    # For now, it's a placeholder
    pass
