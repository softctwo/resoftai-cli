"""
LLM Factory for creating provider instances.
"""

from typing import Dict, Type
import logging

from resoftai.llm.base import LLMProvider, LLMConfig, ModelProvider
from resoftai.llm.providers import (
    AnthropicProvider,
    ZhipuProvider,
    DeepSeekProvider,
    MoonshotProvider,
    MinimaxProvider,
    GoogleProvider,
)

logger = logging.getLogger(__name__)


class LLMFactory:
    """
    Factory class for creating LLM provider instances.
    """

    _providers: Dict[ModelProvider, Type[LLMProvider]] = {
        ModelProvider.ANTHROPIC: AnthropicProvider,
        ModelProvider.ZHIPU: ZhipuProvider,
        ModelProvider.DEEPSEEK: DeepSeekProvider,
        ModelProvider.MOONSHOT: MoonshotProvider,
        ModelProvider.MINIMAX: MinimaxProvider,
        ModelProvider.GOOGLE: GoogleProvider,
    }

    _custom_providers: Dict[str, Type[LLMProvider]] = {}

    @classmethod
    def create(cls, config: LLMConfig) -> LLMProvider:
        """
        Create an LLM provider instance based on configuration.

        Args:
            config: LLM configuration

        Returns:
            LLM provider instance

        Raises:
            ValueError: If provider is not supported
        """
        if config.provider not in cls._providers:
            raise ValueError(f"Unsupported provider: {config.provider}")

        provider_class = cls._providers[config.provider]
        provider = provider_class(config)

        if not provider.validate_config():
            raise ValueError(f"Invalid configuration for provider: {config.provider}")

        logger.info(f"Created {provider.provider_name} provider with model {config.model_name}")

        return provider

    @classmethod
    def register_custom_provider(
        cls,
        name: str,
        provider_class: Type[LLMProvider]
    ) -> None:
        """
        Register a custom LLM provider.

        Args:
            name: Provider name
            provider_class: Provider class
        """
        cls._custom_providers[name] = provider_class
        logger.info(f"Registered custom provider: {name}")

    @classmethod
    def get_available_providers(cls) -> Dict[str, str]:
        """
        Get list of available providers.

        Returns:
            Dictionary of provider names and descriptions
        """
        return {
            "anthropic": "Anthropic Claude (claude-3-5-sonnet等)",
            "zhipu": "智谱AI GLM (glm-4-plus, glm-4等)",
            "deepseek": "DeepSeek (deepseek-chat, deepseek-coder等)",
            "moonshot": "Moonshot (Kimi) (moonshot-v1-8k, moonshot-v1-32k等)",
            "minimax": "Minimax (abab6.5-chat等)",
            "google": "Google Gemini (gemini-pro, gemini-1.5-pro等)",
        }

    @classmethod
    def get_default_models(cls) -> Dict[ModelProvider, str]:
        """
        Get default model names for each provider.

        Returns:
            Dictionary of provider and default model name
        """
        return {
            ModelProvider.ANTHROPIC: "claude-3-5-sonnet-20241022",
            ModelProvider.ZHIPU: "glm-4-plus",
            ModelProvider.DEEPSEEK: "deepseek-chat",
            ModelProvider.MOONSHOT: "moonshot-v1-8k",
            ModelProvider.MINIMAX: "abab6.5-chat",
            ModelProvider.GOOGLE: "gemini-1.5-pro",
        }
