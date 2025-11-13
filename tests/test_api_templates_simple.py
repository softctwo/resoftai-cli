"""Simplified tests for templates API routes without database."""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock

from resoftai.api.main import app
from resoftai.auth.dependencies import get_current_active_user


# Mock authentication dependency
async def mock_get_current_user():
    """Mock current user for testing."""
    user = MagicMock()
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.is_active = True
    user.role = "user"
    return user


@pytest.fixture
def override_auth():
    """Override authentication dependency."""
    app.dependency_overrides[get_current_active_user] = mock_get_current_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> dict:
    """Create mock authentication headers."""
    return {"Authorization": "Bearer mock_token"}


@pytest.mark.asyncio
async def test_list_templates(override_auth, auth_headers: dict):
    """Test listing all templates."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/templates", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3  # We have 3 built-in templates

    # Check template structure
    template = data[0]
    assert "id" in template
    assert "name" in template
    assert "description" in template
    assert "category" in template
    assert "tags" in template
    assert "file_count" in template
    assert "directory_count" in template


@pytest.mark.asyncio
async def test_list_templates_by_category(override_auth, auth_headers: dict):
    """Test filtering templates by category."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/templates?category=rest_api",
            headers=auth_headers
        )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # All returned templates should be REST API category
    for template in data:
        assert template["category"] == "rest_api"


@pytest.mark.asyncio
async def test_list_templates_by_tags(override_auth, auth_headers: dict):
    """Test filtering templates by tags."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/templates?tags=python,fastapi",
            headers=auth_headers
        )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    # At least one template should have python or fastapi tag
    for template in data:
        assert "python" in template["tags"] or "fastapi" in template["tags"]


@pytest.mark.asyncio
async def test_get_template(override_auth, auth_headers: dict):
    """Test getting template details."""
    template_id = "fastapi-rest-api"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/templates/{template_id}",
            headers=auth_headers
        )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == template_id
    assert "name" in data
    assert "description" in data
    assert "category" in data
    assert "variables" in data
    assert isinstance(data["variables"], list)

    # Check variable structure
    if data["variables"]:
        var = data["variables"][0]
        assert "name" in var
        assert "description" in var
        assert "required" in var
        assert "type" in var


@pytest.mark.asyncio
async def test_get_template_not_found(override_auth, auth_headers: dict):
    """Test getting non-existent template."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/templates/non-existent-template",
            headers=auth_headers
        )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_preview_template(override_auth, auth_headers: dict):
    """Test getting template preview."""
    template_id = "fastapi-rest-api"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/templates/{template_id}/preview",
            headers=auth_headers
        )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == template_id
    assert "files" in data
    assert "directories" in data
    assert "setup_commands" in data
    assert isinstance(data["files"], list)
    assert isinstance(data["directories"], list)
    assert isinstance(data["setup_commands"], list)


@pytest.mark.asyncio
async def test_list_categories(override_auth, auth_headers: dict):
    """Test listing template categories."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/templates/categories/list",
            headers=auth_headers
        )

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0
    assert "rest_api" in data
    assert "web_app" in data
    assert "cli_tool" in data


@pytest.mark.asyncio
async def test_template_api_requires_auth():
    """Test that template API requires authentication."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/templates")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_apply_template_validation(override_auth):
    """Test template application with missing required variables."""
    template_id = "python-cli-tool"
    request_data = {
        "project_id": 1,
        "variables": {
            # Missing required "project_name" variable
            "description": "A test CLI tool",
            "author": "Test Author"
        },
        "overwrite": False
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/templates/{template_id}/apply",
            json=request_data,
            headers={"Authorization": "Bearer mock_token"}
        )

    assert response.status_code == 400
    assert "validation failed" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_apply_template_not_found(override_auth):
    """Test applying non-existent template."""
    request_data = {
        "project_id": 1,
        "variables": {"project_name": "Test"},
        "overwrite": False
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/templates/non-existent/apply",
            json=request_data,
            headers={"Authorization": "Bearer mock_token"}
        )

    assert response.status_code == 404
