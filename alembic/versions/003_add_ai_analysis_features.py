"""Add AI analysis features tables

Revision ID: 003
Revises: 002
Create Date: 2025-01-14 02:00:00.000000

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
    """Create AI analysis feature tables."""

    # Code Reviews table
    op.create_table(
        'code_reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('language', sa.String(length=50), nullable=False),
        sa.Column('code_hash', sa.String(length=64), nullable=True),
        sa.Column('files_reviewed', sa.Integer(), nullable=True, default=1),
        sa.Column('total_lines', sa.Integer(), nullable=True, default=0),
        sa.Column('quality_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('maintainability_index', sa.Float(), nullable=True, default=0.0),
        sa.Column('security_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('review_duration', sa.Float(), nullable=True, default=0.0),
        sa.Column('ai_models_used', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_code_reviews_project_id', 'code_reviews', ['project_id'])

    # Code Issues table
    op.create_table(
        'code_issues',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('review_id', sa.Integer(), nullable=False),
        sa.Column('issue_id', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('line_start', sa.Integer(), nullable=False),
        sa.Column('line_end', sa.Integer(), nullable=False),
        sa.Column('code_snippet', sa.Text(), nullable=True),
        sa.Column('suggestion', sa.Text(), nullable=True),
        sa.Column('auto_fixable', sa.Integer(), nullable=True, default=0),
        sa.Column('fix_code', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True, default=1.0),
        sa.Column('references', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['review_id'], ['code_reviews.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_code_issues_review_id', 'code_issues', ['review_id'])
    op.create_index('idx_code_issues_severity', 'code_issues', ['severity'])

    # Predictive Analyses table
    op.create_table(
        'predictive_analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('analysis_timestamp', sa.DateTime(), nullable=True, default=sa.func.now()),

        # Progress Prediction
        sa.Column('estimated_completion', sa.DateTime(), nullable=True),
        sa.Column('progress_confidence', sa.Float(), nullable=True, default=0.0),
        sa.Column('current_progress', sa.Float(), nullable=True, default=0.0),
        sa.Column('projected_velocity', sa.Float(), nullable=True, default=0.0),
        sa.Column('remaining_tasks', sa.Integer(), nullable=True, default=0),
        sa.Column('bottlenecks', sa.JSON(), nullable=True),
        sa.Column('acceleration_opportunities', sa.JSON(), nullable=True),

        # Risk Assessment
        sa.Column('risk_level', sa.String(length=20), nullable=True),
        sa.Column('risk_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('identified_risks', sa.JSON(), nullable=True),
        sa.Column('mitigation_strategies', sa.JSON(), nullable=True),
        sa.Column('risk_factors', sa.JSON(), nullable=True),

        # Effort Estimation
        sa.Column('estimated_hours', sa.Float(), nullable=True, default=0.0),
        sa.Column('estimated_days', sa.Float(), nullable=True, default=0.0),
        sa.Column('confidence_range_min', sa.Float(), nullable=True, default=0.0),
        sa.Column('confidence_range_max', sa.Float(), nullable=True, default=0.0),
        sa.Column('complexity_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('similar_projects', sa.JSON(), nullable=True),
        sa.Column('assumptions', sa.JSON(), nullable=True),

        # Quality Trend
        sa.Column('current_quality', sa.Float(), nullable=True, default=0.0),
        sa.Column('quality_trend', sa.String(length=20), nullable=True),
        sa.Column('predicted_quality', sa.Float(), nullable=True, default=0.0),
        sa.Column('quality_velocity', sa.Float(), nullable=True, default=0.0),
        sa.Column('improvement_areas', sa.JSON(), nullable=True),
        sa.Column('regression_risks', sa.JSON(), nullable=True),

        # Resource Forecast
        sa.Column('predicted_team_size', sa.Integer(), nullable=True, default=0),
        sa.Column('predicted_budget', sa.Float(), nullable=True, default=0.0),
        sa.Column('predicted_infrastructure', sa.JSON(), nullable=True),
        sa.Column('scaling_timeline', sa.JSON(), nullable=True),
        sa.Column('optimization_opportunities', sa.JSON(), nullable=True),

        # Overall
        sa.Column('key_insights', sa.JSON(), nullable=True),
        sa.Column('recommended_actions', sa.JSON(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True, default=0.0),

        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_predictive_analyses_project_id', 'predictive_analyses', ['project_id'])

    # Multi-Model Executions table
    op.create_table(
        'multi_model_executions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('strategy', sa.String(length=50), nullable=False),
        sa.Column('task_complexity', sa.String(length=20), nullable=False),

        # Results
        sa.Column('final_output', sa.Text(), nullable=True),
        sa.Column('total_tokens', sa.Integer(), nullable=True, default=0),
        sa.Column('total_cost', sa.Float(), nullable=True, default=0.0),
        sa.Column('avg_latency', sa.Float(), nullable=True, default=0.0),
        sa.Column('consensus_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('models_used', sa.Integer(), nullable=True, default=0),
        sa.Column('successful_responses', sa.Integer(), nullable=True, default=0),

        # Model Responses
        sa.Column('individual_responses', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),

        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),

        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_multi_model_executions_project_id', 'multi_model_executions', ['project_id'])
    op.create_index('idx_multi_model_executions_created_at', 'multi_model_executions', ['created_at'])


def downgrade() -> None:
    """Drop AI analysis feature tables."""
    op.drop_index('idx_multi_model_executions_created_at', table_name='multi_model_executions')
    op.drop_index('idx_multi_model_executions_project_id', table_name='multi_model_executions')
    op.drop_table('multi_model_executions')

    op.drop_index('idx_predictive_analyses_project_id', table_name='predictive_analyses')
    op.drop_table('predictive_analyses')

    op.drop_index('idx_code_issues_severity', table_name='code_issues')
    op.drop_index('idx_code_issues_review_id', table_name='code_issues')
    op.drop_table('code_issues')

    op.drop_index('idx_code_reviews_project_id', table_name='code_reviews')
    op.drop_table('code_reviews')
