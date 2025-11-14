"""Performance metrics models for enhanced monitoring."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from resoftai.db import Base


class WorkflowMetrics(Base):
    """Track workflow-level performance metrics."""

    __tablename__ = "workflow_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    workflow_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Timing metrics
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    total_duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Stage metrics
    stages_completed: Mapped[int] = mapped_column(Integer, default=0)
    stages_failed: Mapped[int] = mapped_column(Integer, default=0)
    current_stage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Resource usage
    total_tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    total_llm_calls: Mapped[int] = mapped_column(Integer, default=0)
    total_cache_hits: Mapped[int] = mapped_column(Integer, default=0)
    total_cache_misses: Mapped[int] = mapped_column(Integer, default=0)

    # Performance indicators
    avg_stage_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cache_hit_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Detailed metrics (JSON)
    stage_timings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    agent_metrics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_log: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(20), default="running")  # running, completed, failed, canceled

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="workflow_metrics")
    agent_performance = relationship("AgentPerformance", back_populates="workflow_metrics", cascade="all, delete-orphan")

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_workflow_status_time', 'status', 'created_at'),
        Index('idx_workflow_project_status', 'project_id', 'status'),
    )

    def __repr__(self) -> str:
        return f"<WorkflowMetrics(id={self.id}, project_id={self.project_id}, status='{self.status}')>"


class AgentPerformance(Base):
    """Track individual agent performance metrics."""

    __tablename__ = "agent_performance"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workflow_metrics_id: Mapped[int] = mapped_column(ForeignKey("workflow_metrics.id"), nullable=False, index=True)
    agent_role: Mapped[str] = mapped_column(String(50), nullable=False)

    # Execution metrics
    execution_count: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Timing metrics
    total_execution_time: Mapped[float] = mapped_column(Float, default=0.0)
    avg_execution_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    min_execution_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_execution_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # LLM usage
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    llm_calls: Mapped[int] = mapped_column(Integer, default=0)
    avg_tokens_per_call: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Cache metrics
    cache_hits: Mapped[int] = mapped_column(Integer, default=0)
    cache_misses: Mapped[int] = mapped_column(Integer, default=0)
    cache_hit_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Quality metrics
    output_quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-100
    complexity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Detailed data
    execution_history: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    error_details: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workflow_metrics = relationship("WorkflowMetrics", back_populates="agent_performance")

    # Indexes
    __table_args__ = (
        Index('idx_agent_perf_role_time', 'agent_role', 'created_at'),
        Index('idx_agent_perf_workflow', 'workflow_metrics_id', 'agent_role'),
    )

    def __repr__(self) -> str:
        return f"<AgentPerformance(id={self.id}, agent_role='{self.agent_role}', success_rate={self.success_count}/{self.execution_count})>"


class SystemMetrics(Base):
    """Track system-wide performance metrics over time."""

    __tablename__ = "system_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Workflow metrics
    active_workflows: Mapped[int] = mapped_column(Integer, default=0)
    total_workflows_completed: Mapped[int] = mapped_column(Integer, default=0)
    total_workflows_failed: Mapped[int] = mapped_column(Integer, default=0)
    avg_workflow_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # LLM metrics
    total_llm_calls: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    avg_tokens_per_call: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    llm_error_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Cache metrics
    cache_hits: Mapped[int] = mapped_column(Integer, default=0)
    cache_misses: Mapped[int] = mapped_column(Integer, default=0)
    cache_hit_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cache_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Resource metrics
    cpu_usage_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    memory_usage_mb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    disk_usage_mb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # API metrics
    api_requests_total: Mapped[int] = mapped_column(Integer, default=0)
    api_requests_success: Mapped[int] = mapped_column(Integer, default=0)
    api_requests_error: Mapped[int] = mapped_column(Integer, default=0)
    avg_response_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # WebSocket metrics
    websocket_connections: Mapped[int] = mapped_column(Integer, default=0)
    websocket_messages_sent: Mapped[int] = mapped_column(Integer, default=0)
    websocket_messages_received: Mapped[int] = mapped_column(Integer, default=0)

    # Plugin metrics
    active_plugins: Mapped[int] = mapped_column(Integer, default=0)
    plugin_executions: Mapped[int] = mapped_column(Integer, default=0)

    # Detailed metrics
    metrics_detail: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index('idx_system_metrics_timestamp', 'timestamp'),
    )

    def __repr__(self) -> str:
        return f"<SystemMetrics(id={self.id}, timestamp='{self.timestamp}', active_workflows={self.active_workflows})>"


class LLMUsageMetrics(Base):
    """Track LLM usage for billing and optimization."""

    __tablename__ = "llm_usage_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("projects.id"), nullable=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # LLM details
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)

    # Usage metrics
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)

    # Cost estimation (if available)
    estimated_cost_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Performance
    response_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    success: Mapped[bool] = mapped_column(default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Context
    agent_role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    workflow_stage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    request_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    project = relationship("Project")
    user = relationship("User")

    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_llm_usage_user_time', 'user_id', 'timestamp'),
        Index('idx_llm_usage_project_time', 'project_id', 'timestamp'),
        Index('idx_llm_usage_provider_model', 'provider', 'model'),
    )

    def __repr__(self) -> str:
        return f"<LLMUsageMetrics(id={self.id}, provider='{self.provider}', tokens={self.total_tokens})>"


class PerformanceAlert(Base):
    """Track performance alerts and anomalies."""

    __tablename__ = "performance_alerts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Alert details
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)  # slow_response, high_error_rate, etc.
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # info, warning, critical
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Context
    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("projects.id"), nullable=True)
    workflow_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    agent_role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Metrics
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    threshold_value: Mapped[float] = mapped_column(Float, nullable=False)

    # Status
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, acknowledged, resolved
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Additional data
    alert_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project")

    # Indexes
    __table_args__ = (
        Index('idx_perf_alert_status_time', 'status', 'created_at'),
        Index('idx_perf_alert_type_severity', 'alert_type', 'severity'),
    )

    def __repr__(self) -> str:
        return f"<PerformanceAlert(id={self.id}, type='{self.alert_type}', severity='{self.severity}')>"
