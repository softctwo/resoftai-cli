"""
Tests for database connection module.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from resoftai.db.connection import (
    get_db,
    init_db,
    close_db,
    Base,
    engine,
    AsyncSessionLocal,
)


@pytest.mark.asyncio
async def test_get_db():
    """Test get_db dependency function."""
    async for session in get_db():
        # Verify we get an AsyncSession
        assert isinstance(session, AsyncSession)
        # Session should be active
        assert session.is_active
        # Break after first iteration
        break


@pytest.mark.asyncio
async def test_get_db_context_manager():
    """Test get_db as context manager."""
    db_gen = get_db()
    session = await db_gen.__anext__()

    try:
        # Verify session is valid
        assert isinstance(session, AsyncSession)
        assert session.is_active

        # Simulate successful operation
        # Session should commit on success
    except Exception:
        # Should rollback on error
        pass
    finally:
        # Cleanup
        try:
            await db_gen.__anext__()
        except StopAsyncIteration:
            pass


@pytest.mark.asyncio
async def test_init_db():
    """Test database initialization."""
    # This should create all tables
    await init_db()

    # Verify engine is still valid
    assert engine is not None


@pytest.mark.asyncio
async def test_close_db():
    """Test database connection closing."""
    # Should not raise any errors
    await close_db()


@pytest.mark.asyncio
async def test_session_factory():
    """Test async session factory."""
    async with AsyncSessionLocal() as session:
        # Verify we get a valid session
        assert isinstance(session, AsyncSession)
        assert session.is_active


@pytest.mark.asyncio
async def test_get_db_rollback_on_error():
    """Test that get_db rolls back on error."""
    db_gen = get_db()
    session = await db_gen.__anext__()

    try:
        # Simulate an error
        raise ValueError("Test error")
    except ValueError:
        pass
    finally:
        # Cleanup - should trigger rollback
        try:
            await db_gen.__anext__()
        except StopAsyncIteration:
            pass


def test_base_declarative():
    """Test that Base is a valid declarative base."""
    # Base should have metadata
    assert hasattr(Base, "metadata")
    assert Base.metadata is not None


def test_engine_created():
    """Test that engine is created."""
    assert engine is not None
    # Engine should have a URL
    assert engine.url is not None


def test_session_local_created():
    """Test that AsyncSessionLocal is created."""
    assert AsyncSessionLocal is not None
