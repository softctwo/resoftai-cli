"""
Tests for plugin management system
"""
import pytest
from pathlib import Path

from resoftai.plugins.manager import PluginManager
from resoftai.plugins.base import PluginContext, PluginMetadata, PluginConfig


def test_plugin_manager_init():
    """Test plugin manager initialization"""
    manager = PluginManager(plugin_dirs=[Path("/tmp/plugins")], platform_version="0.2.0")

    assert manager.platform_version == "0.2.0"
    assert len(manager._plugins) == 0


def test_plugin_metadata():
    """Test plugin metadata creation"""
    metadata = PluginMetadata(
        name="Test Plugin",
        slug="test-plugin",
        version="1.0.0",
        description="A test plugin",
        author="Test Author"
    )

    assert metadata.name == "Test Plugin"
    assert metadata.slug == "test-plugin"
    assert metadata.version == "1.0.0"


def test_plugin_config():
    """Test plugin configuration"""
    config = PluginConfig(
        enabled=True,
        config={"key": "value"},
        auto_update=False
    )

    assert config.enabled is True
    assert config.get("key") == "value"
    assert config.get("nonexistent", "default") == "default"

    # Test set
    config.set("new_key", "new_value")
    assert config.get("new_key") == "new_value"


def test_plugin_context():
    """Test plugin context"""
    context = PluginContext()

    # Test data storage
    context.set_data("key", "value")
    assert context.get_data("key") == "value"
    assert context.get_data("nonexistent", "default") == "default"
