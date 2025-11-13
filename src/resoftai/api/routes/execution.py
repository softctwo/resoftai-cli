"""API routes for project execution."""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from resoftai.db import get_db
from resoftai.auth.dependencies import get_current_active_user
from resoftai.models.user import User
from resoftai.crud.project import get_project_by_id as get_project
from resoftai.orchestration.executor import ProjectExecutor

router = APIRouter(prefix="/execution", tags=["execution"])


# Pydantic schemas

class ExecutionStartResponse(BaseModel):
    """Schema for execution start response."""
    project_id: int
    status: str
    message: str


class ExecutionStatusResponse(BaseModel):
    """Schema for execution status response."""
    project_id: int
    is_running: bool
    progress: Dict[str, Any]
    execution_time: float = None


class ExecutionArtifactsResponse(BaseModel):
    """Schema for execution artifacts response."""
    project_id: int
    artifacts: Dict[str, Any]


# Endpoints

@router.post("/{project_id}/start", response_model=ExecutionStartResponse)
async def start_project_execution(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Start project execution.

    This will start the multi-agent workflow to develop the project.
    """
    # Get project
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify ownership
    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to execute this project"
        )

    # Check if already running
    if ProjectExecutor.get_executor(project_id):
        raise HTTPException(
            status_code=400,
            detail="Project is already running"
        )

    try:
        # Start execution
        await ProjectExecutor.start_execution(project, db)

        return ExecutionStartResponse(
            project_id=project_id,
            status="started",
            message="Project execution started successfully"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start execution: {str(e)}"
        )


@router.post("/{project_id}/stop", response_model=ExecutionStartResponse)
async def stop_project_execution(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Stop project execution.

    This will cancel the running workflow.
    """
    # Get project
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify ownership
    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to stop this project"
        )

    # Stop execution
    stopped = await ProjectExecutor.stop_execution(project_id)

    if not stopped:
        raise HTTPException(
            status_code=400,
            detail="Project is not running"
        )

    return ExecutionStartResponse(
        project_id=project_id,
        status="stopped",
        message="Project execution stopped successfully"
    )


@router.get("/{project_id}/status", response_model=ExecutionStatusResponse)
async def get_execution_status(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get project execution status.

    Returns current execution progress and status.
    """
    # Get project
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify ownership
    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this project"
        )

    # Get executor
    executor = ProjectExecutor.get_executor(project_id)

    if not executor:
        return ExecutionStatusResponse(
            project_id=project_id,
            is_running=False,
            progress={
                "progress_percentage": 0,
                "current_stage": "not_started",
                "stage_history": [],
                "errors": [],
                "total_tokens": 0,
                "total_requests": 0
            }
        )

    return ExecutionStatusResponse(
        project_id=project_id,
        is_running=executor.is_running,
        progress=executor.get_progress(),
        execution_time=executor.get_execution_time()
    )


@router.get("/{project_id}/artifacts", response_model=ExecutionArtifactsResponse)
async def get_execution_artifacts(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get project execution artifacts.

    Returns all generated artifacts (requirements, architecture, code, etc.)
    """
    # Get project
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify ownership
    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this project"
        )

    # Get executor
    executor = ProjectExecutor.get_executor(project_id)

    if not executor:
        raise HTTPException(
            status_code=404,
            detail="No execution found for this project"
        )

    return ExecutionArtifactsResponse(
        project_id=project_id,
        artifacts=executor.get_artifacts()
    )
