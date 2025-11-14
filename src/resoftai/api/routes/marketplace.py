"""Plugin marketplace API routes."""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from resoftai.auth.dependencies import get_current_active_user
from resoftai.models.user import User
from resoftai.plugins.marketplace import PluginMarketplace
from resoftai.plugins.manager import PluginManager
from resoftai.plugins.base import PluginMetadata

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


# Request/Response Models
class PluginInfoResponse(BaseModel):
    """Plugin information response."""
    slug: str
    name: str
    version: str
    author: str
    description: str
    category: str
    tags: List[str] = Field(default_factory=list)
    downloads: int = 0
    rating: float = 0.0
    review_count: int = 0
    min_platform_version: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    homepage: Optional[str] = None
    repository: Optional[str] = None


class PluginInstallRequest(BaseModel):
    """Plugin installation request."""
    slug: str
    version: Optional[str] = None
    auto_dependencies: bool = True


class PluginReviewRequest(BaseModel):
    """Plugin review submission request."""
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=10, max_length=1000)


class PluginReviewResponse(BaseModel):
    """Plugin review response."""
    id: int
    user_name: str
    rating: int
    comment: str
    created_at: str
    helpful_count: int = 0


class ValidationResponse(BaseModel):
    """Plugin validation response."""
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    plugin_info: Optional[Dict[str, Any]] = None


class UpdateCheckResponse(BaseModel):
    """Update check response."""
    updates_available: Dict[str, str]  # slug -> new version
    total_updates: int


# Global marketplace instance (would be initialized at app startup)
_marketplace: Optional[PluginMarketplace] = None


def get_marketplace() -> PluginMarketplace:
    """Get plugin marketplace instance."""
    global _marketplace
    if _marketplace is None:
        # Initialize with default settings
        # In production, this would be configured properly
        from pathlib import Path
        plugin_manager = PluginManager(
            plugin_dirs=[Path("./plugins")],
            platform_version="0.2.2"
        )
        _marketplace = PluginMarketplace(plugin_manager)
    return _marketplace


@router.get("/plugins", response_model=List[PluginInfoResponse])
async def discover_plugins(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    marketplace: PluginMarketplace = Depends(get_marketplace)
) -> List[Dict[str, Any]]:
    """
    Discover available plugins from marketplace.

    Args:
        category: Optional category filter

    Returns:
        List of available plugins
    """
    plugins = await marketplace.discover_plugins(category)
    return plugins


@router.get("/plugins/search", response_model=List[PluginInfoResponse])
async def search_plugins(
    q: str = Query(..., min_length=2),
    current_user: User = Depends(get_current_active_user),
    marketplace: PluginMarketplace = Depends(get_marketplace)
) -> List[Dict[str, Any]]:
    """
    Search for plugins in marketplace.

    Args:
        q: Search query

    Returns:
        List of matching plugins
    """
    results = await marketplace.search_plugins(q)
    return results


@router.get("/plugins/featured", response_model=List[PluginInfoResponse])
async def get_featured_plugins(
    current_user: User = Depends(get_current_active_user),
    marketplace: PluginMarketplace = Depends(get_marketplace)
) -> List[Dict[str, Any]]:
    """
    Get featured plugins.

    Returns:
        List of featured plugins
    """
    plugins = await marketplace.get_featured_plugins()
    return plugins


@router.get("/plugins/popular", response_model=List[PluginInfoResponse])
async def get_popular_plugins(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    marketplace: PluginMarketplace = Depends(get_marketplace)
) -> List[Dict[str, Any]]:
    """
    Get popular plugins.

    Args:
        limit: Maximum number of results

    Returns:
        List of popular plugins
    """
    plugins = await marketplace.get_popular_plugins(limit)
    return plugins


@router.get("/plugins/installed", response_model=List[PluginInfoResponse])
async def get_installed_plugins(
    current_user: User = Depends(get_current_active_user),
    marketplace: PluginMarketplace = Depends(get_marketplace)
) -> List[Dict[str, Any]]:
    """
    Get installed plugins.

    Returns:
        List of installed plugins
    """
    plugins = marketplace.get_installed_plugins()
    return [
        {
            "slug": p.slug,
            "name": p.name,
            "version": p.version,
            "author": p.author,
            "description": p.description,
            "category": p.category,
            "tags": p.tags or [],
            "dependencies": p.dependencies or [],
            "homepage": p.homepage,
            "repository": p.repository,
            "downloads": 0,  # Not tracked locally
            "rating": 0.0,
            "review_count": 0
        }
        for p in plugins
    ]


@router.get("/plugins/{slug}", response_model=PluginInfoResponse)
async def get_plugin_details(
    slug: str,
    current_user: User = Depends(get_current_active_user),
    marketplace: PluginMarketplace = Depends(get_marketplace)
) -> Dict[str, Any]:
    """
    Get detailed plugin information.

    Args:
        slug: Plugin slug

    Returns:
        Plugin details
    """
    plugin_info = await marketplace.get_plugin_info(slug)
    if not plugin_info:
        raise HTTPException(status_code=404, detail="Plugin not found")

    return plugin_info


@router.get("/plugins/{slug}/versions")
async def get_plugin_versions(
    slug: str,
    current_user: User = Depends(get_current_active_user),
    marketplace: PluginMarketplace = Depends(get_marketplace)
) -> List[str]:
    """
    Get available versions for a plugin.

    Args:
        slug: Plugin slug

    Returns:
        List of version strings
    """
    versions = await marketplace.get_plugin_versions(slug)
    return versions


@router.post("/plugins/{slug}/install")
async def install_plugin(
    slug: str,
    request: PluginInstallRequest,
    current_user: User = Depends(get_current_active_user),
    marketplace: PluginMarketplace = Depends(get_marketplace)
) -> Dict[str, str]:
    """
    Install a plugin.

    Args:
        slug: Plugin slug
        request: Installation options

    Returns:
        Installation status
    """
    # Validate plugin first
    validation = await marketplace.validate_plugin(slug)
    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail={"errors": validation["errors"]}
        )

    # Install plugin
    success = await marketplace.install_plugin(
        slug,
        request.version,
        request.auto_dependencies
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to install plugin")

    return {"message": f"Plugin {slug} installed successfully"}


@router.post("/plugins/{slug}/uninstall")
async def uninstall_plugin(
    slug: str,
    current_user: User = Depends(get_current_active_user),
    marketplace: PluginMarketplace = Depends(get_marketplace)
) -> Dict[str, str]:
    """
    Uninstall a plugin.

    Args:
        slug: Plugin slug

    Returns:
        Uninstallation status
    """
    success = await marketplace.uninstall_plugin(slug)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to uninstall plugin")

    return {"message": f"Plugin {slug} uninstalled successfully"}


@router.post("/plugins/{slug}/update")
async def update_plugin(
    slug: str,
    target_version: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    marketplace: PluginMarketplace = Depends(get_marketplace)
) -> Dict[str, str]:
    """
    Update a plugin to a newer version.

    Args:
        slug: Plugin slug
        target_version: Optional target version

    Returns:
        Update status
    """
    success = await marketplace.update_plugin(slug, target_version)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to update plugin")

    return {"message": f"Plugin {slug} updated successfully"}


@router.get("/updates/check", response_model=UpdateCheckResponse)
async def check_updates(
    current_user: User = Depends(get_current_active_user),
    marketplace: PluginMarketplace = Depends(get_marketplace)
) -> Dict[str, Any]:
    """
    Check for available plugin updates.

    Returns:
        Available updates
    """
    updates = await marketplace.check_updates()

    return {
        "updates_available": updates,
        "total_updates": len(updates)
    }


@router.get("/plugins/{slug}/reviews", response_model=List[PluginReviewResponse])
async def get_plugin_reviews(
    slug: str,
    current_user: User = Depends(get_current_active_user),
    marketplace: PluginMarketplace = Depends(get_marketplace)
) -> List[Dict[str, Any]]:
    """
    Get reviews for a plugin.

    Args:
        slug: Plugin slug

    Returns:
        List of reviews
    """
    reviews = await marketplace.get_plugin_reviews(slug)
    return reviews


@router.post("/plugins/{slug}/reviews")
async def submit_review(
    slug: str,
    review: PluginReviewRequest,
    current_user: User = Depends(get_current_active_user),
    marketplace: PluginMarketplace = Depends(get_marketplace)
) -> Dict[str, str]:
    """
    Submit a review for a plugin.

    Args:
        slug: Plugin slug
        review: Review data

    Returns:
        Submission status
    """
    # In a real implementation, we'd get the user token from the session
    user_token = "dummy_token"

    success = await marketplace.submit_review(
        slug,
        review.rating,
        review.comment,
        user_token
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to submit review")

    return {"message": "Review submitted successfully"}


@router.get("/plugins/{slug}/validate", response_model=ValidationResponse)
async def validate_plugin(
    slug: str,
    current_user: User = Depends(get_current_active_user),
    marketplace: PluginMarketplace = Depends(get_marketplace)
) -> Dict[str, Any]:
    """
    Validate a plugin before installation.

    Args:
        slug: Plugin slug

    Returns:
        Validation results
    """
    validation = await marketplace.validate_plugin(slug)
    return validation
