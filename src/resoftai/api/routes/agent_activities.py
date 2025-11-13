"""API routes for agent activities."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from resoftai.db import get_db
from resoftai.auth.dependencies import get_current_active_user
from resoftai.models.user import User
from resoftai.models.agent_activity import AgentActivity
from resoftai.crud import agent_activity as crud
from resoftai.crud.project import get_project


router = APIRouter(prefix="/agent-activities", tags=["agent-activities"])


# Pydantic schemas
class AgentActivityCreate(BaseModel):
    """Schema for creating agent activity."""
    project_id: int
    agent_role: str
    status: str = "idle"
    current_task: Optional[str] = None


class AgentActivityUpdate(BaseModel):
    """Schema for updating agent activity."""
    status: Optional[str] = None
    current_task: Optional[str] = None
    tokens_used: Optional[int] = None


class AgentActivityResponse(BaseModel):
    """Schema for agent activity response."""
    id: int
    project_id: int
    agent_role: str
    status: str
    current_task: Optional[str]
    tokens_used: int
    started_at: str
    completed_at: Optional[str]

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, activity: AgentActivity):
        return cls(
            id=activity.id,
            project_id=activity.project_id,
            agent_role=activity.agent_role,
            status=activity.status,
            current_task=activity.current_task,
            tokens_used=activity.tokens_used,
            started_at=activity.started_at.isoformat(),
            completed_at=activity.completed_at.isoformat() if activity.completed_at else None
        )


class AgentActivityListResponse(BaseModel):
    """Schema for agent activity list response."""
    activities: List[AgentActivityResponse]
    total: int
    skip: int
    limit: int


@router.get("", response_model=AgentActivityListResponse)
async def list_agent_activities(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    agent_role: Optional[str] = Query(None, description="Filter by agent role"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List agent activities with optional filters."""
    if not project_id:
        raise HTTPException(
            status_code=400,
            detail="project_id is required"
        )

    # Verify user has access to the project
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this project"
        )

    # Get activities
    activities = await crud.get_agent_activities_by_project(
        db,
        project_id=project_id,
        skip=skip,
        limit=limit,
        agent_role=agent_role,
        status=status
    )

    # Count total
    total = await crud.count_project_agent_activities(
        db,
        project_id=project_id,
        status=status
    )

    return AgentActivityListResponse(
        activities=[AgentActivityResponse.from_orm(a) for a in activities],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/active", response_model=List[AgentActivityResponse])
async def list_active_agents(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List all currently active agents (working status)."""
    if project_id:
        # Verify user has access to the project
        project = await get_project(db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        if project.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access this project"
            )

    activities = await crud.get_active_agents(db, project_id=project_id)

    return [AgentActivityResponse.from_orm(a) for a in activities]


@router.get("/{activity_id}", response_model=AgentActivityResponse)
async def get_agent_activity(
    activity_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get agent activity by ID."""
    activity = await crud.get_agent_activity(db, activity_id)

    if not activity:
        raise HTTPException(status_code=404, detail="Agent activity not found")

    # Verify user has access
    project = await get_project(db, activity.project_id)
    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this activity"
        )

    return AgentActivityResponse.from_orm(activity)


@router.post("", response_model=AgentActivityResponse, status_code=201)
async def create_agent_activity(
    activity_data: AgentActivityCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new agent activity."""
    # Verify user has access to the project
    project = await get_project(db, activity_data.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to modify this project"
        )

    activity = await crud.create_agent_activity(
        db,
        project_id=activity_data.project_id,
        agent_role=activity_data.agent_role,
        status=activity_data.status,
        current_task=activity_data.current_task
    )

    await db.commit()

    return AgentActivityResponse.from_orm(activity)


@router.put("/{activity_id}", response_model=AgentActivityResponse)
async def update_agent_activity(
    activity_id: int,
    activity_data: AgentActivityUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update agent activity."""
    activity = await crud.get_agent_activity(db, activity_id)

    if not activity:
        raise HTTPException(status_code=404, detail="Agent activity not found")

    # Verify user has access
    project = await get_project(db, activity.project_id)
    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to modify this activity"
        )

    activity = await crud.update_agent_activity(
        db,
        activity_id=activity_id,
        status=activity_data.status,
        current_task=activity_data.current_task,
        tokens_used=activity_data.tokens_used
    )

    await db.commit()

    return AgentActivityResponse.from_orm(activity)


@router.delete("/{activity_id}", status_code=204)
async def delete_agent_activity(
    activity_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete agent activity."""
    activity = await crud.get_agent_activity(db, activity_id)

    if not activity:
        raise HTTPException(status_code=404, detail="Agent activity not found")

    # Verify user has access
    project = await get_project(db, activity.project_id)
    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this activity"
        )

    await crud.delete_agent_activity(db, activity_id)
    await db.commit()

    return None
