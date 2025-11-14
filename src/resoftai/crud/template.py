"""
CRUD operations for Template Marketplace

Provides database operations for:
- Templates and versions
- Template installations/usage tracking
- Template reviews and ratings
- Template collections and community features
- Contributor profiles and badges
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from resoftai.models.template import (
    TemplateModel, TemplateVersion, TemplateInstallation, TemplateReview,
    TemplateComment, TemplateCollection, TemplateCollectionItem,
    ContributorProfile, ContributorBadge,
    TemplateStatus, TemplateCategory
)


# =============================================================================
# Template Operations
# =============================================================================

async def create_template(
    db: AsyncSession,
    name: str,
    slug: str,
    category: TemplateCategory,
    version: str,
    template_data: Dict[str, Any],
    author_id: Optional[int] = None,
    description: Optional[str] = None,
    **kwargs
) -> TemplateModel:
    """Create a new template"""
    template = TemplateModel(
        name=name,
        slug=slug,
        category=category,
        version=version,
        template_data=template_data,
        author_id=author_id,
        description=description,
        **kwargs
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


async def get_template_by_id(db: AsyncSession, template_id: int) -> Optional[TemplateModel]:
    """Get template by ID"""
    result = await db.execute(
        select(TemplateModel)
        .where(TemplateModel.id == template_id)
        .options(selectinload(TemplateModel.versions))
    )
    return result.scalar_one_or_none()


async def get_template_by_slug(db: AsyncSession, slug: str) -> Optional[TemplateModel]:
    """Get template by slug"""
    result = await db.execute(
        select(TemplateModel)
        .where(TemplateModel.slug == slug)
        .options(selectinload(TemplateModel.versions))
    )
    return result.scalar_one_or_none()


async def list_templates(
    db: AsyncSession,
    category: Optional[TemplateCategory] = None,
    status: Optional[TemplateStatus] = None,
    is_featured: Optional[bool] = None,
    is_official: Optional[bool] = None,
    search: Optional[str] = None,
    tags: Optional[List[str]] = None,
    sort_by: str = "created_at",
    skip: int = 0,
    limit: int = 20
) -> List[TemplateModel]:
    """List templates with filters"""
    query = select(TemplateModel)

    # Filters
    if category:
        query = query.where(TemplateModel.category == category)
    if status:
        query = query.where(TemplateModel.status == status)
    if is_featured is not None:
        query = query.where(TemplateModel.is_featured == is_featured)
    if is_official is not None:
        query = query.where(TemplateModel.is_official == is_official)
    if search:
        query = query.where(
            or_(
                TemplateModel.name.ilike(f"%{search}%"),
                TemplateModel.description.ilike(f"%{search}%")
            )
        )
    if tags:
        # Filter by tags (JSON array contains any of the specified tags)
        for tag in tags:
            query = query.where(TemplateModel.tags.contains([tag]))

    # Sorting
    if sort_by == "downloads":
        query = query.order_by(desc(TemplateModel.downloads_count))
    elif sort_by == "rating":
        query = query.order_by(desc(TemplateModel.rating_average))
    elif sort_by == "installs":
        query = query.order_by(desc(TemplateModel.installs_count))
    elif sort_by == "name":
        query = query.order_by(TemplateModel.name)
    else:  # created_at
        query = query.order_by(desc(TemplateModel.created_at))

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def update_template(
    db: AsyncSession,
    template_id: int,
    **kwargs
) -> Optional[TemplateModel]:
    """Update template"""
    template = await get_template_by_id(db, template_id)
    if not template:
        return None

    for key, value in kwargs.items():
        if hasattr(template, key):
            setattr(template, key, value)

    template.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(template)
    return template


async def delete_template(db: AsyncSession, template_id: int) -> bool:
    """Delete template (soft delete by setting status to deprecated)"""
    template = await get_template_by_id(db, template_id)
    if not template:
        return False

    template.status = TemplateStatus.DEPRECATED
    await db.commit()
    return True


async def increment_template_downloads(db: AsyncSession, template_id: int):
    """Increment template download counter"""
    template = await get_template_by_id(db, template_id)
    if template:
        template.downloads_count += 1
        await db.commit()


async def increment_template_installs(db: AsyncSession, template_id: int):
    """Increment template install counter"""
    template = await get_template_by_id(db, template_id)
    if template:
        template.installs_count += 1
        await db.commit()


async def search_templates(
    db: AsyncSession,
    query_text: str,
    category: Optional[TemplateCategory] = None,
    tags: Optional[List[str]] = None,
    limit: int = 20
) -> List[TemplateModel]:
    """Full-text search for templates"""
    query = select(TemplateModel).where(TemplateModel.status == TemplateStatus.APPROVED)

    # Search in name, description, and tags
    search_filter = or_(
        TemplateModel.name.ilike(f"%{query_text}%"),
        TemplateModel.description.ilike(f"%{query_text}%"),
        TemplateModel.long_description.ilike(f"%{query_text}%")
    )
    query = query.where(search_filter)

    if category:
        query = query.where(TemplateModel.category == category)

    if tags:
        for tag in tags:
            query = query.where(TemplateModel.tags.contains([tag]))

    query = query.order_by(desc(TemplateModel.rating_average)).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_trending_templates(
    db: AsyncSession,
    days: int = 7,
    limit: int = 10
) -> List[TemplateModel]:
    """Get trending templates based on recent activity"""
    since_date = datetime.utcnow() - timedelta(days=days)

    # Subquery for recent installs
    recent_installs = (
        select(
            TemplateInstallation.template_id,
            func.count(TemplateInstallation.id).label('recent_installs')
        )
        .where(TemplateInstallation.installed_at >= since_date)
        .group_by(TemplateInstallation.template_id)
        .subquery()
    )

    # Join templates with recent install counts
    query = (
        select(TemplateModel)
        .outerjoin(recent_installs, TemplateModel.id == recent_installs.c.template_id)
        .where(TemplateModel.status == TemplateStatus.APPROVED)
        .order_by(desc(func.coalesce(recent_installs.c.recent_installs, 0)))
        .limit(limit)
    )

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_recommended_templates(
    db: AsyncSession,
    user_id: int,
    limit: int = 10
) -> List[TemplateModel]:
    """Get personalized template recommendations for a user"""
    # Get user's template usage history
    user_templates = await db.execute(
        select(TemplateInstallation.template_id)
        .where(TemplateInstallation.user_id == user_id)
    )
    used_template_ids = [t for t in user_templates.scalars().all()]

    # Get templates in same categories as user's installed templates
    if used_template_ids:
        user_categories = await db.execute(
            select(TemplateModel.category)
            .where(TemplateModel.id.in_(used_template_ids))
            .distinct()
        )
        categories = [c for c in user_categories.scalars().all()]

        # Recommend highly-rated templates in same categories that user hasn't used
        query = (
            select(TemplateModel)
            .where(
                and_(
                    TemplateModel.status == TemplateStatus.APPROVED,
                    TemplateModel.category.in_(categories),
                    ~TemplateModel.id.in_(used_template_ids)
                )
            )
            .order_by(desc(TemplateModel.rating_average))
            .limit(limit)
        )
    else:
        # For new users, recommend popular templates
        query = (
            select(TemplateModel)
            .where(TemplateModel.status == TemplateStatus.APPROVED)
            .order_by(desc(TemplateModel.installs_count))
            .limit(limit)
        )

    result = await db.execute(query)
    return list(result.scalars().all())


# =============================================================================
# Template Version Operations
# =============================================================================

async def create_template_version(
    db: AsyncSession,
    template_id: int,
    version: str,
    template_data: Dict[str, Any],
    changelog: Optional[str] = None,
    **kwargs
) -> TemplateVersion:
    """Create a new template version"""
    template_version = TemplateVersion(
        template_id=template_id,
        version=version,
        template_data=template_data,
        changelog=changelog,
        **kwargs
    )
    db.add(template_version)
    await db.commit()
    await db.refresh(template_version)
    return template_version


async def get_template_versions(
    db: AsyncSession,
    template_id: int
) -> List[TemplateVersion]:
    """Get all versions for a template"""
    result = await db.execute(
        select(TemplateVersion)
        .where(TemplateVersion.template_id == template_id)
        .order_by(desc(TemplateVersion.created_at))
    )
    return list(result.scalars().all())


async def get_template_version(
    db: AsyncSession,
    template_id: int,
    version: str
) -> Optional[TemplateVersion]:
    """Get specific version of a template"""
    result = await db.execute(
        select(TemplateVersion)
        .where(
            and_(
                TemplateVersion.template_id == template_id,
                TemplateVersion.version == version
            )
        )
    )
    return result.scalar_one_or_none()


# =============================================================================
# Template Installation Operations
# =============================================================================

async def track_template_usage(
    db: AsyncSession,
    template_id: int,
    user_id: int,
    installed_version: str,
    project_id: Optional[int] = None,
    variables_used: Optional[Dict[str, Any]] = None,
    **kwargs
) -> TemplateInstallation:
    """Track template usage/installation"""
    installation = TemplateInstallation(
        template_id=template_id,
        user_id=user_id,
        installed_version=installed_version,
        project_id=project_id,
        variables_used=variables_used,
        **kwargs
    )
    db.add(installation)

    # Increment template install count
    await increment_template_installs(db, template_id)

    await db.commit()
    await db.refresh(installation)
    return installation


async def list_template_installations(
    db: AsyncSession,
    user_id: int,
    template_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 20
) -> List[TemplateInstallation]:
    """List template installations for a user"""
    query = select(TemplateInstallation).where(TemplateInstallation.user_id == user_id)

    if template_id:
        query = query.where(TemplateInstallation.template_id == template_id)

    query = query.order_by(desc(TemplateInstallation.installed_at)).offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


# =============================================================================
# Template Review Operations
# =============================================================================

async def create_template_review(
    db: AsyncSession,
    template_id: int,
    user_id: int,
    rating: int,
    title: Optional[str] = None,
    content: Optional[str] = None
) -> TemplateReview:
    """Create a review for a template"""
    review = TemplateReview(
        template_id=template_id,
        user_id=user_id,
        rating=rating,
        title=title,
        content=content
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)

    # Update template rating statistics
    await update_template_rating_stats(db, template_id)

    return review


async def update_template_rating_stats(db: AsyncSession, template_id: int):
    """Recalculate template rating statistics"""
    result = await db.execute(
        select(
            func.avg(TemplateReview.rating).label('avg_rating'),
            func.count(TemplateReview.id).label('count')
        )
        .where(TemplateReview.template_id == template_id)
    )
    row = result.one()

    template = await get_template_by_id(db, template_id)
    if template:
        template.rating_average = float(row.avg_rating or 0.0)
        template.rating_count = row.count
        await db.commit()


async def list_template_reviews(
    db: AsyncSession,
    template_id: int,
    skip: int = 0,
    limit: int = 20
) -> List[TemplateReview]:
    """List reviews for a template"""
    result = await db.execute(
        select(TemplateReview)
        .where(TemplateReview.template_id == template_id)
        .order_by(desc(TemplateReview.created_at))
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_user_template_review(
    db: AsyncSession,
    template_id: int,
    user_id: int
) -> Optional[TemplateReview]:
    """Get user's review for a template"""
    result = await db.execute(
        select(TemplateReview)
        .where(
            and_(
                TemplateReview.template_id == template_id,
                TemplateReview.user_id == user_id
            )
        )
    )
    return result.scalar_one_or_none()


# =============================================================================
# Contributor Profile Operations
# =============================================================================

async def create_contributor_profile(
    db: AsyncSession,
    user_id: int,
    display_name: str,
    **kwargs
) -> ContributorProfile:
    """Create contributor profile"""
    profile = ContributorProfile(
        user_id=user_id,
        display_name=display_name,
        **kwargs
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


async def get_contributor_profile(
    db: AsyncSession,
    user_id: int
) -> Optional[ContributorProfile]:
    """Get contributor profile by user ID"""
    result = await db.execute(
        select(ContributorProfile)
        .where(ContributorProfile.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def update_contributor_profile(
    db: AsyncSession,
    user_id: int,
    **kwargs
) -> Optional[ContributorProfile]:
    """Update contributor profile"""
    profile = await get_contributor_profile(db, user_id)
    if not profile:
        return None

    for key, value in kwargs.items():
        if hasattr(profile, key):
            setattr(profile, key, value)

    profile.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(profile)
    return profile


async def update_contributor_stats(
    db: AsyncSession,
    user_id: int
):
    """Recalculate contributor statistics"""
    from resoftai.models.plugin import Plugin

    profile = await get_contributor_profile(db, user_id)
    if not profile:
        return

    # Count plugins
    plugin_count = await db.execute(
        select(func.count(Plugin.id))
        .where(Plugin.author_id == user_id)
    )
    profile.plugins_count = plugin_count.scalar_one()

    # Count templates
    template_count = await db.execute(
        select(func.count(TemplateModel.id))
        .where(TemplateModel.author_id == user_id)
    )
    profile.templates_count = template_count.scalar_one()

    # Calculate total downloads
    plugin_downloads = await db.execute(
        select(func.sum(Plugin.downloads_count))
        .where(Plugin.author_id == user_id)
    )
    template_downloads = await db.execute(
        select(func.sum(TemplateModel.downloads_count))
        .where(TemplateModel.author_id == user_id)
    )
    profile.total_downloads = (plugin_downloads.scalar_one() or 0) + (template_downloads.scalar_one() or 0)

    # Calculate total installs
    plugin_installs = await db.execute(
        select(func.sum(Plugin.installs_count))
        .where(Plugin.author_id == user_id)
    )
    template_installs = await db.execute(
        select(func.sum(TemplateModel.installs_count))
        .where(TemplateModel.author_id == user_id)
    )
    profile.total_installs = (plugin_installs.scalar_one() or 0) + (template_installs.scalar_one() or 0)

    # Calculate average rating
    plugin_ratings = await db.execute(
        select(func.avg(Plugin.rating_average))
        .where(and_(Plugin.author_id == user_id, Plugin.rating_count > 0))
    )
    template_ratings = await db.execute(
        select(func.avg(TemplateModel.rating_average))
        .where(and_(TemplateModel.author_id == user_id, TemplateModel.rating_count > 0))
    )

    plugin_avg = plugin_ratings.scalar_one() or 0
    template_avg = template_ratings.scalar_one() or 0
    profile.average_rating = (plugin_avg + template_avg) / 2 if (plugin_avg or template_avg) else 0.0

    await db.commit()


async def get_contributor_leaderboard(
    db: AsyncSession,
    sort_by: str = "total_downloads",
    limit: int = 50
) -> List[ContributorProfile]:
    """Get contributor leaderboard"""
    query = select(ContributorProfile)

    if sort_by == "total_installs":
        query = query.order_by(desc(ContributorProfile.total_installs))
    elif sort_by == "average_rating":
        query = query.order_by(desc(ContributorProfile.average_rating))
    elif sort_by == "contributions":
        query = query.order_by(
            desc(ContributorProfile.plugins_count + ContributorProfile.templates_count)
        )
    else:  # total_downloads
        query = query.order_by(desc(ContributorProfile.total_downloads))

    query = query.limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def award_badge(
    db: AsyncSession,
    user_id: int,
    badge_code: str
) -> bool:
    """Award a badge to a contributor"""
    profile = await get_contributor_profile(db, user_id)
    if not profile:
        return False

    badges = profile.badges or []
    if badge_code not in badges:
        badges.append(badge_code)
        profile.badges = badges
        await db.commit()
        return True

    return False


# =============================================================================
# Badge Operations
# =============================================================================

async def create_badge(
    db: AsyncSession,
    code: str,
    name: str,
    requirements: Dict[str, Any],
    **kwargs
) -> ContributorBadge:
    """Create a new badge"""
    badge = ContributorBadge(
        code=code,
        name=name,
        requirements=requirements,
        **kwargs
    )
    db.add(badge)
    await db.commit()
    await db.refresh(badge)
    return badge


async def list_badges(db: AsyncSession) -> List[ContributorBadge]:
    """List all available badges"""
    result = await db.execute(
        select(ContributorBadge)
        .where(ContributorBadge.is_active == True)
        .order_by(ContributorBadge.display_order)
    )
    return list(result.scalars().all())


async def get_badge_by_code(db: AsyncSession, code: str) -> Optional[ContributorBadge]:
    """Get badge by code"""
    result = await db.execute(
        select(ContributorBadge)
        .where(ContributorBadge.code == code)
    )
    return result.scalar_one_or_none()
