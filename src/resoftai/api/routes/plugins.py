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
# Plugin Update Endpoints
# =============================================================================

@router.get("/updates/check", response_model=Dict[str, Any])
async def check_updates(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    检查已安装插件的可用更新

    Returns available updates for all installed plugins.
    """
    from resoftai.crud.plugin_updates import check_plugin_updates

    updates = await check_plugin_updates(
        db=db,
        user_id=current_user.id
    )

    return {
        "total_updates": len(updates),
        "updates": updates
    }


@router.get("/updates/statistics", response_model=Dict[str, Any])
async def get_update_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取更新统计信息
    """
    from resoftai.crud.plugin_updates import get_update_statistics

    stats = await get_update_statistics(
        db=db,
        user_id=current_user.id
    )

    return stats


@router.post("/{plugin_id}/update", status_code=status.HTTP_200_OK)
async def update_plugin_to_latest(
    plugin_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新插件到最新版本
    """
    from resoftai.crud import plugin as plugin_crud
    from resoftai.crud.plugin_updates import update_plugin

    # 获取安装记录
    installation = await plugin_crud.get_installation(
        db=db,
        plugin_id=plugin_id,
        user_id=current_user.id
    )

    if not installation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin is not installed"
        )

    success = await update_plugin(db, installation.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update plugin"
        )

    return {"message": "Plugin updated successfully"}


@router.post("/installations/{installation_id}/auto-update", status_code=status.HTTP_200_OK)
async def toggle_auto_update(
    installation_id: int,
    auto_update: bool = Query(True, description="Enable or disable auto-update"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    启用/禁用插件自动更新
    """
    from resoftai.crud.plugin_updates import enable_auto_update

    success = await enable_auto_update(db, installation_id, auto_update)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Installation not found"
        )

    return {"message": f"Auto-update {'enabled' if auto_update else 'disabled'}"}


# =============================================================================
# Plugin Review Endpoints (Admin)
# =============================================================================

@router.get("/admin/pending-reviews", response_model=List[PluginResponse])
async def list_pending_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取待审核插件列表 (管理员)

    Requires admin privileges.
    """
    # 检查管理员权限
    if not hasattr(current_user, 'role') or current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    from resoftai.crud.plugin_review import get_pending_reviews

    plugins = await get_pending_reviews(db=db, skip=skip, limit=limit)

    return plugins


@router.post("/{plugin_id}/submit-review", status_code=status.HTTP_200_OK)
async def submit_plugin_for_review(
    plugin_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    提交插件供审核

    Plugin author can submit their plugin for review.
    """
    plugin = await plugin_crud.get_plugin_by_id(db, plugin_id)

    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin not found"
        )

    # 检查所有权
    if plugin.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to submit this plugin"
        )

    from resoftai.crud.plugin_review import submit_for_review

    success = await submit_for_review(db, plugin_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot submit plugin for review"
        )

    return {"message": "Plugin submitted for review"}


@router.post("/admin/{plugin_id}/review", status_code=status.HTTP_200_OK)
async def review_plugin(
    plugin_id: int,
    decision: str = Query(..., regex="^(approved|rejected|needs_changes)$"),
    comments: Optional[str] = None,
    required_changes: Optional[List[str]] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    审核插件 (管理员)

    Requires admin privileges.
    """
    # 检查管理员权限
    if not hasattr(current_user, 'role') or current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    from resoftai.crud import plugin_review

    result = await plugin_review.review_plugin(
        db=db,
        plugin_id=plugin_id,
        decision=decision,
        reviewer_id=current_user.id,
        comments=comments,
        required_changes=required_changes
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Review failed")
        )

    return result


@router.get("/{plugin_id}/automated-checks", response_model=Dict[str, Any])
async def run_automated_checks(
    plugin_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    运行自动化检查

    Can be run by plugin author or admin.
    """
    plugin = await plugin_crud.get_plugin_by_id(db, plugin_id)

    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin not found"
        )

    # 检查权限
    if plugin.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to run checks on this plugin"
        )

    from resoftai.crud.plugin_review import run_automated_checks

    result = await run_automated_checks(db, plugin_id)

    return result


@router.get("/admin/review-statistics", response_model=Dict[str, Any])
async def get_review_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取审核统计 (管理员)

    Requires admin privileges.
    """
    # 检查管理员权限
    if not hasattr(current_user, 'role') or current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    from resoftai.crud.plugin_review import get_review_statistics

    stats = await get_review_statistics(db=db, days=days)

    return stats
