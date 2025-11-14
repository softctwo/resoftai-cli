"""Tests for plugin API routes."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from resoftai.models.plugin import Plugin, PluginCategory, PluginVersion
from resoftai.crud import plugin as plugin_crud


@pytest.mark.asyncio
async def test_list_plugins(client: AsyncClient, user_token: str, db: AsyncSession):
    """Test listing plugins in marketplace."""
    # Create test plugins
    plugin1 = await plugin_crud.create_plugin(
        db,
        name="Test Plugin 1",
        slug="test-plugin-1",
        category=PluginCategory.CODE_QUALITY,
        description="Test plugin 1",
        author="Test Author"
    )
    plugin2 = await plugin_crud.create_plugin(
        db,
        name="Test Plugin 2",
        slug="test-plugin-2",
        category=PluginCategory.INTEGRATION,
        description="Test plugin 2",
        author="Test Author"
    )
    await db.commit()

    response = await client.get(
        "/api/plugins",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_filter_plugins_by_category(client: AsyncClient, user_token: str, db: AsyncSession):
    """Test filtering plugins by category."""
    await plugin_crud.create_plugin(
        db,
        name="Code Quality Plugin",
        slug="code-quality",
        category=PluginCategory.CODE_QUALITY,
        description="Code quality plugin",
        author="Test"
    )
    await plugin_crud.create_plugin(
        db,
        name="Integration Plugin",
        slug="integration",
        category=PluginCategory.INTEGRATION,
        description="Integration plugin",
        author="Test"
    )
    await db.commit()

    response = await client.get(
        "/api/plugins?category=code_quality",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert all(p["category"] == "code_quality" for p in data)


@pytest.mark.asyncio
async def test_search_plugins(client: AsyncClient, user_token: str, db: AsyncSession):
    """Test searching plugins."""
    await plugin_crud.create_plugin(
        db,
        name="Security Scanner",
        slug="security-scanner",
        category=PluginCategory.CODE_QUALITY,
        description="Security vulnerability scanner",
        author="Test"
    )
    await plugin_crud.create_plugin(
        db,
        name="Slack Integration",
        slug="slack-integration",
        category=PluginCategory.INTEGRATION,
        description="Slack notifications",
        author="Test"
    )
    await db.commit()

    response = await client.get(
        "/api/plugins?search=security",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any("security" in p["name"].lower() or "security" in p["description"].lower() for p in data)


@pytest.mark.asyncio
async def test_get_plugin(client: AsyncClient, user_token: str, db: AsyncSession):
    """Test getting a specific plugin."""
    plugin = await plugin_crud.create_plugin(
        db,
        name="Test Plugin",
        slug="test-plugin",
        category=PluginCategory.AGENT,
        description="A test plugin",
        author="Test Author",
        homepage="https://example.com"
    )
    await db.commit()

    response = await client.get(
        f"/api/plugins/{plugin.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == plugin.id
    assert data["name"] == "Test Plugin"
    assert data["slug"] == "test-plugin"
    assert data["category"] == "agent"


@pytest.mark.asyncio
async def test_get_plugin_not_found(client: AsyncClient, user_token: str):
    """Test getting non-existent plugin returns 404."""
    response = await client.get(
        "/api/plugins/99999",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_install_plugin(client: AsyncClient, user_token: str, regular_user: User, db: AsyncSession):
    """Test installing a plugin."""
    plugin = await plugin_crud.create_plugin(
        db,
        name="Test Plugin",
        slug="test-plugin",
        category=PluginCategory.CODE_QUALITY,
        description="Test",
        author="Test"
    )
    version = await plugin_crud.create_plugin_version(
        db,
        plugin_id=plugin.id,
        version="1.0.0",
        min_platform_version="0.2.0"
    )
    await db.commit()

    response = await client.post(
        f"/api/plugins/{plugin.id}/install",
        json={
            "config": {
                "severity_threshold": "high"
            }
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["plugin_id"] == plugin.id
    assert data["user_id"] == regular_user.id
    assert data["enabled"] is True


@pytest.mark.asyncio
async def test_install_plugin_already_installed(client: AsyncClient, user_token: str, regular_user: User, db: AsyncSession):
    """Test installing an already installed plugin fails."""
    plugin = await plugin_crud.create_plugin(
        db,
        name="Test Plugin",
        slug="test-plugin",
        category=PluginCategory.CODE_QUALITY,
        description="Test",
        author="Test"
    )
    await plugin_crud.create_plugin_version(db, plugin_id=plugin.id, version="1.0.0", min_platform_version="0.2.0")
    await plugin_crud.install_plugin(db, plugin_id=plugin.id, user_id=regular_user.id)
    await db.commit()

    response = await client.post(
        f"/api/plugins/{plugin.id}/install",
        json={},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_uninstall_plugin(client: AsyncClient, user_token: str, regular_user: User, db: AsyncSession):
    """Test uninstalling a plugin."""
    plugin = await plugin_crud.create_plugin(
        db,
        name="Test Plugin",
        slug="test-plugin",
        category=PluginCategory.CODE_QUALITY,
        description="Test",
        author="Test"
    )
    await plugin_crud.create_plugin_version(db, plugin_id=plugin.id, version="1.0.0", min_platform_version="0.2.0")
    installation = await plugin_crud.install_plugin(db, plugin_id=plugin.id, user_id=regular_user.id)
    await db.commit()

    response = await client.delete(
        f"/api/plugins/{plugin.id}/uninstall",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_list_installed_plugins(client: AsyncClient, user_token: str, regular_user: User, db: AsyncSession):
    """Test listing installed plugins."""
    plugin = await plugin_crud.create_plugin(
        db,
        name="Test Plugin",
        slug="test-plugin",
        category=PluginCategory.CODE_QUALITY,
        description="Test",
        author="Test"
    )
    await plugin_crud.create_plugin_version(db, plugin_id=plugin.id, version="1.0.0", min_platform_version="0.2.0")
    await plugin_crud.install_plugin(db, plugin_id=plugin.id, user_id=regular_user.id)
    await db.commit()

    response = await client.get(
        "/api/plugins/installed",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(p["plugin_id"] == plugin.id for p in data)


@pytest.mark.asyncio
async def test_create_plugin_review(client: AsyncClient, user_token: str, regular_user: User, db: AsyncSession):
    """Test creating a plugin review."""
    plugin = await plugin_crud.create_plugin(
        db,
        name="Test Plugin",
        slug="test-plugin",
        category=PluginCategory.CODE_QUALITY,
        description="Test",
        author="Test"
    )
    await db.commit()

    response = await client.post(
        f"/api/plugins/{plugin.id}/reviews",
        json={
            "rating": 5,
            "comment": "Excellent plugin!"
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["plugin_id"] == plugin.id
    assert data["user_id"] == regular_user.id
    assert data["rating"] == 5
    assert data["comment"] == "Excellent plugin!"


@pytest.mark.asyncio
async def test_list_plugin_reviews(client: AsyncClient, user_token: str, regular_user: User, db: AsyncSession):
    """Test listing plugin reviews."""
    plugin = await plugin_crud.create_plugin(
        db,
        name="Test Plugin",
        slug="test-plugin",
        category=PluginCategory.CODE_QUALITY,
        description="Test",
        author="Test"
    )
    await plugin_crud.create_review(
        db,
        plugin_id=plugin.id,
        user_id=regular_user.id,
        rating=4,
        comment="Good plugin"
    )
    await db.commit()

    response = await client.get(
        f"/api/plugins/{plugin.id}/reviews",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_trending_plugins(client: AsyncClient, user_token: str, db: AsyncSession):
    """Test getting trending plugins."""
    plugin = await plugin_crud.create_plugin(
        db,
        name="Trending Plugin",
        slug="trending-plugin",
        category=PluginCategory.INTEGRATION,
        description="A trending plugin",
        author="Test",
        downloads=1000
    )
    await db.commit()

    response = await client.get(
        "/api/plugins/trending",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_plugin_pagination(client: AsyncClient, user_token: str, db: AsyncSession):
    """Test plugin listing pagination."""
    # Create multiple plugins
    for i in range(15):
        await plugin_crud.create_plugin(
            db,
            name=f"Plugin {i}",
            slug=f"plugin-{i}",
            category=PluginCategory.CODE_QUALITY,
            description=f"Plugin {i}",
            author="Test"
        )
    await db.commit()

    # Test with limit
    response = await client.get(
        "/api/plugins?skip=0&limit=10",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10

    # Test with offset
    response = await client.get(
        "/api/plugins?skip=10&limit=10",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5


@pytest.mark.asyncio
async def test_plugin_requires_authentication(client: AsyncClient):
    """Test that plugin endpoints require authentication."""
    response = await client.get("/api/plugins")
    assert response.status_code == 401

    response = await client.get("/api/plugins/1")
    assert response.status_code == 401

    response = await client.post("/api/plugins/1/install", json={})
    assert response.status_code == 401

    response = await client.get("/api/plugins/installed")
    assert response.status_code == 401
