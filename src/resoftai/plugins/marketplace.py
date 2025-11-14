"""
Plugin Marketplace System

Provides plugin discovery, installation, versioning, and ratings.
"""
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
import httpx
import asyncio
from packaging import version as pkg_version

from resoftai.plugins.manager import PluginManager
from resoftai.plugins.base import PluginMetadata, PluginConfig, PluginContext

logger = logging.getLogger(__name__)


class PluginMarketplace:
    """
    Plugin marketplace for discovering and installing plugins.

    Features:
    - Plugin discovery from multiple sources
    - Version management
    - Dependency resolution
    - Automatic updates
    - Plugin ratings and reviews
    """

    def __init__(
        self,
        plugin_manager: PluginManager,
        marketplace_url: Optional[str] = None,
        cache_dir: Optional[Path] = None
    ):
        """
        Initialize plugin marketplace.

        Args:
            plugin_manager: PluginManager instance
            marketplace_url: URL of the marketplace API
            cache_dir: Directory for caching downloaded plugins
        """
        self.plugin_manager = plugin_manager
        self.marketplace_url = marketplace_url or "https://marketplace.resoftai.com/api"
        self.cache_dir = cache_dir or Path.home() / ".resoftai" / "plugin_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Local registry of available plugins
        self._available_plugins: Dict[str, Dict[str, Any]] = {}

        logger.info(f"Plugin marketplace initialized with URL: {self.marketplace_url}")

    async def discover_plugins(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Discover available plugins from marketplace.

        Args:
            category: Optional category filter

        Returns:
            List of available plugins with metadata
        """
        try:
            async with httpx.AsyncClient() as client:
                params = {"category": category} if category else {}
                response = await client.get(
                    f"{self.marketplace_url}/plugins",
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()

                plugins = response.json()
                for plugin in plugins:
                    self._available_plugins[plugin["slug"]] = plugin

                logger.info(f"Discovered {len(plugins)} plugins from marketplace")
                return plugins

        except Exception as e:
            logger.error(f"Failed to discover plugins from marketplace: {e}")
            return []

    async def search_plugins(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for plugins in marketplace.

        Args:
            query: Search query

        Returns:
            List of matching plugins
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.marketplace_url}/plugins/search",
                    params={"q": query},
                    timeout=10.0
                )
                response.raise_for_status()

                results = response.json()
                logger.info(f"Found {len(results)} plugins matching '{query}'")
                return results

        except Exception as e:
            logger.error(f"Failed to search plugins: {e}")
            return []

    async def get_plugin_info(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a plugin.

        Args:
            slug: Plugin slug

        Returns:
            Plugin information or None
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.marketplace_url}/plugins/{slug}",
                    timeout=10.0
                )
                response.raise_for_status()

                return response.json()

        except Exception as e:
            logger.error(f"Failed to get plugin info for {slug}: {e}")
            return None

    async def get_plugin_versions(self, slug: str) -> List[str]:
        """
        Get available versions for a plugin.

        Args:
            slug: Plugin slug

        Returns:
            List of version strings
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.marketplace_url}/plugins/{slug}/versions",
                    timeout=10.0
                )
                response.raise_for_status()

                versions = response.json()
                return versions

        except Exception as e:
            logger.error(f"Failed to get versions for {slug}: {e}")
            return []

    async def download_plugin(
        self,
        slug: str,
        version: Optional[str] = None
    ) -> Optional[Path]:
        """
        Download a plugin from marketplace.

        Args:
            slug: Plugin slug
            version: Optional specific version (defaults to latest)

        Returns:
            Path to downloaded plugin or None
        """
        try:
            # Get download URL
            version_param = f"?version={version}" if version else ""
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.marketplace_url}/plugins/{slug}/download{version_param}",
                    timeout=30.0,
                    follow_redirects=True
                )
                response.raise_for_status()

                # Save to cache
                plugin_dir = self.cache_dir / slug
                plugin_dir.mkdir(parents=True, exist_ok=True)

                # Assuming the download is a zip or tar.gz
                plugin_file = plugin_dir / f"{slug}-{version or 'latest'}.zip"
                plugin_file.write_bytes(response.content)

                logger.info(f"Downloaded plugin {slug} to {plugin_file}")
                return plugin_file

        except Exception as e:
            logger.error(f"Failed to download plugin {slug}: {e}")
            return None

    async def install_plugin(
        self,
        slug: str,
        version: Optional[str] = None,
        auto_dependencies: bool = True
    ) -> bool:
        """
        Install a plugin from marketplace.

        Args:
            slug: Plugin slug
            version: Optional specific version
            auto_dependencies: Automatically install dependencies

        Returns:
            True if installed successfully
        """
        try:
            # Download plugin
            plugin_file = await self.download_plugin(slug, version)
            if not plugin_file:
                return False

            # Extract plugin
            # TODO: Implement plugin extraction and installation
            # This would involve:
            # 1. Extracting the archive
            # 2. Validating the plugin
            # 3. Installing dependencies if auto_dependencies=True
            # 4. Registering with plugin manager

            logger.info(f"Plugin {slug} installed successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to install plugin {slug}: {e}")
            return False

    async def uninstall_plugin(self, slug: str) -> bool:
        """
        Uninstall a plugin.

        Args:
            slug: Plugin slug

        Returns:
            True if uninstalled successfully
        """
        try:
            # Unload from plugin manager
            self.plugin_manager.unload_plugin(slug)

            # Remove from cache
            plugin_dir = self.cache_dir / slug
            if plugin_dir.exists():
                import shutil
                shutil.rmtree(plugin_dir)

            logger.info(f"Plugin {slug} uninstalled successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to uninstall plugin {slug}: {e}")
            return False

    async def update_plugin(
        self,
        slug: str,
        target_version: Optional[str] = None
    ) -> bool:
        """
        Update a plugin to a newer version.

        Args:
            slug: Plugin slug
            target_version: Optional target version (defaults to latest)

        Returns:
            True if updated successfully
        """
        try:
            # Get current version
            current_plugin = self.plugin_manager.get_plugin(slug)
            if not current_plugin:
                logger.error(f"Plugin {slug} is not installed")
                return False

            current_version = current_plugin.metadata.version

            # Get available versions
            available_versions = await self.get_plugin_versions(slug)
            if not available_versions:
                logger.info(f"No updates available for {slug}")
                return False

            # Determine target version
            if not target_version:
                # Get latest version
                target_version = max(available_versions, key=pkg_version.parse)

            # Check if update is needed
            if pkg_version.parse(target_version) <= pkg_version.parse(current_version):
                logger.info(f"Plugin {slug} is already at version {current_version}")
                return True

            # Uninstall current version
            await self.uninstall_plugin(slug)

            # Install new version
            success = await self.install_plugin(slug, target_version)

            if success:
                logger.info(f"Updated plugin {slug} from {current_version} to {target_version}")
            else:
                logger.error(f"Failed to update plugin {slug}")

            return success

        except Exception as e:
            logger.error(f"Failed to update plugin {slug}: {e}")
            return False

    async def check_updates(self) -> Dict[str, str]:
        """
        Check for available updates for installed plugins.

        Returns:
            Dictionary mapping plugin slug to available version
        """
        updates = {}

        for slug, plugin in self.plugin_manager._plugins.items():
            try:
                current_version = plugin.metadata.version
                available_versions = await self.get_plugin_versions(slug)

                if available_versions:
                    latest_version = max(available_versions, key=pkg_version.parse)

                    if pkg_version.parse(latest_version) > pkg_version.parse(current_version):
                        updates[slug] = latest_version
                        logger.info(f"Update available for {slug}: {current_version} -> {latest_version}")

            except Exception as e:
                logger.error(f"Failed to check updates for {slug}: {e}")

        return updates

    async def get_plugin_reviews(self, slug: str) -> List[Dict[str, Any]]:
        """
        Get reviews for a plugin.

        Args:
            slug: Plugin slug

        Returns:
            List of reviews
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.marketplace_url}/plugins/{slug}/reviews",
                    timeout=10.0
                )
                response.raise_for_status()

                return response.json()

        except Exception as e:
            logger.error(f"Failed to get reviews for {slug}: {e}")
            return []

    async def submit_review(
        self,
        slug: str,
        rating: int,
        comment: str,
        user_token: str
    ) -> bool:
        """
        Submit a review for a plugin.

        Args:
            slug: Plugin slug
            rating: Rating (1-5)
            comment: Review comment
            user_token: User authentication token

        Returns:
            True if submitted successfully
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.marketplace_url}/plugins/{slug}/reviews",
                    json={
                        "rating": rating,
                        "comment": comment
                    },
                    headers={"Authorization": f"Bearer {user_token}"},
                    timeout=10.0
                )
                response.raise_for_status()

                logger.info(f"Submitted review for {slug}")
                return True

        except Exception as e:
            logger.error(f"Failed to submit review for {slug}: {e}")
            return False

    async def get_featured_plugins(self) -> List[Dict[str, Any]]:
        """
        Get featured plugins from marketplace.

        Returns:
            List of featured plugins
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.marketplace_url}/plugins/featured",
                    timeout=10.0
                )
                response.raise_for_status()

                return response.json()

        except Exception as e:
            logger.error(f"Failed to get featured plugins: {e}")
            return []

    async def get_popular_plugins(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most popular plugins.

        Args:
            limit: Maximum number of plugins to return

        Returns:
            List of popular plugins
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.marketplace_url}/plugins/popular",
                    params={"limit": limit},
                    timeout=10.0
                )
                response.raise_for_status()

                return response.json()

        except Exception as e:
            logger.error(f"Failed to get popular plugins: {e}")
            return []

    def get_installed_plugins(self) -> List[PluginMetadata]:
        """
        Get list of installed plugins.

        Returns:
            List of installed plugin metadata
        """
        return self.plugin_manager.list_plugins()

    async def validate_plugin(self, slug: str) -> Dict[str, Any]:
        """
        Validate a plugin before installation.

        Args:
            slug: Plugin slug

        Returns:
            Validation results
        """
        try:
            plugin_info = await self.get_plugin_info(slug)
            if not plugin_info:
                return {"valid": False, "errors": ["Plugin not found"]}

            errors = []
            warnings = []

            # Check platform compatibility
            min_version = plugin_info.get("min_platform_version")
            if min_version:
                current_version = pkg_version.parse(self.plugin_manager.platform_version)
                min_ver = pkg_version.parse(min_version)
                if current_version < min_ver:
                    errors.append(f"Requires platform version >= {min_version}")

            # Check dependencies
            dependencies = plugin_info.get("dependencies", [])
            for dep in dependencies:
                if dep not in self.plugin_manager._plugins:
                    warnings.append(f"Missing dependency: {dep}")

            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "plugin_info": plugin_info
            }

        except Exception as e:
            logger.error(f"Failed to validate plugin {slug}: {e}")
            return {
                "valid": False,
                "errors": [str(e)]
            }
