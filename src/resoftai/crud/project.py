"""CRUD operations for Project model."""
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime

from resoftai.models.project import Project
from resoftai.utils.cache import cached, cache_manager
from resoftai.utils.performance import timing_decorator


@timing_decorator("crud.get_project_by_id")
@cached(key_func=lambda db, project_id: f"project:{project_id}", ttl=300)
async def get_project_by_id(db: AsyncSession, project_id: int) -> Optional[Project]:
    """
    Get project by ID with caching.

    Results are cached for 5 minutes.
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if project:
        # Convert to dict for caching
        return {
            'id': project.id,
            'user_id': project.user_id,
            'name': project.name,
            'requirements': project.requirements,
            'status': project.status,
            'progress': project.progress,
            'current_stage': project.current_stage,
            'llm_provider': project.llm_provider,
            'llm_model': project.llm_model,
            'created_at': project.created_at.isoformat() if project.created_at else None,
            'updated_at': project.updated_at.isoformat() if project.updated_at else None
        }
    return None


@timing_decorator("crud.get_projects_by_user")
async def get_projects_by_user(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None
) -> List[Project]:
    """
    Get projects for a user with pagination and filtering.

    Optimized with index on (user_id, created_at).

    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        status: Optional status filter

    Returns:
        List of Project objects
    """
    query = select(Project).where(Project.user_id == user_id)

    if status:
        query = query.where(Project.status == status)

    # Use covering index for better performance
    query = query.order_by(Project.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def count_user_projects(
    db: AsyncSession,
    user_id: int,
    status: Optional[str] = None
) -> int:
    """Count total projects for a user."""
    query = select(func.count(Project.id)).where(Project.user_id == user_id)

    if status:
        query = query.where(Project.status == status)

    result = await db.execute(query)
    return result.scalar_one()


async def create_project(
    db: AsyncSession,
    user_id: int,
    name: str,
    requirements: str,
    llm_provider: Optional[str] = None,
    llm_model: Optional[str] = None
) -> Project:
    """
    Create a new project.

    Args:
        db: Database session
        user_id: User ID
        name: Project name
        requirements: Project requirements
        llm_provider: LLM provider to use
        llm_model: LLM model to use

    Returns:
        Created Project object
    """
    project = Project(
        user_id=user_id,
        name=name,
        requirements=requirements,
        status="pending",
        progress=0,
        llm_provider=llm_provider,
        llm_model=llm_model,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)

    return project


async def update_project(
    db: AsyncSession,
    project_id: int,
    **kwargs
) -> Optional[Project]:
    """
    Update project fields.

    Args:
        db: Database session
        project_id: Project ID
        **kwargs: Fields to update

    Returns:
        Updated Project object or None
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        return None

    for key, value in kwargs.items():
        if hasattr(project, key):
            setattr(project, key, value)

    project.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(project)

    return project


async def delete_project(db: AsyncSession, project_id: int) -> bool:
    """
    Delete a project.

    Args:
        db: Database session
        project_id: Project ID

    Returns:
        True if deleted, False if not found
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        return False

    await db.delete(project)
    await db.commit()

    return True


@timing_decorator("crud.update_project_progress")
async def update_project_progress(
    db: AsyncSession,
    project_id: int,
    progress: int,
    stage: str = None,
    status: str = None
) -> Optional[Project]:
    """
    Update project progress.

    Invalidates cache after update.

    Args:
        db: Database session
        project_id: Project ID
        progress: Progress percentage (0-100)
        stage: Optional current stage
        status: Optional project status

    Returns:
        Updated Project object or None
    """
    update_data = {"progress": progress}
    if stage:
        update_data["current_stage"] = stage
    if status:
        update_data["status"] = status

    project = await update_project(db, project_id, **update_data)

    # Invalidate cache
    if project:
        await cache_manager.delete(f"project:{project_id}")

    return project


async def get_projects_by_ids(
    db: AsyncSession,
    project_ids: List[int]
) -> List[Project]:
    """
    Batch get projects by IDs.

    More efficient than multiple individual queries.

    Args:
        db: Database session
        project_ids: List of project IDs

    Returns:
        List of Project objects
    """
    if not project_ids:
        return []

    query = select(Project).where(Project.id.in_(project_ids))
    result = await db.execute(query)
    return list(result.scalars().all())


async def bulk_update_project_status(
    db: AsyncSession,
    project_ids: List[int],
    status: str
) -> int:
    """
    Bulk update project status.

    More efficient than individual updates.

    Args:
        db: Database session
        project_ids: List of project IDs
        status: New status

    Returns:
        Number of projects updated
    """
    if not project_ids:
        return 0

    from sqlalchemy import update

    stmt = (
        update(Project)
        .where(Project.id.in_(project_ids))
        .values(status=status, updated_at=datetime.utcnow())
    )

    result = await db.execute(stmt)
    await db.commit()

    # Invalidate caches
    for project_id in project_ids:
        await cache_manager.delete(f"project:{project_id}")

    return result.rowcount
