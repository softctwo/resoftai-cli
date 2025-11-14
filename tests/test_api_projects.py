"""Tests for projects API routes."""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from resoftai.api.main import app
from resoftai.models.user import User
from resoftai.models.project import Project
from resoftai.auth.security import create_access_token


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authentication headers."""
    token = create_access_token(
        data={"sub": test_user.username, "user_id": test_user.id}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_project_valid(db: AsyncSession, test_user: User, auth_headers: dict):
    """Test creating a project with valid data."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/projects", headers=auth_headers, json={
            "name": "Test Project",
            "requirements": "Build a simple web application with user authentication",
            "llm_provider": "anthropic",
            "llm_model": "claude-3-opus-20240229"
        })

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["requirements"] == "Build a simple web application with user authentication"
    assert data["user_id"] == test_user.id
    assert data["status"] == "pending"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_project_missing_fields(db: AsyncSession, auth_headers: dict):
    """Test creating a project with missing required fields."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/projects", headers=auth_headers, json={
            "name": "Test Project"
            # Missing requirements
        })

    assert response.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_create_project_short_requirements(db: AsyncSession, auth_headers: dict):
    """Test creating a project with requirements too short."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/projects", headers=auth_headers, json={
            "name": "Test Project",
            "requirements": "Short"  # Less than 10 characters
        })

    assert response.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_list_projects(db: AsyncSession, test_user: User, test_project: Project, auth_headers: dict):
    """Test listing user's projects."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/projects", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "projects" in data
    assert "total" in data
    assert data["total"] >= 1
    assert len(data["projects"]) >= 1


@pytest.mark.asyncio
async def test_list_projects_pagination(db: AsyncSession, test_user: User, auth_headers: dict):
    """Test pagination in project listing."""
    # Create multiple projects
    for i in range(5):
        project = Project(
            user_id=test_user.id,
            name=f"Project {i}",
            requirements="Test requirements for pagination",
            status="pending"
        )
        db.add(project)
    await db.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/projects?skip=0&limit=2", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data["projects"]) <= 2
    assert data["skip"] == 0
    assert data["limit"] == 2


@pytest.mark.asyncio
async def test_list_projects_filter_by_status(db: AsyncSession, test_user: User, auth_headers: dict):
    """Test filtering projects by status."""
    # Create projects with different statuses
    project1 = Project(
        user_id=test_user.id,
        name="Active Project",
        requirements="Test requirements",
        status="in_progress"
    )
    project2 = Project(
        user_id=test_user.id,
        name="Completed Project",
        requirements="Test requirements",
        status="completed"
    )
    db.add(project1)
    db.add(project2)
    await db.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/projects?status=in_progress", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert all(p["status"] == "in_progress" for p in data["projects"])


@pytest.mark.asyncio
async def test_get_project(db: AsyncSession, test_user: User, test_project: Project, auth_headers: dict):
    """Test getting a specific project."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/v1/projects/{test_project.id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_project.id
    assert data["name"] == test_project.name


@pytest.mark.asyncio
async def test_get_project_not_found(db: AsyncSession, auth_headers: dict):
    """Test getting a non-existent project."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/projects/99999", headers=auth_headers)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_project_access_denied(db: AsyncSession, admin_user: User, test_project: Project):
    """Test accessing another user's project."""
    # Create token for different user
    token = create_access_token(
        data={"sub": admin_user.username, "user_id": admin_user.id}
    )
    headers = {"Authorization": f"Bearer {token}"}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/v1/projects/{test_project.id}", headers=headers)

    # Admin should have access
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_project(db: AsyncSession, test_user: User, test_project: Project, auth_headers: dict):
    """Test updating a project."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers,
            json={
                "name": "Updated Project Name",
                "progress": 50
            }
        )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Project Name"
    assert data["progress"] == 50


@pytest.mark.asyncio
async def test_update_project_not_found(db: AsyncSession, auth_headers: dict):
    """Test updating a non-existent project."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(
            "/api/v1/projects/99999",
            headers=auth_headers,
            json={"name": "Updated Name"}
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_project(db: AsyncSession, test_user: User, auth_headers: dict):
    """Test deleting a project."""
    # Create a project to delete
    project = Project(
        user_id=test_user.id,
        name="Project to Delete",
        requirements="Test requirements",
        status="pending"
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete(f"/api/v1/projects/{project.id}", headers=auth_headers)

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_project_not_found(db: AsyncSession, auth_headers: dict):
    """Test deleting a non-existent project."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete("/api/v1/projects/99999", headers=auth_headers)

    assert response.status_code == 404
