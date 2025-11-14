"""Fixtures for API tests."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from resoftai.models.user import User
from resoftai.crud.user import create_user
from resoftai.auth import create_access_token


@pytest.fixture
async def admin_user(db: AsyncSession) -> User:
    """Create an admin user for testing."""
    user = await create_user(
        db,
        username="admin",
        email="admin@test.com",
        password="admin123",
        is_admin=True
    )
    await db.commit()
    return user


@pytest.fixture
async def regular_user(db: AsyncSession) -> User:
    """Create a regular user for testing."""
    user = await create_user(
        db,
        username="user",
        email="user@test.com",
        password="user123",
        is_admin=False
    )
    await db.commit()
    return user


@pytest.fixture
async def admin_token(admin_user: User) -> str:
    """Create access token for admin user."""
    return create_access_token(data={"sub": admin_user.username, "user_id": admin_user.id})


@pytest.fixture
async def user_token(regular_user: User) -> str:
    """Create access token for regular user."""
    return create_access_token(data={"sub": regular_user.username, "user_id": regular_user.id})


@pytest.fixture
async def client(app) -> AsyncClient:
    """Create async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
