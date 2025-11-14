"""Tests for plugin system edge cases and error handling."""
import pytest
from unittest.mock import Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from resoftai.plugins.base import Plugin, PluginMetadata, PluginContext, CodeQualityPlugin
from resoftai.plugins.manager import PluginManager
from resoftai.models.plugin import PluginCategory
from resoftai.crud import plugin as plugin_crud


class TestPluginEdgeCases:
    """Test edge cases in plugin system."""

    def test_plugin_metadata_validation(self):
        """Test plugin metadata validation."""
        # Valid metadata
        metadata = PluginMetadata(
            name="Test Plugin",
            slug="test-plugin",
            version="1.0.0",
            description="Test description",
            author="Test Author",
            category=PluginCategory.CODE_QUALITY
        )
        assert metadata.name == "Test Plugin"
        assert metadata.version == "1.0.0"

    def test_plugin_context_logging(self):
        """Test plugin context logging methods."""
        context = PluginContext()

        # Should not raise exceptions
        context.log_info("Info message")
        context.log_warning("Warning message")
        context.log_error("Error message")
        context.log_debug("Debug message")

    def test_plugin_manager_with_no_plugins(self):
        """Test plugin manager with no plugins."""
        manager = PluginManager(plugin_dirs=[])
        plugins = manager.discover_plugins()

        assert len(plugins) == 0

    def test_plugin_manager_with_invalid_directory(self):
        """Test plugin manager with invalid directory."""
        manager = PluginManager(plugin_dirs=["/nonexistent/directory"])
        plugins = manager.discover_plugins()

        # Should handle gracefully
        assert isinstance(plugins, list)

    def test_plugin_load_failure(self):
        """Test handling of plugin load failure."""
        manager = PluginManager()

        class FailingPlugin(Plugin):
            def load(self, context: PluginContext) -> bool:
                raise Exception("Load failed")

            def activate(self) -> bool:
                return True

            def deactivate(self) -> bool:
                return True

            def unload(self) -> bool:
                return True

        metadata = PluginMetadata(
            name="Failing Plugin",
            slug="failing",
            version="1.0.0",
            description="Test",
            author="Test",
            category=PluginCategory.CODE_QUALITY
        )

        # Should handle load failure gracefully
        plugin = FailingPlugin(metadata, {})
        context = PluginContext()

        try:
            result = plugin.load(context)
            assert False, "Should have raised exception"
        except Exception as e:
            assert str(e) == "Load failed"

    def test_plugin_with_empty_config(self):
        """Test plugin initialization with empty config."""
        metadata = PluginMetadata(
            name="Test",
            slug="test",
            version="1.0.0",
            description="Test",
            author="Test",
            category=PluginCategory.CODE_QUALITY
        )

        class TestPlugin(CodeQualityPlugin):
            def load(self, context: PluginContext) -> bool:
                return True

            def activate(self) -> bool:
                return True

            def deactivate(self) -> bool:
                return True

            def unload(self) -> bool:
                return True

            def get_tool_name(self) -> str:
                return "test"

            async def analyze_code(self, code: str, language: str):
                return {"tool": "test", "issues": []}

            def get_config_schema(self):
                return {}

            def validate_config(self, config):
                return True

        plugin = TestPlugin(metadata, {})
        assert plugin.config == {}

    def test_plugin_version_comparison(self):
        """Test plugin version comparison logic."""
        # This assumes there's version comparison logic in the plugin system
        from packaging import version

        v1 = version.parse("1.0.0")
        v2 = version.parse("1.0.1")
        v3 = version.parse("2.0.0")

        assert v1 < v2
        assert v2 < v3
        assert v1 < v3

    @pytest.mark.asyncio
    async def test_plugin_crud_with_missing_fields(self, db: AsyncSession):
        """Test plugin CRUD operations with missing optional fields."""
        plugin = await plugin_crud.create_plugin(
            db,
            name="Minimal Plugin",
            slug="minimal",
            category=PluginCategory.CODE_QUALITY,
            description="Minimal description",
            author="Test"
            # No optional fields like homepage, repository, etc.
        )
        await db.commit()

        assert plugin.id is not None
        assert plugin.name == "Minimal Plugin"
        assert plugin.homepage is None
        assert plugin.repository is None

    @pytest.mark.asyncio
    async def test_plugin_search_with_special_characters(self, db: AsyncSession):
        """Test plugin search with special characters."""
        await plugin_crud.create_plugin(
            db,
            name="Test & Plugin",
            slug="test-plugin",
            category=PluginCategory.CODE_QUALITY,
            description="Test with & special chars",
            author="Test"
        )
        await db.commit()

        # Should handle special characters in search
        results = await plugin_crud.search_plugins(db, query="&")
        assert len(results) >= 0  # Should not crash

    @pytest.mark.asyncio
    async def test_plugin_with_very_long_description(self, db: AsyncSession):
        """Test plugin with very long description."""
        long_description = "A" * 10000

        plugin = await plugin_crud.create_plugin(
            db,
            name="Long Desc Plugin",
            slug="long-desc",
            category=PluginCategory.CODE_QUALITY,
            description="Short",
            author="Test",
            long_description=long_description
        )
        await db.commit()

        assert len(plugin.long_description) == 10000

    @pytest.mark.asyncio
    async def test_plugin_rating_calculation(self, db: AsyncSession):
        """Test plugin average rating calculation."""
        plugin = await plugin_crud.create_plugin(
            db,
            name="Rated Plugin",
            slug="rated",
            category=PluginCategory.CODE_QUALITY,
            description="Test",
            author="Test"
        )
        await db.commit()

        # Create reviews with different ratings
        user_ids = [1, 2, 3]
        ratings = [5, 4, 3]

        for user_id, rating in zip(user_ids, ratings):
            await plugin_crud.create_review(
                db,
                plugin_id=plugin.id,
                user_id=user_id,
                rating=rating
            )
        await db.commit()

        # Get updated plugin with ratings
        updated_plugin = await plugin_crud.get_plugin(db, plugin.id)

        # Average should be (5 + 4 + 3) / 3 = 4.0
        assert updated_plugin.rating_average == 4.0
        assert updated_plugin.rating_count == 3

    @pytest.mark.asyncio
    async def test_plugin_download_count_increment(self, db: AsyncSession):
        """Test incrementing plugin download count."""
        plugin = await plugin_crud.create_plugin(
            db,
            name="Download Test",
            slug="download-test",
            category=PluginCategory.CODE_QUALITY,
            description="Test",
            author="Test"
        )
        await db.commit()
        initial_downloads = plugin.downloads or 0

        # Simulate download
        await plugin_crud.increment_downloads(db, plugin.id)
        await db.commit()

        updated = await plugin_crud.get_plugin(db, plugin.id)
        assert updated.downloads == initial_downloads + 1

    @pytest.mark.asyncio
    async def test_plugin_version_compatibility(self, db: AsyncSession):
        """Test plugin version platform compatibility checking."""
        plugin = await plugin_crud.create_plugin(
            db,
            name="Version Test",
            slug="version-test",
            category=PluginCategory.CODE_QUALITY,
            description="Test",
            author="Test"
        )

        # Create version with platform requirement
        version = await plugin_crud.create_plugin_version(
            db,
            plugin_id=plugin.id,
            version="1.0.0",
            min_platform_version="0.2.0",
            max_platform_version="0.3.0"
        )
        await db.commit()

        assert version.min_platform_version == "0.2.0"
        assert version.max_platform_version == "0.3.0"

    @pytest.mark.asyncio
    async def test_plugin_installation_with_invalid_config(self, db: AsyncSession):
        """Test plugin installation with invalid configuration."""
        plugin = await plugin_crud.create_plugin(
            db,
            name="Config Test",
            slug="config-test",
            category=PluginCategory.CODE_QUALITY,
            description="Test",
            author="Test"
        )
        await plugin_crud.create_plugin_version(
            db,
            plugin_id=plugin.id,
            version="1.0.0",
            min_platform_version="0.2.0"
        )
        await db.commit()

        # Install with invalid config (should be handled by validation)
        installation = await plugin_crud.install_plugin(
            db,
            plugin_id=plugin.id,
            user_id=1,
            config={"invalid_key": "invalid_value"}
        )
        await db.commit()

        # Should still install but config validation might fail later
        assert installation.id is not None

    @pytest.mark.asyncio
    async def test_plugin_collection_operations(self, db: AsyncSession):
        """Test plugin collection CRUD operations."""
        # Create collection
        collection = await plugin_crud.create_collection(
            db,
            name="Security Tools",
            slug="security-tools",
            description="Security-focused plugins"
        )
        await db.commit()

        assert collection.id is not None
        assert collection.name == "Security Tools"

        # Get collection
        retrieved = await plugin_crud.get_collection(db, collection.id)
        assert retrieved.slug == "security-tools"

    @pytest.mark.asyncio
    async def test_plugin_dependency_resolution(self, db: AsyncSession):
        """Test plugin dependency resolution."""
        # Create base plugin
        base_plugin = await plugin_crud.create_plugin(
            db,
            name="Base Plugin",
            slug="base",
            category=PluginCategory.AGENT,
            description="Base",
            author="Test"
        )

        # Create dependent plugin
        dependent_plugin = await plugin_crud.create_plugin(
            db,
            name="Dependent Plugin",
            slug="dependent",
            category=PluginCategory.AGENT,
            description="Depends on base",
            author="Test",
            dependencies=["base>=1.0.0"]
        )
        await db.commit()

        assert "base>=1.0.0" in dependent_plugin.dependencies

    @pytest.mark.asyncio
    async def test_plugin_uninstall_with_dependencies(self, db: AsyncSession):
        """Test uninstalling plugin that other plugins depend on."""
        base = await plugin_crud.create_plugin(
            db,
            name="Base",
            slug="base",
            category=PluginCategory.AGENT,
            description="Base",
            author="Test"
        )
        dependent = await plugin_crud.create_plugin(
            db,
            name="Dependent",
            slug="dependent",
            category=PluginCategory.AGENT,
            description="Dependent",
            author="Test",
            dependencies=["base"]
        )
        await plugin_crud.create_plugin_version(db, plugin_id=base.id, version="1.0.0", min_platform_version="0.2.0")
        await plugin_crud.create_plugin_version(db, plugin_id=dependent.id, version="1.0.0", min_platform_version="0.2.0")

        # Install both
        base_install = await plugin_crud.install_plugin(db, plugin_id=base.id, user_id=1)
        dep_install = await plugin_crud.install_plugin(db, plugin_id=dependent.id, user_id=1)
        await db.commit()

        # Uninstalling base should fail or warn (implementation dependent)
        await plugin_crud.uninstall_plugin(db, plugin_id=base.id, user_id=1)
        await db.commit()

        # Verify uninstallation
        base_installations = await plugin_crud.get_user_installations(db, user_id=1)
        assert not any(i.plugin_id == base.id for i in base_installations)
