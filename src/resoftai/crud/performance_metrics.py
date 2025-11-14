"""CRUD operations for performance metrics."""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload

from resoftai.models.performance_metrics import (
    WorkflowMetrics,
    AgentPerformance,
    SystemMetrics,
    LLMUsageMetrics,
    PerformanceAlert
)

logger = logging.getLogger(__name__)


# WorkflowMetrics CRUD
async def create_workflow_metrics(
    db: AsyncSession,
    project_id: int,
    workflow_id: str,
    **kwargs
) -> WorkflowMetrics:
    """Create a new workflow metrics entry."""
    metrics = WorkflowMetrics(
        project_id=project_id,
        workflow_id=workflow_id,
        start_time=kwargs.get('start_time', datetime.utcnow()),
        **{k: v for k, v in kwargs.items() if k != 'start_time'}
    )
    db.add(metrics)
    await db.flush()
    await db.refresh(metrics)
    return metrics


async def get_workflow_metrics(
    db: AsyncSession,
    metrics_id: int
) -> Optional[WorkflowMetrics]:
    """Get workflow metrics by ID."""
    result = await db.execute(
        select(WorkflowMetrics)
        .options(selectinload(WorkflowMetrics.agent_performance))
        .where(WorkflowMetrics.id == metrics_id)
    )
    return result.scalar_one_or_none()


async def get_workflow_metrics_by_project(
    db: AsyncSession,
    project_id: int,
    limit: int = 10
) -> List[WorkflowMetrics]:
    """Get workflow metrics for a project."""
    result = await db.execute(
        select(WorkflowMetrics)
        .where(WorkflowMetrics.project_id == project_id)
        .order_by(desc(WorkflowMetrics.created_at))
        .limit(limit)
    )
    return list(result.scalars().all())


async def update_workflow_metrics(
    db: AsyncSession,
    metrics_id: int,
    **kwargs
) -> Optional[WorkflowMetrics]:
    """Update workflow metrics."""
    metrics = await get_workflow_metrics(db, metrics_id)
    if not metrics:
        return None

    for key, value in kwargs.items():
        if hasattr(metrics, key):
            setattr(metrics, key, value)

    # Calculate derived metrics
    if metrics.end_time and metrics.start_time:
        metrics.total_duration_seconds = (metrics.end_time - metrics.start_time).total_seconds()

    if metrics.stage_timings:
        durations = list(metrics.stage_timings.values())
        if durations:
            metrics.avg_stage_duration = sum(durations) / len(durations)

    if metrics.total_cache_hits + metrics.total_cache_misses > 0:
        metrics.cache_hit_rate = metrics.total_cache_hits / (metrics.total_cache_hits + metrics.total_cache_misses)

    await db.flush()
    await db.refresh(metrics)
    return metrics


async def get_workflow_stats(
    db: AsyncSession,
    project_id: Optional[int] = None,
    days: int = 7
) -> Dict[str, Any]:
    """Get workflow statistics."""
    since = datetime.utcnow() - timedelta(days=days)

    query = select(WorkflowMetrics).where(WorkflowMetrics.created_at >= since)
    if project_id:
        query = query.where(WorkflowMetrics.project_id == project_id)

    result = await db.execute(query)
    workflows = list(result.scalars().all())

    if not workflows:
        return {
            "total": 0,
            "completed": 0,
            "failed": 0,
            "running": 0,
            "avg_duration": 0,
            "total_tokens": 0,
            "avg_cache_hit_rate": 0
        }

    completed = [w for w in workflows if w.status == "completed"]
    failed = [w for w in workflows if w.status == "failed"]
    running = [w for w in workflows if w.status == "running"]

    durations = [w.total_duration_seconds for w in completed if w.total_duration_seconds]
    cache_rates = [w.cache_hit_rate for w in workflows if w.cache_hit_rate is not None]

    return {
        "total": len(workflows),
        "completed": len(completed),
        "failed": len(failed),
        "running": len(running),
        "avg_duration": sum(durations) / len(durations) if durations else 0,
        "total_tokens": sum(w.total_tokens_used for w in workflows),
        "avg_cache_hit_rate": sum(cache_rates) / len(cache_rates) if cache_rates else 0
    }


# AgentPerformance CRUD
async def create_agent_performance(
    db: AsyncSession,
    workflow_metrics_id: int,
    agent_role: str,
    **kwargs
) -> AgentPerformance:
    """Create agent performance entry."""
    performance = AgentPerformance(
        workflow_metrics_id=workflow_metrics_id,
        agent_role=agent_role,
        **kwargs
    )
    db.add(performance)
    await db.flush()
    await db.refresh(performance)
    return performance


async def update_agent_performance(
    db: AsyncSession,
    performance_id: int,
    **kwargs
) -> Optional[AgentPerformance]:
    """Update agent performance metrics."""
    result = await db.execute(
        select(AgentPerformance).where(AgentPerformance.id == performance_id)
    )
    performance = result.scalar_one_or_none()

    if not performance:
        return None

    for key, value in kwargs.items():
        if hasattr(performance, key):
            setattr(performance, key, value)

    # Calculate derived metrics
    if performance.execution_count > 0:
        performance.avg_execution_time = performance.total_execution_time / performance.execution_count

    if performance.llm_calls > 0:
        performance.avg_tokens_per_call = performance.tokens_used / performance.llm_calls

    if performance.cache_hits + performance.cache_misses > 0:
        performance.cache_hit_rate = performance.cache_hits / (performance.cache_hits + performance.cache_misses)

    await db.flush()
    await db.refresh(performance)
    return performance


async def get_agent_performance_by_role(
    db: AsyncSession,
    agent_role: str,
    days: int = 7
) -> List[AgentPerformance]:
    """Get performance metrics for a specific agent role."""
    since = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(AgentPerformance)
        .where(
            and_(
                AgentPerformance.agent_role == agent_role,
                AgentPerformance.created_at >= since
            )
        )
        .order_by(desc(AgentPerformance.created_at))
    )
    return list(result.scalars().all())


async def get_agent_performance_summary(
    db: AsyncSession,
    days: int = 7
) -> Dict[str, Any]:
    """Get summary of agent performance across all agents."""
    since = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(AgentPerformance).where(AgentPerformance.created_at >= since)
    )
    performances = list(result.scalars().all())

    # Aggregate by agent role
    summary = {}
    for perf in performances:
        role = perf.agent_role
        if role not in summary:
            summary[role] = {
                "total_executions": 0,
                "total_successes": 0,
                "total_failures": 0,
                "total_tokens": 0,
                "avg_execution_time": 0,
                "avg_cache_hit_rate": 0
            }

        summary[role]["total_executions"] += perf.execution_count
        summary[role]["total_successes"] += perf.success_count
        summary[role]["total_failures"] += perf.failure_count
        summary[role]["total_tokens"] += perf.tokens_used

    return summary


# SystemMetrics CRUD
async def create_system_metrics(
    db: AsyncSession,
    **kwargs
) -> SystemMetrics:
    """Create system metrics snapshot."""
    metrics = SystemMetrics(
        timestamp=datetime.utcnow(),
        **kwargs
    )
    db.add(metrics)
    await db.flush()
    await db.refresh(metrics)
    return metrics


async def get_system_metrics_history(
    db: AsyncSession,
    hours: int = 24,
    interval_minutes: int = 5
) -> List[SystemMetrics]:
    """Get system metrics history."""
    since = datetime.utcnow() - timedelta(hours=hours)

    result = await db.execute(
        select(SystemMetrics)
        .where(SystemMetrics.timestamp >= since)
        .order_by(SystemMetrics.timestamp)
    )
    return list(result.scalars().all())


async def get_latest_system_metrics(
    db: AsyncSession
) -> Optional[SystemMetrics]:
    """Get the most recent system metrics."""
    result = await db.execute(
        select(SystemMetrics)
        .order_by(desc(SystemMetrics.timestamp))
        .limit(1)
    )
    return result.scalar_one_or_none()


# LLMUsageMetrics CRUD
async def create_llm_usage_metrics(
    db: AsyncSession,
    user_id: int,
    provider: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    **kwargs
) -> LLMUsageMetrics:
    """Record LLM usage."""
    usage = LLMUsageMetrics(
        user_id=user_id,
        provider=provider,
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
        **kwargs
    )
    db.add(usage)
    await db.flush()
    await db.refresh(usage)
    return usage


async def get_llm_usage_by_user(
    db: AsyncSession,
    user_id: int,
    days: int = 30
) -> List[LLMUsageMetrics]:
    """Get LLM usage for a user."""
    since = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(LLMUsageMetrics)
        .where(
            and_(
                LLMUsageMetrics.user_id == user_id,
                LLMUsageMetrics.timestamp >= since
            )
        )
        .order_by(desc(LLMUsageMetrics.timestamp))
    )
    return list(result.scalars().all())


async def get_llm_usage_summary(
    db: AsyncSession,
    user_id: Optional[int] = None,
    project_id: Optional[int] = None,
    days: int = 30
) -> Dict[str, Any]:
    """Get LLM usage summary."""
    since = datetime.utcnow() - timedelta(days=days)

    query = select(LLMUsageMetrics).where(LLMUsageMetrics.timestamp >= since)

    if user_id:
        query = query.where(LLMUsageMetrics.user_id == user_id)
    if project_id:
        query = query.where(LLMUsageMetrics.project_id == project_id)

    result = await db.execute(query)
    usage_records = list(result.scalars().all())

    if not usage_records:
        return {
            "total_calls": 0,
            "total_tokens": 0,
            "total_cost": 0,
            "by_provider": {},
            "by_model": {},
            "success_rate": 0
        }

    total_calls = len(usage_records)
    successful_calls = len([u for u in usage_records if u.success])
    total_tokens = sum(u.total_tokens for u in usage_records)
    total_cost = sum(u.estimated_cost_usd or 0 for u in usage_records)

    # Aggregate by provider
    by_provider = {}
    for usage in usage_records:
        if usage.provider not in by_provider:
            by_provider[usage.provider] = {"calls": 0, "tokens": 0, "cost": 0}
        by_provider[usage.provider]["calls"] += 1
        by_provider[usage.provider]["tokens"] += usage.total_tokens
        by_provider[usage.provider]["cost"] += usage.estimated_cost_usd or 0

    # Aggregate by model
    by_model = {}
    for usage in usage_records:
        model = f"{usage.provider}/{usage.model}"
        if model not in by_model:
            by_model[model] = {"calls": 0, "tokens": 0, "cost": 0}
        by_model[model]["calls"] += 1
        by_model[model]["tokens"] += usage.total_tokens
        by_model[model]["cost"] += usage.estimated_cost_usd or 0

    return {
        "total_calls": total_calls,
        "total_tokens": total_tokens,
        "total_cost": total_cost,
        "by_provider": by_provider,
        "by_model": by_model,
        "success_rate": successful_calls / total_calls if total_calls > 0 else 0
    }


# PerformanceAlert CRUD
async def create_performance_alert(
    db: AsyncSession,
    alert_type: str,
    severity: str,
    title: str,
    description: str,
    metric_name: str,
    metric_value: float,
    threshold_value: float,
    **kwargs
) -> PerformanceAlert:
    """Create a performance alert."""
    alert = PerformanceAlert(
        alert_type=alert_type,
        severity=severity,
        title=title,
        description=description,
        metric_name=metric_name,
        metric_value=metric_value,
        threshold_value=threshold_value,
        **kwargs
    )
    db.add(alert)
    await db.flush()
    await db.refresh(alert)
    return alert


async def get_active_alerts(
    db: AsyncSession,
    severity: Optional[str] = None
) -> List[PerformanceAlert]:
    """Get active performance alerts."""
    query = select(PerformanceAlert).where(PerformanceAlert.status == "active")

    if severity:
        query = query.where(PerformanceAlert.severity == severity)

    query = query.order_by(desc(PerformanceAlert.created_at))

    result = await db.execute(query)
    return list(result.scalars().all())


async def acknowledge_alert(
    db: AsyncSession,
    alert_id: int
) -> Optional[PerformanceAlert]:
    """Acknowledge a performance alert."""
    result = await db.execute(
        select(PerformanceAlert).where(PerformanceAlert.id == alert_id)
    )
    alert = result.scalar_one_or_none()

    if alert:
        alert.status = "acknowledged"
        alert.acknowledged_at = datetime.utcnow()
        await db.flush()
        await db.refresh(alert)

    return alert


async def resolve_alert(
    db: AsyncSession,
    alert_id: int
) -> Optional[PerformanceAlert]:
    """Resolve a performance alert."""
    result = await db.execute(
        select(PerformanceAlert).where(PerformanceAlert.id == alert_id)
    )
    alert = result.scalar_one_or_none()

    if alert:
        alert.status = "resolved"
        alert.resolved_at = datetime.utcnow()
        await db.flush()
        await db.refresh(alert)

    return alert


async def cleanup_old_metrics(
    db: AsyncSession,
    days: int = 90
) -> int:
    """Clean up old performance metrics."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Delete old workflow metrics
    workflow_result = await db.execute(
        select(WorkflowMetrics).where(WorkflowMetrics.created_at < cutoff)
    )
    old_workflows = list(workflow_result.scalars().all())

    for workflow in old_workflows:
        await db.delete(workflow)

    # Delete old system metrics
    system_result = await db.execute(
        select(SystemMetrics).where(SystemMetrics.timestamp < cutoff)
    )
    old_system = list(system_result.scalars().all())

    for metrics in old_system:
        await db.delete(metrics)

    await db.flush()

    return len(old_workflows) + len(old_system)
