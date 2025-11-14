"""
Tests for configuration settings module.
"""
import os
import tempfile
from pathlib import Path
import pytest
from resoftai.config.settings import Settings, get_settings


def test_settings_defaults():
    """Test that settings have proper default values."""
    settings = Settings()

    assert settings.llm_provider == "anthropic"
    assert settings.llm_model == "claude-3-5-sonnet-20241022"
    assert settings.llm_max_tokens == 8192
    assert settings.llm_temperature == 0.7
    assert settings.llm_top_p == 0.95
    assert settings.api_host == "0.0.0.0"
    assert settings.api_port == 8000
    assert settings.jwt_algorithm == "HS256"
    assert settings.jwt_access_token_expire_minutes == 30
    assert settings.jwt_refresh_token_expire_days == 7


def test_settings_from_env(monkeypatch):
    """Test that settings can be loaded from environment variables."""
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("LLM_API_KEY", "test-api-key")
    monkeypatch.setenv("LLM_MODEL", "deepseek-chat")
    monkeypatch.setenv("API_PORT", "9000")

    settings = Settings()

    assert settings.llm_provider == "deepseek"
    assert settings.llm_api_key == "test-api-key"
    assert settings.llm_model == "deepseek-chat"
    assert settings.api_port == 9000


def test_workspace_directory_creation():
    """Test that workspace directory is created on initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace_path = Path(tmpdir) / "test_workspace"
        settings = Settings(workspace_dir=workspace_path)

        assert workspace_path.exists()
        assert workspace_path.is_dir()


def test_backward_compatibility_anthropic_api_key(monkeypatch):
    """Test backward compatibility with anthropic_api_key."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "legacy-api-key")

    settings = Settings()

    # Should use anthropic_api_key when llm_api_key is default
    assert settings.llm_api_key == "legacy-api-key"
    assert settings.llm_provider == "anthropic"


def test_backward_compatibility_claude_model(monkeypatch):
    """Test backward compatibility with claude_model."""
    monkeypatch.setenv("CLAUDE_MODEL", "claude-3-opus-20240229")

    settings = Settings()

    # Should store claude_model in the field
    assert settings.claude_model == "claude-3-opus-20240229"


def test_get_llm_config():
    """Test that get_llm_config returns proper LLMConfig."""
    settings = Settings(
        llm_provider="deepseek",
        llm_api_key="test-key",
        llm_model="deepseek-chat",
        llm_max_tokens=4096,
        llm_temperature=0.5,
        llm_top_p=0.9
    )

    config = settings.get_llm_config()

    assert str(config.provider.value) == "deepseek"
    assert config.api_key == "test-key"
    assert config.model_name == "deepseek-chat"
    assert config.max_tokens == 4096
    assert config.temperature == 0.5
    assert config.top_p == 0.9


def test_get_settings_singleton():
    """Test that get_settings returns the same instance."""
    settings1 = get_settings()
    settings2 = get_settings()

    assert settings1 is settings2


def test_database_url_default(monkeypatch):
    """Test database URL default value."""
    # Clear any DATABASE_URL from environment
    monkeypatch.delenv("DATABASE_URL", raising=False)

    settings = Settings()

    # Should have a valid database URL
    assert settings.database_url is not None
    assert len(settings.database_url) > 0
    # In clean environment, defaults to PostgreSQL
    if "DATABASE_URL" not in os.environ:
        assert "postgresql" in settings.database_url or "sqlite" in settings.database_url


def test_api_configuration():
    """Test API configuration settings."""
    settings = Settings(
        api_host="127.0.0.1",
        api_port=5000,
        api_reload=True,
        api_enable_websocket=False
    )

    assert settings.api_host == "127.0.0.1"
    assert settings.api_port == 5000
    assert settings.api_reload is True
    assert settings.api_enable_websocket is False


def test_jwt_configuration():
    """Test JWT configuration settings."""
    settings = Settings(
        jwt_secret_key="custom-secret",
        jwt_algorithm="HS512",
        jwt_access_token_expire_minutes=60,
        jwt_refresh_token_expire_days=14
    )

    assert settings.jwt_secret_key == "custom-secret"
    assert settings.jwt_algorithm == "HS512"
    assert settings.jwt_access_token_expire_minutes == 60
    assert settings.jwt_refresh_token_expire_days == 14
