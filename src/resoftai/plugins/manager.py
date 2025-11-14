"""
Plugin Manager - Plugin Lifecycle and Registry

Manages plugin discovery, loading, activation, and execution.
Provides the central registry for all plugins in the system.
"""
import importlib
import importlib.util
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Type, Any
import logging
import json
from packaging import version as pkg_version

from resoftai.plugins.base import (
    Plugin, PluginMetadata, PluginConfig, PluginContext,
    PluginError, PluginLoadError, PluginDependencyError, PluginVersionError
)
from resoftai.plugins.hooks import HookManager

logger = logging.getLogger(__name__)


class PluginManager:
    """
    Central plugin manager for the ResoftAI platform

    Responsibilities:
    - Plugin discovery and registration
    - Plugin lifecycle management (load, activate, deactivate, unload)
    - Dependency resolution
    - Hook management
    """

    def __init__(self, plugin_dirs: List[Path], platform_version: str = "0.2.0"):
        """
        Initialize the plugin manager

        Args:
            plugin_dirs: List of directories to search for plugins
            platform_version: Current platform version for compatibility checks
        """
        self.plugin_dirs = [Path(d) for d in plugin_dirs]
        self.platform_version = platform_version

        # Plugin registry: slug -> Plugin instance
        self._plugins: Dict[str, Plugin] = {}

        # Plugin metadata registry: slug -> PluginMetadata
        self._metadata: Dict[str, PluginMetadata] = {}

        # Plugin configurations: slug -> PluginConfig
        self._configs: Dict[str, PluginConfig] = {}

        # Load order (for dependency resolution)
        self._load_order: List[str] = []

        # Hook manager
        self.hooks = HookManager()

        logger.info(f"PluginManager initialized with platform version {platform_version}")

    def discover_plugins(self) -> List[PluginMetadata]:
        """
        Discover all available plugins in plugin directories

        Searches for plugin.json manifest files and loads metadata.

        Returns:
            List of discovered plugin metadata
        """
        discovered = []

        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                logger.warning(f"Plugin directory does not exist: {plugin_dir}")
                continue

            logger.info(f"Scanning for plugins in: {plugin_dir}")

            # Look for plugin.json files
            for manifest_path in plugin_dir.rglob("plugin.json"):
                try:
                    metadata = self._load_plugin_manifest(manifest_path)
                    discovered.append(metadata)
                    self._metadata[metadata.slug] = metadata
                    logger.info(f"Discovered plugin: {metadata.slug} v{metadata.version}")
                except Exception as e:
                    logger.error(f"Error loading plugin manifest {manifest_path}: {e}")

        logger.info(f"Discovered {len(discovered)} plugins")
        return discovered

    def _load_plugin_manifest(self, manifest_path: Path) -> PluginMetadata:
        """
        Load plugin metadata from manifest file

        Args:
            manifest_path: Path to plugin.json

        Returns:
            PluginMetadata object

        Raises:
            PluginLoadError: If manifest is invalid
        """
        try:
            with open(manifest_path, 'r') as f:
                data = json.load(f)

            # Set entry point relative to manifest directory
            plugin_dir = manifest_path.parent
            if "entry_point" in data:
                data["entry_point"] = str(plugin_dir / data["entry_point"])

            return PluginMetadata(**data)
        except Exception as e:
            raise PluginLoadError(f"Failed to load manifest {manifest_path}: {e}")

    def register_plugin(self, plugin_class: Type[Plugin], metadata: PluginMetadata,
                       config: Optional[PluginConfig] = None) -> bool:
        """
        Register a plugin programmatically

        Args:
            plugin_class: Plugin class
            metadata: Plugin metadata
            config: Plugin configuration (optional)

        Returns:
            True if registered successfully
        """
        if metadata.slug in self._plugins:
            logger.warning(f"Plugin {metadata.slug} is already registered")
            return False

        try:
            # Create plugin instance
            plugin_config = config or PluginConfig()
            plugin = plugin_class(metadata, plugin_config)

            # Validate plugin
            self._validate_plugin(plugin)

            # Register
            self._plugins[metadata.slug] = plugin
            self._metadata[metadata.slug] = metadata
            self._configs[metadata.slug] = plugin_config

            logger.info(f"Registered plugin: {metadata.slug}")
            return True

        except Exception as e:
            logger.error(f"Failed to register plugin {metadata.slug}: {e}")
            return False

    def load_plugin(self, slug: str, context: PluginContext) -> bool:
        """
        Load a plugin

        Args:
            slug: Plugin slug identifier
            context: Plugin context

        Returns:
            True if loaded successfully
        """
        if slug not in self._metadata:
            logger.error(f"Plugin {slug} not found in registry")
            return False

        if slug in self._plugins and self._plugins[slug].is_loaded:
            logger.warning(f"Plugin {slug} is already loaded")
            return True

        metadata = self._metadata[slug]

        try:
            # Check version compatibility
            self._check_version_compatibility(metadata)

            # Resolve and load dependencies
            self._load_dependencies(metadata, context)

            # Load plugin if not already loaded
            if slug not in self._plugins:
                plugin = self._import_plugin(metadata)
                config = self._configs.get(slug, PluginConfig())
                plugin = plugin(metadata, config)
                self._plugins[slug] = plugin

            plugin = self._plugins[slug]

            # Initialize plugin
            plugin.context = context
            if plugin.load(context):
                plugin._loaded = True
                plugin._load_time = None  # Set actual time
                self._load_order.append(slug)
                logger.info(f"Loaded plugin: {slug}")
                return True
            else:
                logger.error(f"Plugin {slug} load() returned False")
                return False

        except Exception as e:
            logger.error(f"Failed to load plugin {slug}: {e}")
            raise PluginLoadError(f"Failed to load plugin {slug}: {e}")

    def activate_plugin(self, slug: str) -> bool:
        """
        Activate a loaded plugin

        Args:
            slug: Plugin slug identifier

        Returns:
            True if activated successfully
        """
        if slug not in self._plugins:
            logger.error(f"Plugin {slug} not loaded")
            return False

        plugin = self._plugins[slug]

        if not plugin.is_loaded:
            logger.error(f"Plugin {slug} must be loaded before activation")
            return False

        if plugin.is_active:
            logger.warning(f"Plugin {slug} is already active")
            return True

        try:
            if plugin.activate():
                plugin._active = True
                logger.info(f"Activated plugin: {slug}")
                return True
            else:
                logger.error(f"Plugin {slug} activate() returned False")
                return False
        except Exception as e:
            logger.error(f"Failed to activate plugin {slug}: {e}")
            return False

    def deactivate_plugin(self, slug: str) -> bool:
        """
        Deactivate an active plugin

        Args:
            slug: Plugin slug identifier

        Returns:
            True if deactivated successfully
        """
        if slug not in self._plugins:
            logger.error(f"Plugin {slug} not found")
            return False

        plugin = self._plugins[slug]

        if not plugin.is_active:
            logger.warning(f"Plugin {slug} is not active")
            return True

        try:
            if plugin.deactivate():
                plugin._active = False
                logger.info(f"Deactivated plugin: {slug}")
                return True
            else:
                logger.error(f"Plugin {slug} deactivate() returned False")
                return False
        except Exception as e:
            logger.error(f"Failed to deactivate plugin {slug}: {e}")
            return False

    def unload_plugin(self, slug: str) -> bool:
        """
        Unload a plugin

        Args:
            slug: Plugin slug identifier

        Returns:
            True if unloaded successfully
        """
        if slug not in self._plugins:
            logger.warning(f"Plugin {slug} not loaded")
            return True

        plugin = self._plugins[slug]

        try:
            # Deactivate first if active
            if plugin.is_active:
                self.deactivate_plugin(slug)

            # Unload
            if plugin.unload():
                plugin._loaded = False
                if slug in self._load_order:
                    self._load_order.remove(slug)
                logger.info(f"Unloaded plugin: {slug}")
                return True
            else:
                logger.error(f"Plugin {slug} unload() returned False")
                return False
        except Exception as e:
            logger.error(f"Failed to unload plugin {slug}: {e}")
            return False

    def get_plugin(self, slug: str) -> Optional[Plugin]:
        """
        Get a plugin instance

        Args:
            slug: Plugin slug identifier

        Returns:
            Plugin instance or None
        """
        return self._plugins.get(slug)

    def list_plugins(self, active_only: bool = False) -> List[PluginMetadata]:
        """
        List all plugins

        Args:
            active_only: Only return active plugins

        Returns:
            List of plugin metadata
        """
        if active_only:
            return [
                self._metadata[slug]
                for slug, plugin in self._plugins.items()
                if plugin.is_active
            ]
        else:
            return list(self._metadata.values())

    def _validate_plugin(self, plugin: Plugin):
        """
        Validate plugin implementation

        Args:
            plugin: Plugin to validate

        Raises:
            PluginValidationError: If validation fails
        """
        # Validate metadata
        metadata = plugin.metadata
        if not metadata.name or not metadata.slug:
            raise PluginError("Plugin must have name and slug")

        # Validate configuration
        config_schema = plugin.get_config_schema()
        if config_schema and not plugin.validate_config(plugin.config.config):
            raise PluginError("Plugin configuration is invalid")

    def _check_version_compatibility(self, metadata: PluginMetadata):
        """
        Check if plugin is compatible with platform version

        Args:
            metadata: Plugin metadata

        Raises:
            PluginVersionError: If version is incompatible
        """
        current = pkg_version.parse(self.platform_version)

        if metadata.min_platform_version:
            min_ver = pkg_version.parse(metadata.min_platform_version)
            if current < min_ver:
                raise PluginVersionError(
                    f"Plugin {metadata.slug} requires platform version >= {metadata.min_platform_version}, "
                    f"but current version is {self.platform_version}"
                )

        if metadata.max_platform_version:
            max_ver = pkg_version.parse(metadata.max_platform_version)
            if current > max_ver:
                raise PluginVersionError(
                    f"Plugin {metadata.slug} requires platform version <= {metadata.max_platform_version}, "
                    f"but current version is {self.platform_version}"
                )

    def _load_dependencies(self, metadata: PluginMetadata, context: PluginContext):
        """
        Load plugin dependencies

        Args:
            metadata: Plugin metadata
            context: Plugin context

        Raises:
            PluginDependencyError: If dependency cannot be loaded
        """
        for dep_slug in metadata.dependencies:
            if dep_slug not in self._metadata:
                raise PluginDependencyError(f"Dependency {dep_slug} not found")

            # Load dependency if not already loaded
            if dep_slug not in self._plugins or not self._plugins[dep_slug].is_loaded:
                logger.info(f"Loading dependency: {dep_slug}")
                if not self.load_plugin(dep_slug, context):
                    raise PluginDependencyError(f"Failed to load dependency {dep_slug}")

    def _import_plugin(self, metadata: PluginMetadata) -> Type[Plugin]:
        """
        Dynamically import plugin class

        Args:
            metadata: Plugin metadata

        Returns:
            Plugin class

        Raises:
            PluginLoadError: If import fails
        """
        if not metadata.entry_point:
            raise PluginLoadError(f"Plugin {metadata.slug} has no entry_point")

        try:
            # Parse entry point: "path/to/module.py:ClassName"
            if ":" in metadata.entry_point:
                module_path, class_name = metadata.entry_point.rsplit(":", 1)
            else:
                raise PluginLoadError("entry_point must be in format 'module.py:ClassName'")

            # Load module
            module_path = Path(module_path)
            if not module_path.exists():
                raise PluginLoadError(f"Module file not found: {module_path}")

            spec = importlib.util.spec_from_file_location(f"plugin_{metadata.slug}", module_path)
            if spec is None or spec.loader is None:
                raise PluginLoadError(f"Failed to load module spec for {module_path}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[f"plugin_{metadata.slug}"] = module
            spec.loader.exec_module(module)

            # Get plugin class
            plugin_class = getattr(module, class_name)

            if not issubclass(plugin_class, Plugin):
                raise PluginLoadError(f"{class_name} is not a Plugin subclass")

            return plugin_class

        except Exception as e:
            raise PluginLoadError(f"Failed to import plugin {metadata.slug}: {e}")

    def shutdown(self):
        """
        Shutdown plugin manager and unload all plugins
        """
        logger.info("Shutting down plugin manager")

        # Unload in reverse order
        for slug in reversed(self._load_order):
            try:
                self.unload_plugin(slug)
            except Exception as e:
                logger.error(f"Error unloading plugin {slug}: {e}")

        self._plugins.clear()
        self._load_order.clear()
        logger.info("Plugin manager shutdown complete")
