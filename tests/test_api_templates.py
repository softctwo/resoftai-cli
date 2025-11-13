"""Tests for templates API routes."""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from resoftai.api.main import app
from resoftai.models.user import User
from resoftai.models.project import Project
from resoftai.auth.security import create_access_token


@pytest.fixture
async def test_project(db: AsyncSession, test_user: User) -> Project:
    """Create test project."""
    project = Project(
        name="Test Project",
        requirements="Test requirements for template application",
        status="draft",
        progress=0,
        user_id=test_user.id
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authentication headers."""
    token = create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_list_templates(auth_headers: dict):
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
async def test_list_templates_by_category(auth_headers: dict):
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
async def test_list_templates_by_tags(auth_headers: dict):
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
async def test_get_template(auth_headers: dict):
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
async def test_get_template_not_found(auth_headers: dict):
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
async def test_preview_template(auth_headers: dict):
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
async def test_preview_template_not_found(auth_headers: dict):
    """Test previewing non-existent template."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/templates/non-existent/preview",
            headers=auth_headers
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_apply_template_success(auth_headers: dict, test_project: Project):
    """Test applying template to project."""
    template_id = "python-cli-tool"
    request_data = {
        "project_id": test_project.id,
        "variables": {
            "project_name": "MyCLI",
            "description": "A test CLI tool",
            "author": "Test Author",
            "command_name": "mycli"
        },
        "overwrite": False
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/templates/{template_id}/apply",
            json=request_data,
            headers=auth_headers
        )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["project_id"] == test_project.id
    assert "application started" in data["message"].lower()


@pytest.mark.asyncio
async def test_apply_template_missing_required_variable(auth_headers: dict, test_project: Project):
    """Test applying template with missing required variables."""
    template_id = "python-cli-tool"
    request_data = {
        "project_id": test_project.id,
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
            headers=auth_headers
        )

    assert response.status_code == 400
    assert "validation failed" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_apply_template_not_found(auth_headers: dict, test_project: Project):
    """Test applying non-existent template."""
    request_data = {
        "project_id": test_project.id,
        "variables": {"project_name": "Test"},
        "overwrite": False
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/templates/non-existent/apply",
            json=request_data,
            headers=auth_headers
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_categories(auth_headers: dict):
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
async def test_template_with_optional_variables(auth_headers: dict, test_project: Project):
    """Test applying template with optional variables."""
    template_id = "python-cli-tool"
    request_data = {
        "project_id": test_project.id,
        "variables": {
            "project_name": "MyCLI",  # Required
            # Optional variables will use defaults
        },
        "overwrite": True
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/templates/{template_id}/apply",
            json=request_data,
            headers=auth_headers
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
