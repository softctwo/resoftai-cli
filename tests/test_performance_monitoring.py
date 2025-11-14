"""Tests for performance monitoring functionality."""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from resoftai.models.performance_metrics import (
    WorkflowMetrics,
    AgentPerformance,
    SystemMetrics,
    LLMUsageMetrics,
    PerformanceAlert
)
from resoftai.crud.performance_metrics import (
    create_workflow_metrics,
    get_workflow_metrics,
    update_workflow_metrics,
    get_workflow_stats,
    create_agent_performance,
    update_agent_performance,
    get_agent_performance_summary,
    create_system_metrics,
    get_latest_system_metrics,
    create_llm_usage_metrics,
    get_llm_usage_summary,
    create_performance_alert,
    get_active_alerts,
    acknowledge_alert,
    resolve_alert
)


@pytest.mark.asyncio
class TestWorkflowMetricsCRUD:
    """Test workflow metrics CRUD operations."""

    async def test_create_workflow_metrics(self, db_session: AsyncSession, test_project):
        """Test creating workflow metrics."""
        metrics = await create_workflow_metrics(
            db_session,
            project_id=test_project.id,
            workflow_id="wf-001",
            total_tokens_used=1000,
            total_llm_calls=10
        )

        assert metrics.id is not None
        assert metrics.project_id == test_project.id
        assert metrics.workflow_id == "wf-001"
        assert metrics.total_tokens_used == 1000
        assert metrics.total_llm_calls == 10

    async def test_get_workflow_metrics(self, db_session: AsyncSession, test_project):
        """Test retrieving workflow metrics."""
        # Create metrics
        created = await create_workflow_metrics(
            db_session,
            project_id=test_project.id,
            workflow_id="wf-002",
            status="running"
        )
        await db_session.commit()

        # Retrieve metrics
        retrieved = await get_workflow_metrics(db_session, created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.workflow_id == "wf-002"

    async def test_update_workflow_metrics(self, db_session: AsyncSession, test_project):
        """Test updating workflow metrics."""
        # Create metrics
        metrics = await create_workflow_metrics(
            db_session,
            project_id=test_project.id,
            workflow_id="wf-003",
            status="running"
        )
        await db_session.commit()

        # Update metrics
        end_time = datetime.utcnow()
        updated = await update_workflow_metrics(
            db_session,
            metrics.id,
            status="completed",
            end_time=end_time,
            stages_completed=7
        )
        await db_session.commit()

        assert updated.status == "completed"
        assert updated.end_time == end_time
        assert updated.stages_completed == 7
        assert updated.total_duration_seconds is not None

    async def test_get_workflow_stats(self, db_session: AsyncSession, test_project):
        """Test getting workflow statistics."""
        # Create multiple workflows
        for i in range(5):
            status = "completed" if i < 3 else "running"
            await create_workflow_metrics(
                db_session,
                project_id=test_project.id,
                workflow_id=f"wf-{i}",
                status=status,
                total_tokens_used=1000 * (i + 1)
            )
        await db_session.commit()

        # Get stats
        stats = await get_workflow_stats(db_session, test_project.id, days=7)

        assert stats["total"] == 5
        assert stats["completed"] == 3
        assert stats["running"] == 2
        assert stats["total_tokens"] > 0


@pytest.mark.asyncio
class TestAgentPerformanceCRUD:
    """Test agent performance CRUD operations."""

    async def test_create_agent_performance(self, db_session: AsyncSession, test_project):
        """Test creating agent performance metrics."""
        # Create workflow metrics first
        workflow = await create_workflow_metrics(
            db_session,
            project_id=test_project.id,
            workflow_id="wf-perf-001"
        )
        await db_session.commit()

        # Create agent performance
        performance = await create_agent_performance(
            db_session,
            workflow_metrics_id=workflow.id,
            agent_role="developer",
            execution_count=5,
            success_count=4,
            tokens_used=500
        )

        assert performance.id is not None
        assert performance.agent_role == "developer"
        assert performance.execution_count == 5
        assert performance.success_count == 4

    async def test_update_agent_performance(self, db_session: AsyncSession, test_project):
        """Test updating agent performance metrics."""
        # Create workflow and performance
        workflow = await create_workflow_metrics(
            db_session,
            project_id=test_project.id,
            workflow_id="wf-perf-002"
        )
        performance = await create_agent_performance(
            db_session,
            workflow_metrics_id=workflow.id,
            agent_role="developer",
            execution_count=1,
            total_execution_time=10.0
        )
        await db_session.commit()

        # Update performance
        updated = await update_agent_performance(
            db_session,
            performance.id,
            execution_count=2,
            total_execution_time=25.0
        )
        await db_session.commit()

        assert updated.execution_count == 2
        assert updated.total_execution_time == 25.0
        assert updated.avg_execution_time == 12.5

    async def test_get_agent_performance_summary(self, db_session: AsyncSession, test_project):
        """Test getting agent performance summary."""
        # Create workflow
        workflow = await create_workflow_metrics(
            db_session,
            project_id=test_project.id,
            workflow_id="wf-summary"
        )

        # Create performances for different agents
        agents = ["developer", "architect", "tester"]
        for agent in agents:
            await create_agent_performance(
                db_session,
                workflow_metrics_id=workflow.id,
                agent_role=agent,
                execution_count=10,
                success_count=8,
                tokens_used=1000
            )
        await db_session.commit()

        # Get summary
        summary = await get_agent_performance_summary(db_session, days=7)

        assert len(summary) == 3
        assert "developer" in summary
        assert summary["developer"]["total_executions"] == 10


@pytest.mark.asyncio
class TestSystemMetricsCRUD:
    """Test system metrics CRUD operations."""

    async def test_create_system_metrics(self, db_session: AsyncSession):
        """Test creating system metrics."""
        metrics = await create_system_metrics(
            db_session,
            active_workflows=5,
            total_workflows_completed=100,
            total_tokens_used=50000,
            cache_hit_rate=0.75
        )

        assert metrics.id is not None
        assert metrics.active_workflows == 5
        assert metrics.total_workflows_completed == 100
        assert metrics.cache_hit_rate == 0.75

    async def test_get_latest_system_metrics(self, db_session: AsyncSession):
        """Test getting latest system metrics."""
        # Create multiple metrics
        for i in range(3):
            await create_system_metrics(
                db_session,
                active_workflows=i + 1
            )
        await db_session.commit()

        # Get latest
        latest = await get_latest_system_metrics(db_session)

        assert latest is not None
        assert latest.active_workflows == 3


@pytest.mark.asyncio
class TestLLMUsageMetricsCRUD:
    """Test LLM usage metrics CRUD operations."""

    async def test_create_llm_usage_metrics(self, db_session: AsyncSession, test_user, test_project):
        """Test creating LLM usage metrics."""
        usage = await create_llm_usage_metrics(
            db_session,
            user_id=test_user.id,
            provider="deepseek",
            model="deepseek-chat",
            prompt_tokens=100,
            completion_tokens=200,
            project_id=test_project.id,
            estimated_cost_usd=0.01
        )

        assert usage.id is not None
        assert usage.user_id == test_user.id
        assert usage.provider == "deepseek"
        assert usage.total_tokens == 300
        assert usage.estimated_cost_usd == 0.01

    async def test_get_llm_usage_summary(self, db_session: AsyncSession, test_user, test_project):
        """Test getting LLM usage summary."""
        # Create multiple usage records
        providers = ["deepseek", "anthropic", "deepseek"]
        for i, provider in enumerate(providers):
            await create_llm_usage_metrics(
                db_session,
                user_id=test_user.id,
                provider=provider,
                model=f"{provider}-chat",
                prompt_tokens=100 * (i + 1),
                completion_tokens=200 * (i + 1),
                project_id=test_project.id,
                estimated_cost_usd=0.01 * (i + 1)
            )
        await db_session.commit()

        # Get summary
        summary = await get_llm_usage_summary(
            db_session,
            user_id=test_user.id,
            days=30
        )

        assert summary["total_calls"] == 3
        assert summary["total_tokens"] == 900  # 300 + 600 + 900
        assert "deepseek" in summary["by_provider"]
        assert "anthropic" in summary["by_provider"]
        assert summary["by_provider"]["deepseek"]["calls"] == 2


@pytest.mark.asyncio
class TestPerformanceAlertsCRUD:
    """Test performance alerts CRUD operations."""

    async def test_create_performance_alert(self, db_session: AsyncSession, test_project):
        """Test creating performance alert."""
        alert = await create_performance_alert(
            db_session,
            alert_type="slow_response",
            severity="warning",
            title="Slow Workflow Execution",
            description="Workflow execution is slower than normal",
            metric_name="workflow_duration",
            metric_value=300.0,
            threshold_value=120.0,
            project_id=test_project.id
        )

        assert alert.id is not None
        assert alert.alert_type == "slow_response"
        assert alert.severity == "warning"
        assert alert.status == "active"

    async def test_get_active_alerts(self, db_session: AsyncSession, test_project):
        """Test getting active alerts."""
        # Create alerts with different severities
        await create_performance_alert(
            db_session,
            alert_type="test",
            severity="warning",
            title="Test Warning",
            description="Test",
            metric_name="test",
            metric_value=1.0,
            threshold_value=0.5
        )
        await create_performance_alert(
            db_session,
            alert_type="test",
            severity="critical",
            title="Test Critical",
            description="Test",
            metric_name="test",
            metric_value=2.0,
            threshold_value=0.5
        )
        await db_session.commit()

        # Get all active alerts
        alerts = await get_active_alerts(db_session)
        assert len(alerts) == 2

        # Get critical alerts only
        critical_alerts = await get_active_alerts(db_session, severity="critical")
        assert len(critical_alerts) == 1

    async def test_acknowledge_alert(self, db_session: AsyncSession):
        """Test acknowledging an alert."""
        # Create alert
        alert = await create_performance_alert(
            db_session,
            alert_type="test",
            severity="warning",
            title="Test",
            description="Test",
            metric_name="test",
            metric_value=1.0,
            threshold_value=0.5
        )
        await db_session.commit()

        # Acknowledge alert
        acknowledged = await acknowledge_alert(db_session, alert.id)
        await db_session.commit()

        assert acknowledged.status == "acknowledged"
        assert acknowledged.acknowledged_at is not None

    async def test_resolve_alert(self, db_session: AsyncSession):
        """Test resolving an alert."""
        # Create alert
        alert = await create_performance_alert(
            db_session,
            alert_type="test",
            severity="warning",
            title="Test",
            description="Test",
            metric_name="test",
            metric_value=1.0,
            threshold_value=0.5
        )
        await db_session.commit()

        # Resolve alert
        resolved = await resolve_alert(db_session, alert.id)
        await db_session.commit()

        assert resolved.status == "resolved"
        assert resolved.resolved_at is not None


@pytest.mark.asyncio
class TestPerformanceMetricsIntegration:
    """Integration tests for performance metrics."""

    async def test_complete_workflow_tracking(
        self,
        db_session: AsyncSession,
        test_project
    ):
        """Test tracking a complete workflow execution."""
        # Create workflow metrics
        workflow = await create_workflow_metrics(
            db_session,
            project_id=test_project.id,
            workflow_id="wf-integration-001",
            status="running"
        )

        # Add agent performances
        agents = ["pm", "developer", "tester"]
        for agent in agents:
            await create_agent_performance(
                db_session,
                workflow_metrics_id=workflow.id,
                agent_role=agent,
                execution_count=1,
                success_count=1,
                total_execution_time=10.0,
                tokens_used=500
            )

        # Complete workflow
        await update_workflow_metrics(
            db_session,
            workflow.id,
            status="completed",
            end_time=datetime.utcnow(),
            stages_completed=7,
            total_tokens_used=1500,
            total_llm_calls=15
        )

        await db_session.commit()

        # Verify complete tracking
        final_metrics = await get_workflow_metrics(db_session, workflow.id)
        assert final_metrics.status == "completed"
        assert len(final_metrics.agent_performance) == 3
        assert final_metrics.total_tokens_used == 1500

    async def test_performance_degradation_detection(
        self,
        db_session: AsyncSession,
        test_project
    ):
        """Test detecting performance degradation."""
        # Create workflow with slow execution
        workflow = await create_workflow_metrics(
            db_session,
            project_id=test_project.id,
            workflow_id="wf-slow",
            start_time=datetime.utcnow() - timedelta(seconds=300),
            end_time=datetime.utcnow(),
            total_duration_seconds=300.0,
            status="completed"
        )

        # Create alert for slow execution
        alert = await create_performance_alert(
            db_session,
            alert_type="slow_execution",
            severity="warning",
            title="Slow Workflow Detected",
            description="Workflow took longer than expected",
            metric_name="workflow_duration",
            metric_value=300.0,
            threshold_value=120.0,
            project_id=test_project.id,
            workflow_id="wf-slow"
        )

        await db_session.commit()

        # Verify alert was created
        alerts = await get_active_alerts(db_session, severity="warning")
        assert len(alerts) >= 1
        assert any(a.workflow_id == "wf-slow" for a in alerts)
