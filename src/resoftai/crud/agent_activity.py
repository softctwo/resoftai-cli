"""CRUD operations for agent activities."""
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from resoftai.models.agent_activity import AgentActivity


async def get_agent_activity(
    db: AsyncSession,
    activity_id: int
) -> Optional[AgentActivity]:
    """Get agent activity by ID."""
    result = await db.execute(
        select(AgentActivity).where(AgentActivity.id == activity_id)
    )
    return result.scalar_one_or_none()


async def get_agent_activities_by_project(
    db: AsyncSession,
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    agent_role: Optional[str] = None,
    status: Optional[str] = None
) -> List[AgentActivity]:
    """Get agent activities for a project with optional filters."""
    query = select(AgentActivity).where(AgentActivity.project_id == project_id)

    if agent_role:
        query = query.where(AgentActivity.agent_role == agent_role)

    if status:
        query = query.where(AgentActivity.status == status)

    query = query.order_by(AgentActivity.started_at.desc())
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_active_agents(
    db: AsyncSession,
    project_id: Optional[int] = None
) -> List[AgentActivity]:
    """Get all currently active agents (working status)."""
    query = select(AgentActivity).where(AgentActivity.status == "working")

    if project_id:
        query = query.where(AgentActivity.project_id == project_id)

    query = query.order_by(AgentActivity.started_at.desc())

    result = await db.execute(query)
    return list(result.scalars().all())


async def create_agent_activity(
    db: AsyncSession,
    project_id: int,
    agent_role: str,
    status: str = "idle",
    current_task: Optional[str] = None
) -> AgentActivity:
    """Create a new agent activity record."""
    activity = AgentActivity(
        project_id=project_id,
        agent_role=agent_role,
        status=status,
        current_task=current_task,
        tokens_used=0
    )

    db.add(activity)
    await db.flush()
    await db.refresh(activity)

    return activity


async def update_agent_activity(
    db: AsyncSession,
    activity_id: int,
    status: Optional[str] = None,
    current_task: Optional[str] = None,
    tokens_used: Optional[int] = None
) -> Optional[AgentActivity]:
    """Update agent activity."""
    activity = await get_agent_activity(db, activity_id)

    if not activity:
        return None

    if status is not None:
        activity.status = status

    if current_task is not None:
        activity.current_task = current_task

    if tokens_used is not None:
        activity.tokens_used = tokens_used

    # Update completed_at if status is completed or failed
    if status in ("completed", "failed"):
        from datetime import datetime
        activity.completed_at = datetime.utcnow()

    await db.flush()
    await db.refresh(activity)

    return activity


async def delete_agent_activity(
    db: AsyncSession,
    activity_id: int
) -> bool:
    """Delete agent activity."""
    activity = await get_agent_activity(db, activity_id)

    if not activity:
        return False

    await db.delete(activity)
    await db.flush()

    return True


async def count_project_agent_activities(
    db: AsyncSession,
    project_id: int,
    status: Optional[str] = None
) -> int:
    """Count agent activities for a project."""
    from sqlalchemy import func

    query = select(func.count(AgentActivity.id)).where(
        AgentActivity.project_id == project_id
    )

    if status:
        query = query.where(AgentActivity.status == status)

    result = await db.execute(query)
    return result.scalar_one()
