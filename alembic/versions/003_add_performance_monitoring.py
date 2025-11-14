"""Add performance monitoring and optimizations

Revision ID: 003
Revises: 002
Create Date: 2025-11-14

This migration adds all tables for:
- Performance Metrics (workflow metrics, agent performance, system metrics)
- LLM Usage Tracking
- Performance Alerts
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # =========================================================================
    # Workflow Metrics Table
    # =========================================================================
    op.create_table(
        'workflow_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('workflow_id', sa.String(length=100), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('total_duration_seconds', sa.Float(), nullable=True),
        sa.Column('stages_completed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('stages_failed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('current_stage', sa.String(length=50), nullable=True),
        sa.Column('total_tokens_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_llm_calls', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_cache_hits', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_cache_misses', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_stage_duration', sa.Float(), nullable=True),
        sa.Column('cache_hit_rate', sa.Float(), nullable=True),
        sa.Column('stage_timings', sa.JSON(), nullable=True),
        sa.Column('agent_metrics', sa.JSON(), nullable=True),
        sa.Column('error_log', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='running'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_workflow_metrics_project_id', 'workflow_metrics', ['project_id'])
    op.create_index('ix_workflow_metrics_workflow_id', 'workflow_metrics', ['workflow_id'])
    op.create_index('idx_workflow_status_time', 'workflow_metrics', ['status', 'created_at'])
    op.create_index('idx_workflow_project_status', 'workflow_metrics', ['project_id', 'status'])

    # =========================================================================
    # Agent Performance Table
    # =========================================================================
    op.create_table(
        'agent_performance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('workflow_metrics_id', sa.Integer(), nullable=False),
        sa.Column('agent_role', sa.String(length=50), nullable=False),
        sa.Column('execution_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('success_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failure_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_execution_time', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('avg_execution_time', sa.Float(), nullable=True),
        sa.Column('min_execution_time', sa.Float(), nullable=True),
        sa.Column('max_execution_time', sa.Float(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('llm_calls', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_tokens_per_call', sa.Float(), nullable=True),
        sa.Column('cache_hits', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cache_misses', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cache_hit_rate', sa.Float(), nullable=True),
        sa.Column('output_quality_score', sa.Float(), nullable=True),
        sa.Column('complexity_score', sa.Float(), nullable=True),
        sa.Column('execution_history', sa.JSON(), nullable=True),
        sa.Column('error_details', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['workflow_metrics_id'], ['workflow_metrics.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_agent_performance_workflow_metrics_id', 'agent_performance', ['workflow_metrics_id'])
    op.create_index('idx_agent_perf_role_time', 'agent_performance', ['agent_role', 'created_at'])
    op.create_index('idx_agent_perf_workflow', 'agent_performance', ['workflow_metrics_id', 'agent_role'])

    # =========================================================================
    # System Metrics Table
    # =========================================================================
    op.create_table(
        'system_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('active_workflows', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_workflows_completed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_workflows_failed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_workflow_duration', sa.Float(), nullable=True),
        sa.Column('total_llm_calls', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_tokens_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_tokens_per_call', sa.Float(), nullable=True),
        sa.Column('llm_error_rate', sa.Float(), nullable=True),
        sa.Column('cache_hits', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cache_misses', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cache_hit_rate', sa.Float(), nullable=True),
        sa.Column('cache_size_bytes', sa.Integer(), nullable=True),
        sa.Column('cpu_usage_percent', sa.Float(), nullable=True),
        sa.Column('memory_usage_mb', sa.Float(), nullable=True),
        sa.Column('disk_usage_mb', sa.Float(), nullable=True),
        sa.Column('api_requests_total', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('api_requests_success', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('api_requests_error', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('avg_response_time_ms', sa.Float(), nullable=True),
        sa.Column('websocket_connections', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('websocket_messages_sent', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('websocket_messages_received', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('active_plugins', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('plugin_executions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('metrics_detail', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_system_metrics_timestamp', 'system_metrics', ['timestamp'])

    # =========================================================================
    # LLM Usage Metrics Table
    # =========================================================================
    op.create_table(
        'llm_usage_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('prompt_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('completion_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('estimated_cost_usd', sa.Float(), nullable=True),
        sa.Column('response_time_ms', sa.Float(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('agent_role', sa.String(length=50), nullable=True),
        sa.Column('workflow_stage', sa.String(length=50), nullable=True),
        sa.Column('request_metadata', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_llm_usage_metrics_project_id', 'llm_usage_metrics', ['project_id'])
    op.create_index('ix_llm_usage_metrics_user_id', 'llm_usage_metrics', ['user_id'])
    op.create_index('ix_llm_usage_metrics_timestamp', 'llm_usage_metrics', ['timestamp'])
    op.create_index('idx_llm_usage_user_time', 'llm_usage_metrics', ['user_id', 'timestamp'])
    op.create_index('idx_llm_usage_project_time', 'llm_usage_metrics', ['project_id', 'timestamp'])
    op.create_index('idx_llm_usage_provider_model', 'llm_usage_metrics', ['provider', 'model'])

    # =========================================================================
    # Performance Alerts Table
    # =========================================================================
    op.create_table(
        'performance_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('alert_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('workflow_id', sa.String(length=100), nullable=True),
        sa.Column('agent_role', sa.String(length=50), nullable=True),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('threshold_value', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('alert_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_perf_alert_status_time', 'performance_alerts', ['status', 'created_at'])
    op.create_index('idx_perf_alert_type_severity', 'performance_alerts', ['alert_type', 'severity'])


def downgrade() -> None:
    # Drop all indexes and tables in reverse order
    op.drop_index('idx_perf_alert_type_severity', table_name='performance_alerts')
    op.drop_index('idx_perf_alert_status_time', table_name='performance_alerts')
    op.drop_table('performance_alerts')

    op.drop_index('idx_llm_usage_provider_model', table_name='llm_usage_metrics')
    op.drop_index('idx_llm_usage_project_time', table_name='llm_usage_metrics')
    op.drop_index('idx_llm_usage_user_time', table_name='llm_usage_metrics')
    op.drop_index('ix_llm_usage_metrics_timestamp', table_name='llm_usage_metrics')
    op.drop_index('ix_llm_usage_metrics_user_id', table_name='llm_usage_metrics')
    op.drop_index('ix_llm_usage_metrics_project_id', table_name='llm_usage_metrics')
    op.drop_table('llm_usage_metrics')

    op.drop_index('idx_system_metrics_timestamp', table_name='system_metrics')
    op.drop_table('system_metrics')

    op.drop_index('idx_agent_perf_workflow', table_name='agent_performance')
    op.drop_index('idx_agent_perf_role_time', table_name='agent_performance')
    op.drop_index('ix_agent_performance_workflow_metrics_id', table_name='agent_performance')
    op.drop_table('agent_performance')

    op.drop_index('idx_workflow_project_status', table_name='workflow_metrics')
    op.drop_index('idx_workflow_status_time', table_name='workflow_metrics')
    op.drop_index('ix_workflow_metrics_workflow_id', table_name='workflow_metrics')
    op.drop_index('ix_workflow_metrics_project_id', table_name='workflow_metrics')
    op.drop_table('workflow_metrics')
