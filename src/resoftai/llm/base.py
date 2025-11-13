"""
Base classes for LLM provider abstraction.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum


class ModelProvider(str, Enum):
    """Supported LLM providers."""

    ANTHROPIC = "anthropic"  # Claude
    ZHIPU = "zhipu"  # 智谱 GLM
    DEEPSEEK = "deepseek"  # DeepSeek
    MOONSHOT = "moonshot"  # Kimi (月之暗面)
    MINIMAX = "minimax"  # Minimax
    GOOGLE = "google"  # Google Gemini
    OPENAI = "openai"  # OpenAI GPT (兼容)


@dataclass
class LLMConfig:
    """Configuration for LLM provider."""

    provider: ModelProvider
    api_key: str
    model_name: str
    api_base: Optional[str] = None
    max_tokens: int = 8192
    temperature: float = 0.7
    top_p: float = 0.95
    extra_params: Dict[str, Any] = None

    def __post_init__(self):
        if self.extra_params is None:
            self.extra_params = {}


@dataclass
class LLMResponse:
    """Standardized response from LLM providers."""

    content: str
    model: str
    provider: ModelProvider
    usage: Dict[str, int]
    raw_response: Optional[Any] = None

    @property
    def total_tokens(self) -> int:
        """Get total tokens used."""
        return self.usage.get("total_tokens", 0)


class LLMProvider(ABC):
    """
    Abstract base class for all LLM providers.

    All provider implementations must inherit from this class and implement
    the required methods.
    """

    def __init__(self, config: LLMConfig):
        """
        Initialize the LLM provider.

        Args:
            config: LLM configuration
        """
        self.config = config

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        pass

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from the LLM.

        Args:
            prompt: User prompt
            system_prompt: System prompt (instructions)
            **kwargs: Additional provider-specific parameters

        Returns:
            LLMResponse object
        """
        pass

    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        """
        Generate a streaming response from the LLM.

        Args:
            prompt: User prompt
            system_prompt: System prompt (instructions)
            **kwargs: Additional provider-specific parameters

        Yields:
            Chunks of generated text
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate the provider configuration.

        Returns:
            True if configuration is valid
        """
        pass

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.

        Returns:
            Dictionary with model information
        """
        return {
            "provider": self.config.provider.value,
            "model": self.config.model_name,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
        }
