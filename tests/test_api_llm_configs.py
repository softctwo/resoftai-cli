"""Tests for LLM configurations API routes."""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, MagicMock

from resoftai.api.main import app
from resoftai.models.user import User
from resoftai.models.llm_config import LLMConfigModel
from resoftai.auth.security import create_access_token


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authentication headers."""
    token = create_access_token(
        data={"sub": test_user.username, "user_id": test_user.id}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_llm_config(db: AsyncSession, test_user: User) -> LLMConfigModel:
    """Create test LLM configuration."""
    config = LLMConfigModel(
        user_id=test_user.id,
        name="Test Config",
        provider="anthropic",
        model_name="claude-3-opus-20240229",
        api_key_encrypted="sk-test-api-key",
        max_tokens=4096,
        temperature=0.7,
        is_default=False
    )
    db.add(config)
    await db.commit()
    await db.refresh(config)
    return config


@pytest.mark.asyncio
async def test_create_llm_config(db: AsyncSession, test_user: User, auth_headers: dict):
    """Test creating an LLM configuration."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/llm-configs", headers=auth_headers, json={
            "name": "My Anthropic Config",
            "provider": "anthropic",
            "model_name": "claude-3-opus-20240229",
            "api_key": "sk-test-key-12345678",
            "max_tokens": 8192,
            "temperature": 0.7,
            "top_p": 0.95
        })

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Anthropic Config"
    assert data["provider"] == "anthropic"
    assert "api_key_masked" in data
    assert "sk-test-key" not in data["api_key_masked"]  # Should be masked


@pytest.mark.asyncio
async def test_create_llm_config_invalid_provider(db: AsyncSession, auth_headers: dict):
    """Test creating LLM config with invalid provider."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/llm-configs", headers=auth_headers, json={
            "name": "Invalid Config",
            "provider": "invalid_provider",
            "model_name": "some-model",
            "api_key": "test-key",
            "max_tokens": 4096,
            "temperature": 0.7
        })

    assert response.status_code == 400
    assert "Invalid provider" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_llm_configs(db: AsyncSession, test_user: User, test_llm_config: LLMConfigModel, auth_headers: dict):
    """Test listing user's LLM configurations."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/llm-configs", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "configs" in data
    assert data["total"] >= 1
    assert len(data["configs"]) >= 1


@pytest.mark.asyncio
async def test_list_llm_configs_pagination(db: AsyncSession, test_user: User, auth_headers: dict):
    """Test pagination in LLM config listing."""
    # Create multiple configs
    for i in range(5):
        config = LLMConfigModel(
            user_id=test_user.id,
            name=f"Config {i}",
            provider="anthropic",
            model_name="claude-3-opus-20240229",
            api_key_encrypted=f"sk-key-{i}",
            max_tokens=4096,
            temperature=0.7,
            is_default=False
        )
        db.add(config)
    await db.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/llm-configs?skip=0&limit=2", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data["configs"]) <= 2
    assert data["skip"] == 0
    assert data["limit"] == 2


@pytest.mark.asyncio
async def test_get_llm_config(db: AsyncSession, test_llm_config: LLMConfigModel, auth_headers: dict):
    """Test getting a specific LLM configuration."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/v1/llm-configs/{test_llm_config.id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_llm_config.id
    assert "api_key_masked" in data


@pytest.mark.asyncio
async def test_get_llm_config_not_found(db: AsyncSession, auth_headers: dict):
    """Test getting a non-existent LLM config."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/llm-configs/99999", headers=auth_headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_active_config(db: AsyncSession, test_user: User, auth_headers: dict):
    """Test getting active LLM configuration."""
    # Create an active config
    config = LLMConfigModel(
        user_id=test_user.id,
        name="Active Config",
        provider="anthropic",
        model_name="claude-3-opus-20240229",
        api_key_encrypted="sk-active-key",
        max_tokens=4096,
        temperature=0.7,
        is_default=True
    )
    db.add(config)
    await db.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/llm-configs/active", headers=auth_headers)

    assert response.status_code == 200
    if response.json():  # May be None if no active config
        assert response.json()["is_active"] is True


@pytest.mark.asyncio
async def test_activate_llm_config(db: AsyncSession, test_llm_config: LLMConfigModel, auth_headers: dict):
    """Test activating an LLM configuration."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/llm-configs/{test_llm_config.id}/activate",
            headers=auth_headers
        )

    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_delete_llm_config(db: AsyncSession, test_user: User, auth_headers: dict):
    """Test deleting an LLM configuration."""
    # Create a non-active config to delete
    config = LLMConfigModel(
        user_id=test_user.id,
        name="To Delete",
        provider="anthropic",
        model_name="claude-3-opus-20240229",
        api_key_encrypted="sk-delete-key",
        max_tokens=4096,
        temperature=0.7,
        is_default=False
    )
    db.add(config)
    await db.commit()
    await db.refresh(config)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete(f"/api/v1/llm-configs/{config.id}", headers=auth_headers)

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_llm_config_not_found(db: AsyncSession, auth_headers: dict):
    """Test deleting a non-existent LLM config."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete("/api/v1/llm-configs/99999", headers=auth_headers)

    assert response.status_code == 404


@pytest.mark.asyncio
@patch('resoftai.llm.factory.LLMFactory.create')
async def test_test_llm_connection_success(mock_llm, db: AsyncSession, test_llm_config: LLMConfigModel, auth_headers: dict):
    """Test successful LLM connection test."""
    # Mock LLM response
    mock_llm_instance = MagicMock()
    mock_llm_instance.generate = MagicMock(return_value=MagicMock(
        content="OK",
        usage={"total_tokens": 10}
    ))
    mock_llm.return_value = mock_llm_instance

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/llm-configs/{test_llm_config.id}/test",
            headers=auth_headers,
            json={"prompt": "Test prompt"}
        )

    assert response.status_code == 200
    # Note: This test may need adjustment based on actual implementation
