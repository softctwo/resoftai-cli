"""
Tests for plugin CRUD operations
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from resoftai.crud import plugin as plugin_crud
from resoftai.models.plugin import PluginCategory, PluginStatus


@pytest.mark.asyncio
async def test_create_plugin(db: AsyncSession):
    """Test creating a plugin"""
    plugin = await plugin_crud.create_plugin(
        db=db,
        name="Test Plugin",
        slug="test-plugin",
        category=PluginCategory.CODE_QUALITY,
        version="1.0.0",
        description="A test plugin"
    )

    assert plugin.id is not None
    assert plugin.name == "Test Plugin"
    assert plugin.slug == "test-plugin"
    assert plugin.category == PluginCategory.CODE_QUALITY


@pytest.mark.asyncio
async def test_search_plugins(db: AsyncSession):
    """Test searching plugins"""
    # Create test plugins
    await plugin_crud.create_plugin(
        db=db,
        name="Security Scanner",
        slug="security-scanner-test",
        category=PluginCategory.CODE_QUALITY,
        version="1.0.0",
        description="Scans for security vulnerabilities",
        status=PluginStatus.APPROVED
    )

    await plugin_crud.create_plugin(
        db=db,
        name="Code Formatter",
        slug="code-formatter-test",
        category=PluginCategory.CODE_QUALITY,
        version="1.0.0",
        description="Formats code automatically",
        status=PluginStatus.APPROVED
    )

    # Search
    results = await plugin_crud.search_plugins(
        db=db,
        query_text="security"
    )

    assert len(results) >= 1
    assert any(p.name == "Security Scanner" for p in results)
