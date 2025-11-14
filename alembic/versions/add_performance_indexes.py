"""Add performance indexes

Revision ID: add_performance_indexes
Revises:
Create Date: 2025-11-14

This migration adds database indexes to improve query performance
for common operations in the ResoftAI platform.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = 'add_performance_indexes'
down_revision = None  # Update this to point to the previous migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add performance indexes."""

    # Projects table indexes
    # Index for user_id lookups (get_projects_by_user)
    op.create_index(
        'idx_projects_user_id',
        'projects',
        ['user_id'],
        unique=False
    )

    # Composite index for user_id + created_at (get_projects_by_user with ordering)
    op.create_index(
        'idx_projects_user_created',
        'projects',
        ['user_id', 'created_at'],
        unique=False
    )

    # Index for status lookups (filtering by status)
    op.create_index(
        'idx_projects_status',
        'projects',
        ['status'],
        unique=False
    )

    # Composite index for user_id + status (filtered queries)
    op.create_index(
        'idx_projects_user_status',
        'projects',
        ['user_id', 'status'],
        unique=False
    )

    # Files table indexes (if exists)
    try:
        # Index for project_id lookups
        op.create_index(
            'idx_files_project_id',
            'files',
            ['project_id'],
            unique=False
        )

        # Index for path lookups
        op.create_index(
            'idx_files_path',
            'files',
            ['path'],
            unique=False
        )
    except Exception:
        pass  # Table might not exist

    # Agent activities table indexes (if exists)
    try:
        # Index for project_id lookups
        op.create_index(
            'idx_agent_activities_project_id',
            'agent_activities',
            ['project_id'],
            unique=False
        )

        # Composite index for project_id + created_at
        op.create_index(
            'idx_agent_activities_project_created',
            'agent_activities',
            ['project_id', 'created_at'],
            unique=False
        )

        # Index for agent_role lookups
        op.create_index(
            'idx_agent_activities_role',
            'agent_activities',
            ['agent_role'],
            unique=False
        )
    except Exception:
        pass  # Table might not exist

    # Users table indexes
    try:
        # Index for email lookups (login)
        op.create_index(
            'idx_users_email',
            'users',
            ['email'],
            unique=True
        )
    except Exception:
        pass  # Index might already exist


def downgrade() -> None:
    """Remove performance indexes."""

    # Projects table indexes
    op.drop_index('idx_projects_user_status', table_name='projects')
    op.drop_index('idx_projects_status', table_name='projects')
    op.drop_index('idx_projects_user_created', table_name='projects')
    op.drop_index('idx_projects_user_id', table_name='projects')

    # Files table indexes
    try:
        op.drop_index('idx_files_path', table_name='files')
        op.drop_index('idx_files_project_id', table_name='files')
    except Exception:
        pass

    # Agent activities table indexes
    try:
        op.drop_index('idx_agent_activities_role', table_name='agent_activities')
        op.drop_index('idx_agent_activities_project_created', table_name='agent_activities')
        op.drop_index('idx_agent_activities_project_id', table_name='agent_activities')
    except Exception:
        pass

    # Users table indexes
    try:
        op.drop_index('idx_users_email', table_name='users')
    except Exception:
        pass
