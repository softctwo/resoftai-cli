"""Tests for files API routes."""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from resoftai.api.main import app
from resoftai.models.user import User
from resoftai.models.project import Project
from resoftai.models.file import File
from resoftai.auth.security import create_access_token


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authentication headers."""
    token = create_access_token(
        data={"sub": test_user.username, "user_id": test_user.id}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_file(db: AsyncSession, test_project: Project, test_user: User) -> File:
    """Create test file."""
    file = File(
        project_id=test_project.id,
        path="test.py",
        content="print('Hello World')",
        language="python",
        current_version=1
    )
    db.add(file)
    await db.commit()
    await db.refresh(file)
    return file


@pytest.mark.asyncio
async def test_create_file(db: AsyncSession, test_project: Project, test_user: User, auth_headers: dict):
    """Test creating a file."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/files", headers=auth_headers, json={
            "project_id": test_project.id,
            "path": "main.py",
            "content": "def main():\n    pass",
            "language": "python"
        })

    assert response.status_code == 201
    data = response.json()
    assert data["path"] == "main.py"
    assert data["project_id"] == test_project.id
    assert data["language"] == "python"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_file_duplicate_path(db: AsyncSession, test_project: Project, test_file: File, auth_headers: dict):
    """Test creating a file with duplicate path."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/files", headers=auth_headers, json={
            "project_id": test_project.id,
            "path": test_file.path,
            "content": "some content",
            "language": "python"
        })

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_file_project_not_found(db: AsyncSession, auth_headers: dict):
    """Test creating a file in non-existent project."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/files", headers=auth_headers, json={
            "project_id": 99999,
            "path": "test.py",
            "content": "test",
            "language": "python"
        })

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_files(db: AsyncSession, test_project: Project, test_file: File, auth_headers: dict):
    """Test listing files in a project."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/files?project_id={test_project.id}",
            headers=auth_headers
        )

    assert response.status_code == 200
    data = response.json()
    assert "files" in data
    assert data["total"] >= 1
    assert len(data["files"]) >= 1


@pytest.mark.asyncio
async def test_list_files_pagination(db: AsyncSession, test_project: Project, test_user: User, auth_headers: dict):
    """Test pagination in file listing."""
    # Create multiple files
    for i in range(5):
        file = File(
            project_id=test_project.id,
            path=f"file{i}.py",
            content=f"# File {i}",
            language="python",
            current_version=1
        )
        db.add(file)
    await db.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/files?project_id={test_project.id}&skip=0&limit=2",
            headers=auth_headers
        )

    assert response.status_code == 200
    data = response.json()
    assert len(data["files"]) <= 2
    assert data["skip"] == 0
    assert data["limit"] == 2


@pytest.mark.asyncio
async def test_get_file(db: AsyncSession, test_project: Project, test_file: File, auth_headers: dict):
    """Test getting a specific file."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/v1/files/{test_file.id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_file.id
    assert data["path"] == test_file.path


@pytest.mark.asyncio
async def test_get_file_not_found(db: AsyncSession, auth_headers: dict):
    """Test getting a non-existent file."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/files/99999", headers=auth_headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_file(db: AsyncSession, test_file: File, auth_headers: dict):
    """Test updating a file."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(
            f"/api/v1/files/{test_file.id}",
            headers=auth_headers,
            json={"content": "print('Updated content')"}
        )

    assert response.status_code == 200
    data = response.json()
    assert "Updated content" in data["content"]
    # Version should increment
    assert data["current_version"] > test_file.current_version


@pytest.mark.asyncio
async def test_update_file_not_found(db: AsyncSession, auth_headers: dict):
    """Test updating a non-existent file."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(
            "/api/v1/files/99999",
            headers=auth_headers,
            json={"content": "test"}
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_file(db: AsyncSession, test_project: Project, test_user: User, auth_headers: dict):
    """Test deleting a file."""
    # Create a file to delete
    file = File(
        project_id=test_project.id,
        path="to_delete.py",
        content="# To be deleted",
        language="python",
        current_version=1
    )
    db.add(file)
    await db.commit()
    await db.refresh(file)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete(f"/api/v1/files/{file.id}", headers=auth_headers)

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_file_not_found(db: AsyncSession, auth_headers: dict):
    """Test deleting a non-existent file."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete("/api/v1/files/99999", headers=auth_headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_file_versions(db: AsyncSession, test_file: File, auth_headers: dict):
    """Test listing file versions."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/files/{test_file.id}/versions",
            headers=auth_headers
        )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_file_versions_not_found(db: AsyncSession, auth_headers: dict):
    """Test listing versions of non-existent file."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/files/99999/versions",
            headers=auth_headers
        )

    assert response.status_code == 404
