"""Projects API routes."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from resoftai.db import get_db
from resoftai.models.user import User
from resoftai.models.project import Project
from resoftai.crud.project import (
    get_project_by_id,
    get_projects_by_user,
    count_user_projects,
    create_project as create_project_db,
    update_project,
    delete_project,
    update_project_progress,
)
from resoftai.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/projects", tags=["projects"])


# Request/Response Models
class ProjectCreate(BaseModel):
    """Project creation request."""
    name: str = Field(..., min_length=1, max_length=200)
    requirements: str = Field(..., min_length=10)
    llm_provider: Optional[str] = Field(default=None)
    llm_model: Optional[str] = Field(default=None)


class ProjectUpdate(BaseModel):
    """Project update request."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    requirements: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    progress: Optional[int] = Field(default=None, ge=0, le=100)
    current_stage: Optional[str] = Field(default=None)


class ProjectResponse(BaseModel):
    """Project response model."""
    id: int
    name: str
    requirements: str
    status: str
    progress: int
    current_stage: Optional[str]
    llm_provider: Optional[str]
    llm_model: Optional[str]
    user_id: int
    created_at: str
    updated_at: str
    completed_at: Optional[str]

    class Config:
        from_attributes = True

    @staticmethod
    def from_orm(project: Project) -> "ProjectResponse":
        """Convert ORM model to response."""
        return ProjectResponse(
            id=project.id,
            name=project.name,
            requirements=project.requirements,
            status=project.status,
            progress=project.progress,
            current_stage=project.current_stage,
            llm_provider=project.llm_provider,
            llm_model=project.llm_model,
            user_id=project.user_id,
            created_at=project.created_at.isoformat(),
            updated_at=project.updated_at.isoformat(),
            completed_at=project.completed_at.isoformat() if project.completed_at else None
        )


class ProjectListResponse(BaseModel):
    """Project list response with pagination."""
    projects: List[ProjectResponse]
    total: int
    skip: int
    limit: int


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new project.

    Args:
        project_data: Project creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created project
    """
    project = await create_project_db(
        db=db,
        user_id=current_user.id,
        name=project_data.name,
        requirements=project_data.requirements,
        llm_provider=project_data.llm_provider,
        llm_model=project_data.llm_model
    )

    return ProjectResponse.from_orm(project)


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List user's projects with pagination and filtering.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records
        status: Optional status filter
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of projects with pagination info
    """
    projects = await get_projects_by_user(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status
    )

    total = await count_user_projects(
        db=db,
        user_id=current_user.id,
        status=status
    )

    return ProjectListResponse(
        projects=[ProjectResponse.from_orm(p) for p in projects],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get project by ID.

    Args:
        project_id: Project ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Project details

    Raises:
        HTTPException: If project not found or access denied
    """
    project = await get_project_by_id(db, project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Check ownership
    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return ProjectResponse.from_orm(project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project_endpoint(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update project.

    Args:
        project_id: Project ID
        project_data: Project update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated project

    Raises:
        HTTPException: If project not found or access denied
    """
    # Check ownership
    existing_project = await get_project_by_id(db, project_id)
    if not existing_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    if existing_project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Update project
    update_data = project_data.dict(exclude_unset=True)
    project = await update_project(db, project_id, **update_data)

    return ProjectResponse.from_orm(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_endpoint(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete project.

    Args:
        project_id: Project ID
        current_user: Current authenticated user
        db: Database session

    Raises:
        HTTPException: If project not found or access denied
    """
    # Check ownership
    project = await get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Delete project
    await delete_project(db, project_id)
