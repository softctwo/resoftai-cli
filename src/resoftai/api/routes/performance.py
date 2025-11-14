"""Performance monitoring API routes."""
from typing import Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from resoftai.utils.performance import (
    get_performance_report,
    performance_monitor,
    websocket_metrics
)
from resoftai.auth.dependencies import get_current_active_user
from resoftai.models.user import User

router = APIRouter(prefix="/performance", tags=["performance"])


# Response Models
class PerformanceMetricsResponse(BaseModel):
    """Performance metrics response."""
    timestamp: str
    performance_metrics: Dict[str, Any]
    websocket_metrics: Dict[str, Any]

    class Config:
        from_attributes = True


class WebSocketMetricsResponse(BaseModel):
    """WebSocket-specific metrics response."""
    active_connections: int
    total_connections: int
    total_disconnections: int
    messages_sent: int
    messages_received: int
    bytes_sent: int
    bytes_received: int
    errors: int
    reconnections: int
    avg_message_size_sent: float
    avg_message_size_received: float

    class Config:
        from_attributes = True


class TimingStatsResponse(BaseModel):
    """Timing statistics for a specific metric."""
    min: float
    max: float
    avg: float
    count: int
    total: float


@router.get("/metrics", response_model=PerformanceMetricsResponse)
async def get_metrics(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get comprehensive performance metrics.

    Returns:
        Performance report including all timing and counter metrics
    """
    return get_performance_report()


@router.get("/websocket", response_model=WebSocketMetricsResponse)
async def get_websocket_metrics(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get WebSocket-specific metrics.

    Returns:
        WebSocket connection and message statistics
    """
    return websocket_metrics.get_stats()


@router.get("/timing/{metric_name}", response_model=TimingStatsResponse)
async def get_timing_stats(
    metric_name: str,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get timing statistics for a specific metric.

    Args:
        metric_name: Name of the timing metric

    Returns:
        Statistical summary of the metric (min, max, avg, count, total)
    """
    stats = performance_monitor.get_stats(metric_name)
    if not stats:
        return {
            "min": 0,
            "max": 0,
            "avg": 0,
            "count": 0,
            "total": 0
        }
    return stats


@router.post("/reset")
async def reset_metrics(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, str]:
    """
    Reset all performance metrics.

    Requires authentication.

    Returns:
        Success message
    """
    performance_monitor.reset()
    return {"message": "Performance metrics reset successfully"}


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint (no authentication required).

    Returns:
        Status message
    """
    return {"status": "healthy"}
