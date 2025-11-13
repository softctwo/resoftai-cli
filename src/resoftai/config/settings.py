"""
Settings and configuration management using environment variables.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # LLM Provider Configuration
    llm_provider: str = Field(default="anthropic")  # anthropic, zhipu, deepseek, moonshot, minimax, google
    llm_api_key: str = Field(default="your_api_key_here")
    llm_model: str = Field(default="claude-3-5-sonnet-20241022")
    llm_api_base: Optional[str] = Field(default=None)
    llm_max_tokens: int = Field(default=8192)
    llm_temperature: float = Field(default=0.7)
    llm_top_p: float = Field(default=0.95)

    # Legacy Anthropic Configuration (for backward compatibility)
    anthropic_api_key: Optional[str] = Field(default=None)
    claude_model: Optional[str] = Field(default=None)
    claude_max_tokens: Optional[int] = Field(default=None)
    claude_temperature: Optional[float] = Field(default=None)

    # Platform Configuration
    workspace_dir: Path = Field(default=Path("/tmp/resoftai-workspace"))
    log_level: str = Field(default="INFO")

    # API Server Configuration
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_reload: bool = Field(default=False)
    api_enable_websocket: bool = Field(default=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure workspace directory exists
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        # Backward compatibility: use anthropic_ settings if llm_ not set
        if self.anthropic_api_key and self.llm_api_key == "your_api_key_here":
            self.llm_api_key = self.anthropic_api_key
            self.llm_provider = "anthropic"
        if self.claude_model and not self.llm_model:
            self.llm_model = self.claude_model

    def get_llm_config(self):
        """
        Get LLM configuration for the factory.

        Returns:
            LLMConfig object
        """
        from resoftai.llm.base import LLMConfig, ModelProvider

        return LLMConfig(
            provider=ModelProvider(self.llm_provider),
            api_key=self.llm_api_key,
            model_name=self.llm_model,
            api_base=self.llm_api_base,
            max_tokens=self.llm_max_tokens,
            temperature=self.llm_temperature,
            top_p=self.llm_top_p,
        )


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
