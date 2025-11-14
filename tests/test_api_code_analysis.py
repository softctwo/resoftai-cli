"""Tests for code analysis API routes."""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from resoftai.api.main import app
from resoftai.models.user import User
from resoftai.auth.security import create_access_token


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authentication headers."""
    token = create_access_token(
        data={"sub": test_user.username, "user_id": test_user.id}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_analyze_python_code(db: AsyncSession, auth_headers: dict):
    """Test analyzing Python code with pylint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/code-analysis/analyze",
            headers=auth_headers,
            json={
                "code": "def hello_world():\n    print('Hello, World!')\n",
                "language": "python",
                "filename": "hello",
                "tools": ["all"]
            }
        )

    assert response.status_code == 200
    data = response.json()
    assert "issues" in data
    assert "summary" in data
    assert data["language"] == "python"
    assert "execution_time" in data


@pytest.mark.asyncio
async def test_analyze_invalid_language(db: AsyncSession, auth_headers: dict):
    """Test analyzing code with unsupported language."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/code-analysis/analyze",
            headers=auth_headers,
            json={
                "code": "some code",
                "language": "cobol",
                "filename": "test"
            }
        )

    assert response.status_code == 400
    assert "Unsupported language" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_available_tools(db: AsyncSession, auth_headers: dict):
    """Test getting available analysis tools."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/code-analysis/tools",
            headers=auth_headers
        )

    assert response.status_code == 200
    data = response.json()
    assert "available_tools" in data
    assert "supported_languages" in data
    assert "python" in data["supported_languages"]


@pytest.mark.asyncio
async def test_analyze_code_missing_auth(db: AsyncSession):
    """Test analyzing code without authentication."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/code-analysis/analyze",
            json={
                "code": "def test(): pass",
                "language": "python",
                "filename": "test"
            }
        )

    assert response.status_code == 401
