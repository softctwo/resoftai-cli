"""
Settings and configuration management using environment variables.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Anthropic API Configuration
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    claude_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        env="CLAUDE_MODEL"
    )
    claude_max_tokens: int = Field(default=8192, env="CLAUDE_MAX_TOKENS")
    claude_temperature: float = Field(default=0.7, env="CLAUDE_TEMPERATURE")

    # Platform Configuration
    workspace_dir: Path = Field(
        default=Path("/tmp/resoftai-workspace"),
        env="RESOFTAI_WORKSPACE"
    )
    log_level: str = Field(default="INFO", env="RESOFTAI_LOG_LEVEL")

    # API Server Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_reload: bool = Field(default=False, env="API_RELOAD")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

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
