"""API routes for performance monitoring."""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from resoftai.db import get_db
from resoftai.auth.dependencies import get_current_active_user
from resoftai.models.user import User
from resoftai.monitoring.performance import performance_monitor


router = APIRouter(prefix="/monitoring", tags=["monitoring"])


class PerformanceMetricsResponse(BaseModel):
    """Performance metrics response schema."""
    request_count: int
    error_count: int
    average_response_time: float
    p95_response_time: float
    p99_response_time: float
    active_agents: int
    completed_workflows: int
    failed_workflows: int
    llm_requests: int
    llm_tokens_used: int
    file_operations: int
    database_operations: int


class AgentActivityResponse(BaseModel):
    """Agent activity response schema."""
    agent_id: str
    agent_type: str
    start_time: str
    end_time: Optional[str]
    duration: Optional[float]
    success: bool
    error_message: Optional[str]
    tokens_used: int
    files_processed: int


class MonitoringResponse(BaseModel):
    """Complete monitoring response."""
    metrics: PerformanceMetricsResponse
    agent_activities: Dict[str, AgentActivityResponse]


@router.get("/metrics", response_model=PerformanceMetricsResponse)
async def get_performance_metrics(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current performance metrics."""
    # Only admin users can access monitoring data
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin users can access monitoring data"
        )
    
    metrics = await performance_monitor.get_metrics()
    return PerformanceMetricsResponse(**metrics.__dict__)


@router.get("/agent-activities", response_model=Dict[str, AgentActivityResponse])
async def get_agent_activities(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current agent activities."""
    # Only admin users can access monitoring data
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin users can access monitoring data"
        )
    
    activities = await performance_monitor.get_agent_activities()
    
    # Convert to response format
    response = {}
    for agent_id, activity in activities.items():
        response[agent_id] = AgentActivityResponse(
            agent_id=agent_id,
            agent_type=activity.agent_type,
            start_time=activity.start_time.isoformat(),
            end_time=activity.end_time.isoformat() if activity.end_time else None,
            duration=activity.duration,
            success=activity.success,
            error_message=activity.error_message,
            tokens_used=activity.tokens_used,
            files_processed=activity.files_processed
        )
    
    return response


@router.get("/status", response_model=MonitoringResponse)
async def get_monitoring_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get complete monitoring status."""
    # Only admin users can access monitoring data
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin users can access monitoring data"
        )
    
    metrics = await performance_monitor.get_metrics()
    activities = await performance_monitor.get_agent_activities()
    
    # Convert activities to response format
    activities_response = {}
    for agent_id, activity in activities.items():
        activities_response[agent_id] = AgentActivityResponse(
            agent_id=agent_id,
            agent_type=activity.agent_type,
            start_time=activity.start_time.isoformat(),
            end_time=activity.end_time.isoformat() if activity.end_time else None,
            duration=activity.duration,
            success=activity.success,
            error_message=activity.error_message,
            tokens_used=activity.tokens_used,
            files_processed=activity.files_processed
        )
    
    return MonitoringResponse(
        metrics=PerformanceMetricsResponse(**metrics.__dict__),
        agent_activities=activities_response
    )


@router.post("/reset")
async def reset_monitoring(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Reset monitoring metrics."""
    # Only admin users can reset monitoring data
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin users can reset monitoring data"
        )
    
    await performance_monitor.reset_metrics()
    return {"message": "Monitoring metrics reset successfully"}