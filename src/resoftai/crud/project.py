"""CRUD operations for Project model."""
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from resoftai.models.project import Project


async def get_project_by_id(db: AsyncSession, project_id: int) -> Optional[Project]:
    """Get project by ID."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    return result.scalar_one_or_none()


async def get_projects_by_user(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None
) -> List[Project]:
    """
    Get projects for a user with pagination and filtering.

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


async def update_project_progress(
    db: AsyncSession,
    project_id: int,
    progress: int,
    stage: str = None,
    status: str = None
) -> Optional[Project]:
    """
    Update project progress.

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

    return await update_project(db, project_id, **update_data)
