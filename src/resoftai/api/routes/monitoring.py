"""Enhanced performance monitoring and analytics API routes."""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from resoftai.db import get_db
from resoftai.auth.dependencies import get_current_active_user
from resoftai.models.user import User
from resoftai.models.performance_metrics import WorkflowMetrics, AgentPerformance, PerformanceAlert
from resoftai.crud.performance_metrics import (
    get_workflow_metrics,
    get_workflow_metrics_by_project,
    get_workflow_stats,
    get_agent_performance_by_role,
    get_agent_performance_summary,
    get_system_metrics_history,
    get_latest_system_metrics,
    get_llm_usage_by_user,
    get_llm_usage_summary,
    get_active_alerts,
    acknowledge_alert,
    resolve_alert
)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


# Response Models
class WorkflowMetricsResponse(BaseModel):
    """Workflow metrics response."""
    id: int
    project_id: int
    workflow_id: str
    start_time: datetime
    end_time: Optional[datetime]
    total_duration_seconds: Optional[float]
    stages_completed: int
    stages_failed: int
    current_stage: Optional[str]
    total_tokens_used: int
    total_llm_calls: int
    total_cache_hits: int
    total_cache_misses: int
    cache_hit_rate: Optional[float]
    status: str
    stage_timings: Optional[Dict[str, Any]]
    agent_metrics: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class AgentPerformanceResponse(BaseModel):
    """Agent performance response."""
    id: int
    agent_role: str
    execution_count: int
    success_count: int
    failure_count: int
    avg_execution_time: Optional[float]
    tokens_used: int
    llm_calls: int
    cache_hit_rate: Optional[float]

    class Config:
        from_attributes = True


class WorkflowStatsResponse(BaseModel):
    """Workflow statistics response."""
    total: int
    completed: int
    failed: int
    running: int
    avg_duration: float
    total_tokens: int
    avg_cache_hit_rate: float


class DashboardOverviewResponse(BaseModel):
    """Dashboard overview response."""
    active_workflows: int
    total_workflows_today: int
    avg_completion_time_seconds: float
    success_rate: float
    total_tokens_used_today: int
    cache_hit_rate: float
    active_alerts: int
    llm_cost_today_usd: float


class AgentMetricsResponse(BaseModel):
    """Agent metrics summary response."""
    agent_role: str
    total_executions: int
    success_rate: float
    avg_execution_time: float
    total_tokens: int
    cache_hit_rate: float


class SystemMetricsResponse(BaseModel):
    """System metrics response."""
    timestamp: datetime
    active_workflows: int
    total_workflows_completed: int
    total_workflows_failed: int
    avg_workflow_duration: Optional[float]
    total_tokens_used: int
    cache_hit_rate: Optional[float]
    cpu_usage_percent: Optional[float]
    memory_usage_mb: Optional[float]
    api_requests_total: int
    avg_response_time_ms: Optional[float]

    class Config:
        from_attributes = True


class LLMUsageSummaryResponse(BaseModel):
    """LLM usage summary response."""
    total_calls: int
    total_tokens: int
    total_cost: float
    by_provider: Dict[str, Dict[str, Any]]
    by_model: Dict[str, Dict[str, Any]]
    success_rate: float


class PerformanceAlertResponse(BaseModel):
    """Performance alert response."""
    id: int
    alert_type: str
    severity: str
    title: str
    description: str
    metric_name: str
    metric_value: float
    threshold_value: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TimeSeriesDataPoint(BaseModel):
    """Time series data point."""
    timestamp: datetime
    value: float


class TimeSeriesResponse(BaseModel):
    """Time series response."""
    metric_name: str
    data_points: List[TimeSeriesDataPoint]


# Endpoints

@router.get("/dashboard/overview", response_model=DashboardOverviewResponse)
async def get_dashboard_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get dashboard overview with key metrics.

    Returns:
        Dashboard overview with current system status
    """
    # Get workflow stats for today
    workflow_stats = await get_workflow_stats(db, days=1)

    # Get latest system metrics
    latest_metrics = await get_latest_system_metrics(db)

    # Get active alerts
    alerts = await get_active_alerts(db)

    # Get LLM usage for today
    llm_usage = await get_llm_usage_summary(db, days=1)

    # Calculate success rate
    success_rate = 0.0
    if workflow_stats["total"] > 0:
        success_rate = workflow_stats["completed"] / workflow_stats["total"]

    return {
        "active_workflows": workflow_stats["running"],
        "total_workflows_today": workflow_stats["total"],
        "avg_completion_time_seconds": workflow_stats["avg_duration"],
        "success_rate": success_rate,
        "total_tokens_used_today": llm_usage["total_tokens"],
        "cache_hit_rate": workflow_stats["avg_cache_hit_rate"],
        "active_alerts": len(alerts),
        "llm_cost_today_usd": llm_usage["total_cost"]
    }


@router.get("/workflows/{project_id}", response_model=List[WorkflowMetricsResponse])
async def get_project_workflow_metrics(
    project_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[WorkflowMetrics]:
    """
    Get workflow metrics for a specific project.

    Args:
        project_id: Project ID
        limit: Maximum number of results

    Returns:
        List of workflow metrics
    """
    metrics = await get_workflow_metrics_by_project(db, project_id, limit)
    return metrics


@router.get("/workflows/stats", response_model=WorkflowStatsResponse)
async def get_workflow_statistics(
    project_id: Optional[int] = None,
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get workflow statistics.

    Args:
        project_id: Optional project ID filter
        days: Number of days to include in stats

    Returns:
        Workflow statistics
    """
    return await get_workflow_stats(db, project_id, days)


@router.get("/agents/performance/{agent_role}", response_model=List[AgentPerformanceResponse])
async def get_agent_performance(
    agent_role: str,
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[AgentPerformance]:
    """
    Get performance metrics for a specific agent role.

    Args:
        agent_role: Agent role (e.g., 'developer', 'architect')
        days: Number of days to include

    Returns:
        Agent performance metrics
    """
    return await get_agent_performance_by_role(db, agent_role, days)


@router.get("/agents/summary", response_model=List[AgentMetricsResponse])
async def get_agents_summary(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """
    Get summary of all agent performance.

    Args:
        days: Number of days to include

    Returns:
        Summary of agent metrics
    """
    summary = await get_agent_performance_summary(db, days)

    # Convert to list format
    result = []
    for role, metrics in summary.items():
        total_exec = metrics["total_executions"]
        success_rate = metrics["total_successes"] / total_exec if total_exec > 0 else 0

        result.append({
            "agent_role": role,
            "total_executions": total_exec,
            "success_rate": success_rate,
            "avg_execution_time": metrics["avg_execution_time"],
            "total_tokens": metrics["total_tokens"],
            "cache_hit_rate": metrics["avg_cache_hit_rate"]
        })

    return result


@router.get("/system/metrics", response_model=List[SystemMetricsResponse])
async def get_system_metrics(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List:
    """
    Get system metrics history.

    Args:
        hours: Number of hours of history

    Returns:
        System metrics time series
    """
    return await get_system_metrics_history(db, hours)


@router.get("/system/timeseries/{metric_name}", response_model=TimeSeriesResponse)
async def get_metric_timeseries(
    metric_name: str,
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get time series data for a specific metric.

    Args:
        metric_name: Name of the metric
        hours: Number of hours of history

    Returns:
        Time series data
    """
    metrics_history = await get_system_metrics_history(db, hours)

    # Extract the requested metric
    data_points = []
    for metrics in metrics_history:
        if hasattr(metrics, metric_name):
            value = getattr(metrics, metric_name)
            if value is not None:
                data_points.append({
                    "timestamp": metrics.timestamp,
                    "value": float(value)
                })

    return {
        "metric_name": metric_name,
        "data_points": data_points
    }


@router.get("/llm/usage", response_model=LLMUsageSummaryResponse)
async def get_llm_usage(
    project_id: Optional[int] = None,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get LLM usage summary.

    Args:
        project_id: Optional project ID filter
        days: Number of days to include

    Returns:
        LLM usage summary
    """
    return await get_llm_usage_summary(
        db,
        user_id=current_user.id,
        project_id=project_id,
        days=days
    )


@router.get("/alerts", response_model=List[PerformanceAlertResponse])
async def get_alerts(
    severity: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[PerformanceAlert]:
    """
    Get active performance alerts.

    Args:
        severity: Optional severity filter (info, warning, critical)

    Returns:
        List of active alerts
    """
    return await get_active_alerts(db, severity)


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_performance_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, str]:
    """
    Acknowledge a performance alert.

    Args:
        alert_id: Alert ID

    Returns:
        Success message
    """
    alert = await acknowledge_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    await db.commit()
    return {"message": "Alert acknowledged"}


@router.post("/alerts/{alert_id}/resolve")
async def resolve_performance_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, str]:
    """
    Resolve a performance alert.

    Args:
        alert_id: Alert ID

    Returns:
        Success message
    """
    alert = await resolve_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    await db.commit()
    return {"message": "Alert resolved"}


@router.get("/analytics/trends")
async def get_performance_trends(
    metric: str = Query(..., description="Metric name (e.g., 'workflow_duration', 'token_usage')"),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get performance trends and analytics.

    Args:
        metric: Metric to analyze
        days: Number of days to analyze

    Returns:
        Trend analysis
    """
    workflow_stats = await get_workflow_stats(db, days=days)

    # Calculate trends (simplified version)
    # In a real implementation, you'd compare with previous period
    return {
        "metric": metric,
        "current_value": workflow_stats.get("avg_duration", 0),
        "trend": "stable",  # Would be calculated from historical data
        "change_percentage": 0.0,
        "period_days": days
    }


@router.get("/export/metrics")
async def export_metrics(
    format: str = Query("json", regex="^(json|csv)$"),
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Export performance metrics.

    Args:
        format: Export format (json or csv)
        days: Number of days to export

    Returns:
        Exported metrics data
    """
    workflow_stats = await get_workflow_stats(db, days=days)
    agent_summary = await get_agent_performance_summary(db, days=days)
    llm_usage = await get_llm_usage_summary(db, current_user.id, days=days)

    return {
        "export_format": format,
        "export_date": datetime.utcnow().isoformat(),
        "period_days": days,
        "workflow_stats": workflow_stats,
        "agent_summary": agent_summary,
        "llm_usage": llm_usage
    }
