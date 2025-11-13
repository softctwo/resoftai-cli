"""Pytest configuration and shared fixtures."""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from resoftai.db.base import Base
from resoftai.models.user import User
from resoftai.models.project import Project
from resoftai.config import Settings


# Test database URL - use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def test_settings():
    """Create test settings."""
    return Settings(
        database_url=TEST_DATABASE_URL,
        jwt_secret_key="test-secret-key",
        jwt_algorithm="HS256",
        access_token_expire_minutes=30
    )


@pytest.fixture
async def test_user(db: AsyncSession) -> User:
    """Create test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="$2b$12$test_hashed_password",
        full_name="Test User",
        role="user",
        is_active=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def admin_user(db: AsyncSession) -> User:
    """Create admin user."""
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password="$2b$12$admin_hashed_password",
        full_name="Admin User",
        role="admin",
        is_active=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def test_project(db: AsyncSession, test_user: User) -> Project:
    """Create test project."""
    from resoftai.models.project import ProjectStatus

    project = Project(
        user_id=test_user.id,
        name="Test Project",
        description="A test project",
        requirements="Build a simple web application with user authentication",
        status=ProjectStatus.PENDING
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


# Mock LLM responses for testing
@pytest.fixture
def mock_llm_response():
    """Mock LLM response."""
    return {
        "content": "This is a mock LLM response",
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }


# Mock authentication
@pytest.fixture
def mock_auth_token():
    """Mock JWT token for testing."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token"


@pytest.fixture
def auth_headers(mock_auth_token):
    """Create authentication headers."""
    return {
        "Authorization": f"Bearer {mock_auth_token}"
    }
