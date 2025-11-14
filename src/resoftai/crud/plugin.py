"""
CRUD operations for Plugin System

Provides database operations for:
- Plugins and versions
- Plugin installations
- Plugin reviews and ratings
- Plugin collections and community features
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from resoftai.models.plugin import (
    Plugin, PluginVersion, PluginInstallation, PluginReview,
    PluginComment, PluginCollection, PluginCollectionItem,
    PluginStatus, PluginCategory, InstallationStatus
)


# =============================================================================
# Plugin Operations
# =============================================================================

async def create_plugin(
    db: AsyncSession,
    name: str,
    slug: str,
    category: PluginCategory,
    version: str,
    author_id: Optional[int] = None,
    description: Optional[str] = None,
    **kwargs
) -> Plugin:
    """Create a new plugin"""
    plugin = Plugin(
        name=name,
        slug=slug,
        category=category,
        version=version,
        author_id=author_id,
        description=description,
        **kwargs
    )
    db.add(plugin)
    await db.commit()
    await db.refresh(plugin)
    return plugin


async def get_plugin_by_id(db: AsyncSession, plugin_id: int) -> Optional[Plugin]:
    """Get plugin by ID"""
    result = await db.execute(
        select(Plugin)
        .where(Plugin.id == plugin_id)
        .options(selectinload(Plugin.versions))
    )
    return result.scalar_one_or_none()


async def get_plugin_by_slug(db: AsyncSession, slug: str) -> Optional[Plugin]:
    """Get plugin by slug"""
    result = await db.execute(
        select(Plugin)
        .where(Plugin.slug == slug)
        .options(selectinload(Plugin.versions))
    )
    return result.scalar_one_or_none()


async def list_plugins(
    db: AsyncSession,
    category: Optional[PluginCategory] = None,
    status: Optional[PluginStatus] = None,
    is_featured: Optional[bool] = None,
    is_official: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    skip: int = 0,
    limit: int = 20
) -> List[Plugin]:
    """List plugins with filters"""
    query = select(Plugin)

    # Filters
    if category:
        query = query.where(Plugin.category == category)
    if status:
        query = query.where(Plugin.status == status)
    if is_featured is not None:
        query = query.where(Plugin.is_featured == is_featured)
    if is_official is not None:
        query = query.where(Plugin.is_official == is_official)
    if search:
        query = query.where(
            or_(
                Plugin.name.ilike(f"%{search}%"),
                Plugin.description.ilike(f"%{search}%")
            )
        )

    # Sorting
    if sort_by == "downloads":
        query = query.order_by(desc(Plugin.downloads_count))
    elif sort_by == "rating":
        query = query.order_by(desc(Plugin.rating_average))
    elif sort_by == "name":
        query = query.order_by(Plugin.name)
    else:  # created_at
        query = query.order_by(desc(Plugin.created_at))

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def update_plugin(
    db: AsyncSession,
    plugin_id: int,
    **kwargs
) -> Optional[Plugin]:
    """Update plugin"""
    plugin = await get_plugin_by_id(db, plugin_id)
    if not plugin:
        return None

    for key, value in kwargs.items():
        if hasattr(plugin, key):
            setattr(plugin, key, value)

    plugin.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(plugin)
    return plugin


async def increment_plugin_downloads(db: AsyncSession, plugin_id: int):
    """Increment plugin download counter"""
    plugin = await get_plugin_by_id(db, plugin_id)
    if plugin:
        plugin.downloads_count += 1
        await db.commit()


async def increment_plugin_installs(db: AsyncSession, plugin_id: int):
    """Increment plugin install counter"""
    plugin = await get_plugin_by_id(db, plugin_id)
    if plugin:
        plugin.installs_count += 1
        await db.commit()


# =============================================================================
# Plugin Version Operations
# =============================================================================

async def create_plugin_version(
    db: AsyncSession,
    plugin_id: int,
    version: str,
    package_url: str,
    package_checksum: str,
    changelog: Optional[str] = None,
    **kwargs
) -> PluginVersion:
    """Create a new plugin version"""
    plugin_version = PluginVersion(
        plugin_id=plugin_id,
        version=version,
        package_url=package_url,
        package_checksum=package_checksum,
        changelog=changelog,
        **kwargs
    )
    db.add(plugin_version)
    await db.commit()
    await db.refresh(plugin_version)
    return plugin_version


async def get_plugin_versions(
    db: AsyncSession,
    plugin_id: int
) -> List[PluginVersion]:
    """Get all versions for a plugin"""
    result = await db.execute(
        select(PluginVersion)
        .where(PluginVersion.plugin_id == plugin_id)
        .order_by(desc(PluginVersion.created_at))
    )
    return list(result.scalars().all())


# =============================================================================
# Plugin Installation Operations
# =============================================================================

async def install_plugin(
    db: AsyncSession,
    plugin_id: int,
    installed_version: str,
    organization_id: Optional[int] = None,
    user_id: Optional[int] = None,
    config: Optional[Dict[str, Any]] = None
) -> PluginInstallation:
    """Install a plugin"""
    installation = PluginInstallation(
        plugin_id=plugin_id,
        organization_id=organization_id,
        user_id=user_id,
        installed_version=installed_version,
        config=config or {},
        status=InstallationStatus.INSTALLING
    )
    db.add(installation)
    await db.commit()
    await db.refresh(installation)

    # Increment install counter
    await increment_plugin_installs(db, plugin_id)

    return installation


async def get_installation(
    db: AsyncSession,
    plugin_id: int,
    organization_id: Optional[int] = None,
    user_id: Optional[int] = None
) -> Optional[PluginInstallation]:
    """Get plugin installation"""
    query = select(PluginInstallation).where(
        PluginInstallation.plugin_id == plugin_id
    )

    if organization_id:
        query = query.where(PluginInstallation.organization_id == organization_id)
    if user_id:
        query = query.where(PluginInstallation.user_id == user_id)

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def list_installations(
    db: AsyncSession,
    organization_id: Optional[int] = None,
    user_id: Optional[int] = None,
    status: Optional[InstallationStatus] = None
) -> List[PluginInstallation]:
    """List plugin installations"""
    query = select(PluginInstallation).options(selectinload(PluginInstallation.plugin))

    if organization_id:
        query = query.where(PluginInstallation.organization_id == organization_id)
    if user_id:
        query = query.where(PluginInstallation.user_id == user_id)
    if status:
        query = query.where(PluginInstallation.status == status)

    query = query.order_by(desc(PluginInstallation.installed_at))

    result = await db.execute(query)
    return list(result.scalars().all())


async def update_installation_status(
    db: AsyncSession,
    installation_id: int,
    status: InstallationStatus,
    error_message: Optional[str] = None
) -> Optional[PluginInstallation]:
    """Update installation status"""
    result = await db.execute(
        select(PluginInstallation).where(PluginInstallation.id == installation_id)
    )
    installation = result.scalar_one_or_none()

    if not installation:
        return None

    installation.status = status
    if error_message:
        installation.error_message = error_message
    installation.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(installation)
    return installation


async def uninstall_plugin(
    db: AsyncSession,
    plugin_id: int,
    organization_id: Optional[int] = None,
    user_id: Optional[int] = None
) -> bool:
    """Uninstall a plugin"""
    installation = await get_installation(db, plugin_id, organization_id, user_id)

    if not installation:
        return False

    await db.delete(installation)
    await db.commit()
    return True


# =============================================================================
# Plugin Review Operations
# =============================================================================

async def create_review(
    db: AsyncSession,
    plugin_id: int,
    user_id: int,
    rating: int,
    title: Optional[str] = None,
    content: Optional[str] = None
) -> PluginReview:
    """Create a plugin review"""
    review = PluginReview(
        plugin_id=plugin_id,
        user_id=user_id,
        rating=rating,
        title=title,
        content=content
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)

    # Update plugin rating
    await update_plugin_rating(db, plugin_id)

    return review


async def update_plugin_rating(db: AsyncSession, plugin_id: int):
    """Recalculate and update plugin average rating"""
    result = await db.execute(
        select(
            func.avg(PluginReview.rating),
            func.count(PluginReview.id)
        ).where(PluginReview.plugin_id == plugin_id)
    )
    avg_rating, count = result.one()

    plugin = await get_plugin_by_id(db, plugin_id)
    if plugin:
        plugin.rating_average = float(avg_rating) if avg_rating else 0.0
        plugin.rating_count = count
        await db.commit()


async def list_reviews(
    db: AsyncSession,
    plugin_id: int,
    skip: int = 0,
    limit: int = 20
) -> List[PluginReview]:
    """List reviews for a plugin"""
    result = await db.execute(
        select(PluginReview)
        .where(PluginReview.plugin_id == plugin_id)
        .order_by(desc(PluginReview.created_at))
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


# =============================================================================
# Plugin Comment Operations
# =============================================================================

async def create_comment(
    db: AsyncSession,
    plugin_id: int,
    user_id: int,
    content: str,
    parent_id: Optional[int] = None
) -> PluginComment:
    """Create a comment on a plugin"""
    comment = PluginComment(
        plugin_id=plugin_id,
        user_id=user_id,
        content=content,
        parent_id=parent_id
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def list_comments(
    db: AsyncSession,
    plugin_id: int,
    parent_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50
) -> List[PluginComment]:
    """List comments for a plugin"""
    query = select(PluginComment).where(PluginComment.plugin_id == plugin_id)

    if parent_id is None:
        # Top-level comments only
        query = query.where(PluginComment.parent_id.is_(None))
    else:
        # Replies to a specific comment
        query = query.where(PluginComment.parent_id == parent_id)

    query = query.where(PluginComment.is_deleted == False)
    query = query.order_by(desc(PluginComment.created_at)).offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


# =============================================================================
# Plugin Collection Operations
# =============================================================================

async def create_collection(
    db: AsyncSession,
    user_id: int,
    name: str,
    slug: str,
    description: Optional[str] = None,
    is_public: bool = True
) -> PluginCollection:
    """Create a plugin collection"""
    collection = PluginCollection(
        user_id=user_id,
        name=name,
        slug=slug,
        description=description,
        is_public=is_public
    )
    db.add(collection)
    await db.commit()
    await db.refresh(collection)
    return collection


async def add_plugin_to_collection(
    db: AsyncSession,
    collection_id: int,
    plugin_id: int,
    note: Optional[str] = None,
    position: int = 0
) -> PluginCollectionItem:
    """Add plugin to collection"""
    item = PluginCollectionItem(
        collection_id=collection_id,
        plugin_id=plugin_id,
        note=note,
        position=position
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def get_collection_by_slug(
    db: AsyncSession,
    slug: str
) -> Optional[PluginCollection]:
    """Get collection by slug"""
    result = await db.execute(
        select(PluginCollection)
        .where(PluginCollection.slug == slug)
        .options(selectinload(PluginCollection.items))
    )
    return result.scalar_one_or_none()


async def list_collections(
    db: AsyncSession,
    user_id: Optional[int] = None,
    is_public: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    skip: int = 0,
    limit: int = 20
) -> List[PluginCollection]:
    """List plugin collections"""
    query = select(PluginCollection)

    if user_id:
        query = query.where(PluginCollection.user_id == user_id)
    if is_public is not None:
        query = query.where(PluginCollection.is_public == is_public)
    if is_featured is not None:
        query = query.where(PluginCollection.is_featured == is_featured)

    query = query.order_by(desc(PluginCollection.created_at)).offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


# =============================================================================
# Search and Discovery
# =============================================================================

async def search_plugins(
    db: AsyncSession,
    query_text: str,
    category: Optional[PluginCategory] = None,
    tags: Optional[List[str]] = None,
    limit: int = 20
) -> List[Plugin]:
    """
    Search plugins by text query

    Searches in name, description, and tags.
    """
    query = select(Plugin).where(Plugin.status == PluginStatus.APPROVED)

    # Text search
    query = query.where(
        or_(
            Plugin.name.ilike(f"%{query_text}%"),
            Plugin.description.ilike(f"%{query_text}%"),
            Plugin.long_description.ilike(f"%{query_text}%")
        )
    )

    # Category filter
    if category:
        query = query.where(Plugin.category == category)

    # Tag filter (PostgreSQL JSON operator)
    if tags:
        for tag in tags:
            query = query.where(Plugin.tags.contains([tag]))

    # Order by relevance (downloads + rating)
    query = query.order_by(
        desc(Plugin.downloads_count + Plugin.rating_average * 1000)
    ).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_trending_plugins(
    db: AsyncSession,
    days: int = 7,
    limit: int = 10
) -> List[Plugin]:
    """
    Get trending plugins based on recent downloads

    This is a simplified version. In production, you'd track downloads
    over time and calculate trends.
    """
    result = await db.execute(
        select(Plugin)
        .where(Plugin.status == PluginStatus.APPROVED)
        .order_by(desc(Plugin.downloads_count))
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_recommended_plugins(
    db: AsyncSession,
    user_id: int,
    limit: int = 10
) -> List[Plugin]:
    """
    Get recommended plugins for a user

    This is a placeholder for a recommendation system.
    In production, you'd use ML or collaborative filtering.
    """
    # For now, return popular plugins the user hasn't installed
    installed_result = await db.execute(
        select(PluginInstallation.plugin_id)
        .where(PluginInstallation.user_id == user_id)
    )
    installed_ids = [row for row in installed_result.scalars().all()]

    query = select(Plugin).where(
        and_(
            Plugin.status == PluginStatus.APPROVED,
            Plugin.id.not_in(installed_ids) if installed_ids else True
        )
    ).order_by(desc(Plugin.rating_average)).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())
