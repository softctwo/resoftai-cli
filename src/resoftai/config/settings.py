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

    # Anthropic API Configuration
    anthropic_api_key: str = Field(default="your_api_key_here")
    claude_model: str = Field(default="claude-3-5-sonnet-20241022")
    claude_max_tokens: int = Field(default=8192)
    claude_temperature: float = Field(default=0.7)

    # Platform Configuration
    workspace_dir: Path = Field(default=Path("/tmp/resoftai-workspace"))
    log_level: str = Field(default="INFO")

    # API Server Configuration
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_reload: bool = Field(default=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure workspace directory exists
        self.workspace_dir.mkdir(parents=True, exist_ok=True)


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
