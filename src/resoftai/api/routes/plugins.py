"""
Plugin Management API Routes

Provides endpoints for plugin marketplace, installation, and management.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from resoftai.db import get_db
from resoftai.auth.dependencies import get_current_active_user
from resoftai.models.user import User
from resoftai.models.plugin import PluginCategory, PluginStatus, InstallationStatus
from resoftai.crud import plugin as plugin_crud

router = APIRouter(prefix="/plugins", tags=["plugins"])


# =============================================================================
# Request/Response Models
# =============================================================================

class PluginCreate(BaseModel):
    """Request model for creating/publishing a plugin"""
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200, pattern="^[a-z0-9-]+$")
    category: PluginCategory
    version: str = Field(..., pattern="^[0-9]+\\.[0-9]+\\.[0-9]+$")
    description: Optional[str] = None
    long_description: Optional[str] = None
    tags: Optional[List[str]] = None
    package_url: Optional[str] = None
    source_url: Optional[str] = None
    documentation_url: Optional[str] = None
    license: str = "MIT"


class PluginUpdate(BaseModel):
    """Request model for updating a plugin"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    long_description: Optional[str] = None
    tags: Optional[List[str]] = None
    package_url: Optional[str] = None
    documentation_url: Optional[str] = None
    status: Optional[PluginStatus] = None


class PluginResponse(BaseModel):
    """Response model for plugin"""
    id: int
    name: str
    slug: str
    category: str
    version: str
    description: Optional[str]
    author_name: Optional[str]
    is_official: bool
    is_featured: bool
    status: str
    downloads_count: int
    installs_count: int
    rating_average: float
    rating_count: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class PluginInstallRequest(BaseModel):
    """Request model for installing a plugin"""
    config: Optional[dict] = Field(default_factory=dict)


class PluginInstallationResponse(BaseModel):
    """Response model for plugin installation"""
    id: int
    plugin_id: int
    installed_version: str
    status: str
    installed_at: str

    class Config:
        from_attributes = True


class PluginReviewCreate(BaseModel):
    """Request model for creating a review"""
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None


class PluginVersionRequest(BaseModel):
    """Request model for publishing a new plugin version"""
    version: str = Field(..., pattern="^[0-9]+\\.[0-9]+\\.[0-9]+$")
    changelog: Optional[str] = None
    package_url: str = Field(..., description="URL to download the plugin package")
    package_checksum: str = Field(..., description="SHA256 checksum of the package")
    min_platform_version: Optional[str] = None
    max_platform_version: Optional[str] = None
    is_stable: bool = True


class PluginVersionResponse(BaseModel):
    """Response model for plugin version"""
    id: int
    plugin_id: int
    version: str
    changelog: Optional[str]
    package_url: str
    package_checksum: str
    min_platform_version: Optional[str]
    max_platform_version: Optional[str]
    is_stable: bool
    is_deprecated: bool
    downloads_count: int
    created_at: str

    class Config:
        from_attributes = True


class PluginReviewResponse(BaseModel):
    """Response model for plugin review"""
    id: int
    plugin_id: int
    user_id: int
    rating: int
    title: Optional[str]
    content: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


# =============================================================================
# Plugin Marketplace Endpoints
# =============================================================================

@router.get("/marketplace", response_model=List[PluginResponse])
async def list_marketplace_plugins(
    category: Optional[PluginCategory] = Query(None),
    is_featured: Optional[bool] = Query(None),
    is_official: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("created_at", regex="^(created_at|downloads|rating|name)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Browse plugin marketplace

    Supports filtering by category, search, and sorting.
    Public endpoint - no authentication required.
    """
    plugins = await plugin_crud.list_plugins(
        db=db,
        category=category,
        status=PluginStatus.APPROVED,  # Only show approved plugins
        is_featured=is_featured,
        is_official=is_official,
        search=search,
        sort_by=sort_by,
        skip=skip,
        limit=limit
    )

    return plugins


@router.get("/marketplace/search", response_model=List[PluginResponse])
async def search_plugins(
    q: str = Query(..., min_length=2),
    category: Optional[PluginCategory] = Query(None),
    tags: Optional[List[str]] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Search plugins in marketplace

    Full-text search across name, description, and tags.
    """
    plugins = await plugin_crud.search_plugins(
        db=db,
        query_text=q,
        category=category,
        tags=tags,
        limit=limit
    )

    return plugins


@router.get("/marketplace/trending", response_model=List[PluginResponse])
async def get_trending_plugins(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Get trending plugins based on recent activity
    """
    plugins = await plugin_crud.get_trending_plugins(
        db=db,
        days=days,
        limit=limit
    )

    return plugins


@router.get("/marketplace/recommended", response_model=List[PluginResponse])
async def get_recommended_plugins(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized plugin recommendations

    Based on installed plugins and usage patterns.
    """
    plugins = await plugin_crud.get_recommended_plugins(
        db=db,
        user_id=current_user.id,
        limit=limit
    )

    return plugins


@router.get("/marketplace/{plugin_id}", response_model=PluginResponse)
async def get_marketplace_plugin(
    plugin_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a plugin
    """
    plugin = await plugin_crud.get_plugin_by_id(db, plugin_id)

    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin not found"
        )

    return plugin


# =============================================================================
# Plugin Publishing Endpoints
# =============================================================================

@router.post("", response_model=PluginResponse, status_code=status.HTTP_201_CREATED)
async def publish_plugin(
    plugin_data: PluginCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Publish a new plugin to the marketplace

    Plugin will be in 'submitted' status and requires approval.
    """
    # Check if slug already exists
    existing = await plugin_crud.get_plugin_by_slug(db, plugin_data.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plugin with slug '{plugin_data.slug}' already exists"
        )

    plugin = await plugin_crud.create_plugin(
        db=db,
        name=plugin_data.name,
        slug=plugin_data.slug,
        category=plugin_data.category,
        version=plugin_data.version,
        author_id=current_user.id,
        description=plugin_data.description,
        long_description=plugin_data.long_description,
        tags=plugin_data.tags,
        package_url=plugin_data.package_url,
        source_url=plugin_data.source_url,
        documentation_url=plugin_data.documentation_url,
        license=plugin_data.license,
        status=PluginStatus.SUBMITTED
    )

    return plugin


@router.put("/{plugin_id}", response_model=PluginResponse)
async def update_plugin(
    plugin_id: int,
    plugin_data: PluginUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update plugin information

    Only the plugin author can update their plugins.
    """
    plugin = await plugin_crud.get_plugin_by_id(db, plugin_id)

    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin not found"
        )

    # Check ownership
    if plugin.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this plugin"
        )

    updated_plugin = await plugin_crud.update_plugin(
        db=db,
        plugin_id=plugin_id,
        **plugin_data.dict(exclude_unset=True)
    )

    return updated_plugin


# =============================================================================
# Plugin Installation Endpoints
# =============================================================================

@router.post("/{plugin_id}/install", response_model=PluginInstallationResponse, status_code=status.HTTP_201_CREATED)
async def install_plugin(
    plugin_id: int,
    install_data: PluginInstallRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Install a plugin for the current user

    Creates an installation record and triggers the installation process.
    """
    plugin = await plugin_crud.get_plugin_by_id(db, plugin_id)

    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin not found"
        )

    if plugin.status != PluginStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plugin is not approved for installation"
        )

    # Check if already installed
    existing = await plugin_crud.get_installation(
        db=db,
        plugin_id=plugin_id,
        user_id=current_user.id
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plugin is already installed"
        )

    installation = await plugin_crud.install_plugin(
        db=db,
        plugin_id=plugin_id,
        installed_version=plugin.version,
        user_id=current_user.id,
        config=install_data.config
    )

    # TODO: Trigger async installation process

    return installation


@router.get("/installations", response_model=List[PluginInstallationResponse])
async def list_installations(
    status_filter: Optional[InstallationStatus] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List installed plugins for the current user
    """
    installations = await plugin_crud.list_installations(
        db=db,
        user_id=current_user.id,
        status=status_filter
    )

    return installations


@router.delete("/{plugin_id}/uninstall", status_code=status.HTTP_204_NO_CONTENT)
async def uninstall_plugin(
    plugin_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Uninstall a plugin
    """
    success = await plugin_crud.uninstall_plugin(
        db=db,
        plugin_id=plugin_id,
        user_id=current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin is not installed"
        )


# =============================================================================
# Plugin Review Endpoints
# =============================================================================

@router.post("/{plugin_id}/reviews", response_model=PluginReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    plugin_id: int,
    review_data: PluginReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a review for a plugin

    Users can only review plugins they have installed.
    """
    plugin = await plugin_crud.get_plugin_by_id(db, plugin_id)

    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin not found"
        )

    # Check if user has installed the plugin
    installation = await plugin_crud.get_installation(
        db=db,
        plugin_id=plugin_id,
        user_id=current_user.id
    )

    if not installation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must install the plugin before reviewing it"
        )

    try:
        review = await plugin_crud.create_review(
            db=db,
            plugin_id=plugin_id,
            user_id=current_user.id,
            rating=review_data.rating,
            title=review_data.title,
            content=review_data.content
        )
    except Exception as e:
        # Handle duplicate review (unique constraint)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this plugin"
        )

    return review


@router.get("/{plugin_id}/reviews", response_model=List[PluginReviewResponse])
async def list_reviews(
    plugin_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    List reviews for a plugin
    """
    reviews = await plugin_crud.list_reviews(
        db=db,
        plugin_id=plugin_id,
        skip=skip,
        limit=limit
    )

    return reviews


# =============================================================================
# Plugin Version Management Endpoints
# =============================================================================

@router.post("/{plugin_id}/versions", response_model=PluginVersionResponse, status_code=status.HTTP_201_CREATED)
async def publish_plugin_version(
    plugin_id: int,
    version_data: PluginVersionRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Publish a new version of a plugin

    Only the plugin author can publish new versions.
    """
    plugin = await plugin_crud.get_plugin_by_id(db, plugin_id)

    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin not found"
        )

    # Check ownership
    if plugin.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to publish versions for this plugin"
        )

    # Check if version already exists
    existing_versions = await plugin_crud.get_plugin_versions(db, plugin_id)
    for v in existing_versions:
        if v.version == version_data.version:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Version {version_data.version} already exists"
            )

    # Create new version
    version = await plugin_crud.create_plugin_version(
        db=db,
        plugin_id=plugin_id,
        version=version_data.version,
        package_url=version_data.package_url,
        package_checksum=version_data.package_checksum,
        changelog=version_data.changelog,
        min_platform_version=version_data.min_platform_version,
        max_platform_version=version_data.max_platform_version,
        is_stable=version_data.is_stable
    )

    # Update plugin's current version if this is the latest stable version
    if version_data.is_stable:
        await plugin_crud.update_plugin(
            db=db,
            plugin_id=plugin_id,
            version=version_data.version,
            package_url=version_data.package_url,
            package_checksum=version_data.package_checksum
        )

    return version


@router.get("/{plugin_id}/versions", response_model=List[PluginVersionResponse])
async def list_plugin_versions(
    plugin_id: int,
    stable_only: bool = Query(False, description="Only return stable versions"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all versions for a plugin
    """
    plugin = await plugin_crud.get_plugin_by_id(db, plugin_id)

    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin not found"
        )

    versions = await plugin_crud.get_plugin_versions(db, plugin_id)

    if stable_only:
        versions = [v for v in versions if v.is_stable and not v.is_deprecated]

    return versions


@router.get("/{plugin_id}/versions/{version}", response_model=PluginVersionResponse)
async def get_plugin_version(
    plugin_id: int,
    version: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific version details
    """
    from sqlalchemy import select, and_
    from resoftai.models.plugin import PluginVersion

    result = await db.execute(
        select(PluginVersion).where(
            and_(
                PluginVersion.plugin_id == plugin_id,
                PluginVersion.version == version
            )
        )
    )
    plugin_version = result.scalar_one_or_none()

    if not plugin_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version} not found for this plugin"
        )

    return plugin_version


@router.post("/{plugin_id}/versions/{version}/deprecate", status_code=status.HTTP_200_OK)
async def deprecate_plugin_version(
    plugin_id: int,
    version: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deprecate a specific plugin version

    Only the plugin author or admin can deprecate versions.
    """
    plugin = await plugin_crud.get_plugin_by_id(db, plugin_id)

    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin not found"
        )

    # Check ownership
    if plugin.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to deprecate this version"
        )

    # Get the version
    from sqlalchemy import select, and_, update
    from resoftai.models.plugin import PluginVersion

    result = await db.execute(
        select(PluginVersion).where(
            and_(
                PluginVersion.plugin_id == plugin_id,
                PluginVersion.version == version
            )
        )
    )
    plugin_version = result.scalar_one_or_none()

    if not plugin_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version} not found"
        )

    # Mark as deprecated
    await db.execute(
        update(PluginVersion)
        .where(PluginVersion.id == plugin_version.id)
        .values(is_deprecated=True)
    )
    await db.commit()

    return {
        "message": f"Version {version} has been deprecated",
        "plugin_id": plugin_id,
        "version": version
    }


@router.post("/{plugin_id}/versions/{version}/download", status_code=status.HTTP_200_OK)
async def track_plugin_version_download(
    plugin_id: int,
    version: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Track download of a specific plugin version

    Call this endpoint before downloading to increment download counter.
    """
    from sqlalchemy import select, and_, update
    from resoftai.models.plugin import PluginVersion

    result = await db.execute(
        select(PluginVersion).where(
            and_(
                PluginVersion.plugin_id == plugin_id,
                PluginVersion.version == version
            )
        )
    )
    plugin_version = result.scalar_one_or_none()

    if not plugin_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version} not found"
        )

    # Increment download counter
    await db.execute(
        update(PluginVersion)
        .where(PluginVersion.id == plugin_version.id)
        .values(downloads_count=PluginVersion.downloads_count + 1)
    )
    await db.commit()

    # Also increment plugin download counter
    await plugin_crud.increment_plugin_downloads(db, plugin_id)

    return {
        "message": "Download tracked",
        "plugin_id": plugin_id,
        "version": version,
        "download_url": plugin_version.package_url
    }
