"""
CRUD operations for template community features.

Handles database operations for templates, versions, ratings, and comments.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from resoftai.models.template_community import (
    TemplateModel,
    TemplateVersion,
    TemplateRating,
    TemplateComment,
    TemplateLike,
    TemplateVisibility,
    TemplateStatus
)


# ===== Template CRUD =====

async def create_template(
    db: AsyncSession,
    author_id: int,
    template_id: str,
    name: str,
    description: str,
    category: str,
    visibility: TemplateVisibility = TemplateVisibility.PUBLIC,
    tags: List[str] = None,
    icon_url: str = None
) -> TemplateModel:
    """Create a new template."""
    template = TemplateModel(
        template_id=template_id,
        name=name,
        description=description,
        category=category,
        author_id=author_id,
        visibility=visibility,
        tags=tags or [],
        icon_url=icon_url,
        status=TemplateStatus.DRAFT
    )

    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


async def get_template(
    db: AsyncSession,
    template_id: int,
    user_id: Optional[int] = None
) -> Optional[TemplateModel]:
    """Get template by ID with visibility check."""
    query = select(TemplateModel).where(TemplateModel.id == template_id)

    # Add visibility filter if user is specified
    if user_id:
        query = query.where(
            or_(
                TemplateModel.visibility == TemplateVisibility.PUBLIC,
                TemplateModel.author_id == user_id
            )
        )
    else:
        query = query.where(TemplateModel.visibility == TemplateVisibility.PUBLIC)

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_template_by_template_id(
    db: AsyncSession,
    template_id: str,
    user_id: Optional[int] = None
) -> Optional[TemplateModel]:
    """Get template by template_id string."""
    query = select(TemplateModel).where(TemplateModel.template_id == template_id)

    if user_id:
        query = query.where(
            or_(
                TemplateModel.visibility == TemplateVisibility.PUBLIC,
                TemplateModel.author_id == user_id
            )
        )
    else:
        query = query.where(TemplateModel.visibility == TemplateVisibility.PUBLIC)

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def list_templates(
    db: AsyncSession,
    user_id: Optional[int] = None,
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    visibility: Optional[TemplateVisibility] = None,
    status: Optional[TemplateStatus] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "created_at",
    sort_desc: bool = True
) -> tuple[List[TemplateModel], int]:
    """List templates with filters."""
    # Build base query
    query = select(TemplateModel)
    count_query = select(func.count(TemplateModel.id))

    # Apply filters
    filters = []

    # Visibility filter
    if user_id:
        filters.append(
            or_(
                TemplateModel.visibility == TemplateVisibility.PUBLIC,
                TemplateModel.author_id == user_id
            )
        )
    else:
        filters.append(TemplateModel.visibility == TemplateVisibility.PUBLIC)

    # Status filter (default to published for public)
    if status:
        filters.append(TemplateModel.status == status)
    elif not user_id:
        filters.append(TemplateModel.status == TemplateStatus.PUBLISHED)

    # Category filter
    if category:
        filters.append(TemplateModel.category == category)

    # Tags filter (contains any of the tags)
    if tags:
        tag_filters = [TemplateModel.tags.contains([tag]) for tag in tags]
        filters.append(or_(*tag_filters))

    # Search filter
    if search:
        search_filter = or_(
            TemplateModel.name.ilike(f"%{search}%"),
            TemplateModel.description.ilike(f"%{search}%"),
            TemplateModel.template_id.ilike(f"%{search}%")
        )
        filters.append(search_filter)

    # Apply all filters
    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))

    # Get total count
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Apply sorting
    if sort_by == "rating":
        order_by = TemplateModel.average_rating
    elif sort_by == "downloads":
        order_by = TemplateModel.download_count
    elif sort_by == "updated_at":
        order_by = TemplateModel.updated_at
    else:  # created_at
        order_by = TemplateModel.created_at

    query = query.order_by(desc(order_by) if sort_desc else order_by)

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    templates = result.scalars().all()

    return list(templates), total


async def update_template(
    db: AsyncSession,
    template_id: int,
    user_id: int,
    **kwargs
) -> Optional[TemplateModel]:
    """Update template (only by author)."""
    template = await get_template(db, template_id, user_id)

    if not template or template.author_id != user_id:
        return None

    # Update allowed fields
    allowed_fields = [
        'name', 'description', 'category', 'tags', 'icon_url',
        'screenshot_urls', 'visibility', 'status'
    ]

    for field, value in kwargs.items():
        if field in allowed_fields and value is not None:
            setattr(template, field, value)

    template.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(template)
    return template


async def publish_template(
    db: AsyncSession,
    template_id: int,
    user_id: int
) -> Optional[TemplateModel]:
    """Publish a template."""
    template = await get_template(db, template_id, user_id)

    if not template or template.author_id != user_id:
        return None

    template.status = TemplateStatus.PUBLISHED
    template.published_at = datetime.utcnow()
    template.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(template)
    return template


async def delete_template(
    db: AsyncSession,
    template_id: int,
    user_id: int
) -> bool:
    """Delete template (only by author)."""
    template = await get_template(db, template_id, user_id)

    if not template or template.author_id != user_id:
        return False

    await db.delete(template)
    await db.commit()
    return True


async def increment_template_stats(
    db: AsyncSession,
    template_id: int,
    stat_name: str
) -> None:
    """Increment template statistics."""
    query = select(TemplateModel).where(TemplateModel.id == template_id)
    result = await db.execute(query)
    template = result.scalar_one_or_none()

    if template and hasattr(template, stat_name):
        current = getattr(template, stat_name)
        setattr(template, stat_name, current + 1)
        await db.commit()


# ===== Template Version CRUD =====

async def create_template_version(
    db: AsyncSession,
    template_id: int,
    user_id: int,
    version: str,
    variables: List[Dict],
    files: List[Dict],
    directories: List[str],
    version_name: str = None,
    changelog: str = None,
    setup_commands: List[str] = None,
    requirements: Dict = None,
    dependencies: List[str] = None,
    is_stable: bool = False
) -> Optional[TemplateVersion]:
    """Create a new template version."""
    # Verify template exists and user is author
    template = await get_template(db, template_id, user_id)
    if not template or template.author_id != user_id:
        return None

    # Set previous versions as not latest
    query = select(TemplateVersion).where(
        and_(
            TemplateVersion.template_id == template_id,
            TemplateVersion.is_latest == True
        )
    )
    result = await db.execute(query)
    for prev_version in result.scalars():
        prev_version.is_latest = False

    # Create new version
    template_version = TemplateVersion(
        template_id=template_id,
        version=version,
        version_name=version_name,
        changelog=changelog,
        variables=variables,
        files=files,
        directories=directories,
        setup_commands=setup_commands or [],
        requirements=requirements or {},
        dependencies=dependencies or [],
        is_stable=is_stable,
        is_latest=True,
        created_by_id=user_id
    )

    db.add(template_version)

    # Update template's current_version_id
    await db.flush()  # Get the new version's ID
    template.current_version_id = template_version.id
    template.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(template_version)
    return template_version


async def get_template_versions(
    db: AsyncSession,
    template_id: int
) -> List[TemplateVersion]:
    """Get all versions of a template."""
    query = select(TemplateVersion).where(
        TemplateVersion.template_id == template_id
    ).order_by(desc(TemplateVersion.created_at))

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_template_version(
    db: AsyncSession,
    template_id: int,
    version: str
) -> Optional[TemplateVersion]:
    """Get specific version of a template."""
    query = select(TemplateVersion).where(
        and_(
            TemplateVersion.template_id == template_id,
            TemplateVersion.version == version
        )
    )

    result = await db.execute(query)
    return result.scalar_one_or_none()


# ===== Rating CRUD =====

async def create_or_update_rating(
    db: AsyncSession,
    template_id: int,
    user_id: int,
    rating: int,
    review: str = None
) -> TemplateRating:
    """Create or update a rating."""
    # Check if rating exists
    query = select(TemplateRating).where(
        and_(
            TemplateRating.template_id == template_id,
            TemplateRating.user_id == user_id
        )
    )
    result = await db.execute(query)
    existing_rating = result.scalar_one_or_none()

    if existing_rating:
        # Update existing rating
        existing_rating.rating = rating
        existing_rating.review = review
        existing_rating.updated_at = datetime.utcnow()
        template_rating = existing_rating
    else:
        # Create new rating
        template_rating = TemplateRating(
            template_id=template_id,
            user_id=user_id,
            rating=rating,
            review=review
        )
        db.add(template_rating)

    # Update template's average rating
    await db.flush()
    await update_template_rating_stats(db, template_id)

    await db.commit()
    await db.refresh(template_rating)
    return template_rating


async def update_template_rating_stats(
    db: AsyncSession,
    template_id: int
) -> None:
    """Recalculate template's rating statistics."""
    query = select(
        func.avg(TemplateRating.rating),
        func.count(TemplateRating.id)
    ).where(TemplateRating.template_id == template_id)

    result = await db.execute(query)
    avg_rating, count = result.one()

    # Update template
    template_query = select(TemplateModel).where(TemplateModel.id == template_id)
    template_result = await db.execute(template_query)
    template = template_result.scalar_one_or_none()

    if template:
        template.average_rating = float(avg_rating) if avg_rating else 0.0
        template.rating_count = count or 0


async def get_template_ratings(
    db: AsyncSession,
    template_id: int,
    skip: int = 0,
    limit: int = 20
) -> tuple[List[TemplateRating], int]:
    """Get ratings for a template."""
    # Count query
    count_query = select(func.count(TemplateRating.id)).where(
        TemplateRating.template_id == template_id
    )
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Ratings query
    query = select(TemplateRating).where(
        TemplateRating.template_id == template_id
    ).order_by(desc(TemplateRating.created_at)).offset(skip).limit(limit)

    result = await db.execute(query)
    ratings = result.scalars().all()

    return list(ratings), total


# ===== Comment CRUD =====

async def create_comment(
    db: AsyncSession,
    template_id: int,
    user_id: int,
    content: str,
    parent_id: Optional[int] = None
) -> TemplateComment:
    """Create a comment."""
    comment = TemplateComment(
        template_id=template_id,
        user_id=user_id,
        content=content,
        parent_id=parent_id
    )

    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def update_comment(
    db: AsyncSession,
    comment_id: int,
    user_id: int,
    content: str
) -> Optional[TemplateComment]:
    """Update a comment (only by author)."""
    query = select(TemplateComment).where(TemplateComment.id == comment_id)
    result = await db.execute(query)
    comment = result.scalar_one_or_none()

    if not comment or comment.user_id != user_id:
        return None

    comment.content = content
    comment.is_edited = True
    comment.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(comment)
    return comment


async def delete_comment(
    db: AsyncSession,
    comment_id: int,
    user_id: int
) -> bool:
    """Delete a comment (only by author)."""
    query = select(TemplateComment).where(TemplateComment.id == comment_id)
    result = await db.execute(query)
    comment = result.scalar_one_or_none()

    if not comment or comment.user_id != user_id:
        return False

    comment.is_deleted = True
    comment.content = "[deleted]"
    await db.commit()
    return True


async def get_template_comments(
    db: AsyncSession,
    template_id: int,
    parent_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50
) -> tuple[List[TemplateComment], int]:
    """Get comments for a template."""
    # Base query
    filters = [TemplateComment.template_id == template_id]

    if parent_id is not None:
        filters.append(TemplateComment.parent_id == parent_id)
    else:
        filters.append(TemplateComment.parent_id.is_(None))

    # Count query
    count_query = select(func.count(TemplateComment.id)).where(and_(*filters))
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Comments query
    query = select(TemplateComment).where(and_(*filters)).order_by(
        desc(TemplateComment.created_at)
    ).offset(skip).limit(limit)

    result = await db.execute(query)
    comments = result.scalars().all()

    return list(comments), total


# ===== Like/Favorite CRUD =====

async def toggle_like(
    db: AsyncSession,
    template_id: int,
    user_id: int
) -> bool:
    """Toggle like status. Returns True if liked, False if unliked."""
    query = select(TemplateLike).where(
        and_(
            TemplateLike.template_id == template_id,
            TemplateLike.user_id == user_id
        )
    )
    result = await db.execute(query)
    like = result.scalar_one_or_none()

    if like:
        # Unlike
        await db.delete(like)
        await db.commit()
        return False
    else:
        # Like
        like = TemplateLike(template_id=template_id, user_id=user_id)
        db.add(like)
        await db.commit()
        return True


async def get_user_liked_templates(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 50
) -> tuple[List[TemplateModel], int]:
    """Get templates liked by a user."""
    # Count query
    count_query = select(func.count(TemplateLike.id)).where(
        TemplateLike.user_id == user_id
    )
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Templates query
    query = select(TemplateModel).join(TemplateLike).where(
        TemplateLike.user_id == user_id
    ).order_by(desc(TemplateLike.created_at)).offset(skip).limit(limit)

    result = await db.execute(query)
    templates = result.scalars().all()

    return list(templates), total
