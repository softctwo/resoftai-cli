"""Add enterprise features and plugin system

Revision ID: 002
Revises: 001
Create Date: 2024-11-14

This migration adds all tables for:
- Enterprise Edition (organizations, teams, RBAC, quotas, audit logs)
- Plugin System (plugins, installations, reviews, collections)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # =========================================================================
    # Enterprise Edition Tables
    # =========================================================================

    # Organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tier', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('trial_ends_at', sa.DateTime(), nullable=True),
        sa.Column('subscription_ends_at', sa.DateTime(), nullable=True),
        sa.Column('contact_email', sa.String(length=200), nullable=True),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('sso_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sso_provider', sa.String(length=50), nullable=True),
        sa.Column('sso_config', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_organizations_slug', 'organizations', ['slug'], unique=True)
    op.create_index('ix_organizations_id', 'organizations', ['id'])

    # Teams table
    op.create_table(
        'teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'name', name='uq_org_team_name')
    )
    op.create_index('ix_teams_id', 'teams', ['id'])
    op.create_index('ix_teams_org_id', 'teams', ['organization_id'])

    # Team members table
    op.create_table(
        'team_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('joined_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id', 'user_id', name='uq_team_user')
    )
    op.create_index('ix_team_members_id', 'team_members', ['id'])
    op.create_index('ix_team_members_user_id', 'team_members', ['user_id'])

    # Permissions table
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_permissions_id', 'permissions', ['id'])
    op.create_index('ix_permissions_code', 'permissions', ['code'], unique=True)

    # Roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_system_role', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_roles_id', 'roles', ['id'])
    op.create_index('ix_roles_code', 'roles', ['code'], unique=True)

    # Role permissions table
    op.create_table(
        'role_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('role_id', 'permission_id', name='uq_role_permission')
    )

    # User roles table
    op.create_table(
        'user_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('assigned_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_roles_user_id', 'user_roles', ['user_id'])
    op.create_index('ix_user_roles_org_id', 'user_roles', ['organization_id'])

    # Quotas table
    op.create_table(
        'quotas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('limit_value', sa.BigInteger(), nullable=False),
        sa.Column('period', sa.String(length=20), nullable=True),
        sa.Column('warning_threshold', sa.Float(), nullable=False, server_default='0.8'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'resource_type', 'period', name='uq_org_resource_period')
    )

    # Usage records table
    op.create_table(
        'usage_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('quota_id', sa.Integer(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['quota_id'], ['quotas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_usage_org_resource_time', 'usage_records',
                    ['organization_id', 'resource_type', 'recorded_at'])

    # Audit logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('changes', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_user_time', 'audit_logs', ['user_id', 'created_at'])
    op.create_index('ix_audit_org_time', 'audit_logs', ['organization_id', 'created_at'])
    op.create_index('ix_audit_resource', 'audit_logs', ['resource_type', 'resource_id'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])

    # SSO providers table
    op.create_table(
        'sso_providers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('provider_type', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('config', sa.JSON(), nullable=False),
        sa.Column('attribute_mapping', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # =========================================================================
    # Plugin System Tables
    # =========================================================================

    # Plugins table
    op.create_table(
        'plugins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('long_description', sa.Text(), nullable=True),
        sa.Column('author_id', sa.Integer(), nullable=True),
        sa.Column('author_name', sa.String(length=200), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('min_platform_version', sa.String(length=50), nullable=True),
        sa.Column('max_platform_version', sa.String(length=50), nullable=True),
        sa.Column('package_url', sa.String(length=500), nullable=True),
        sa.Column('package_checksum', sa.String(length=128), nullable=True),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_official', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_free', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('license', sa.String(length=100), nullable=True),
        sa.Column('downloads_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('installs_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rating_average', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('rating_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('documentation_url', sa.String(length=500), nullable=True),
        sa.Column('support_url', sa.String(length=500), nullable=True),
        sa.Column('homepage_url', sa.String(length=500), nullable=True),
        sa.Column('icon_url', sa.String(length=500), nullable=True),
        sa.Column('screenshots', sa.JSON(), nullable=True),
        sa.Column('config_schema', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.text('now()')),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_plugins_id', 'plugins', ['id'])
    op.create_index('ix_plugins_slug', 'plugins', ['slug'], unique=True)
    op.create_index('ix_plugins_name', 'plugins', ['name'])
    op.create_index('ix_plugins_category', 'plugins', ['category'])
    op.create_index('ix_plugins_status', 'plugins', ['status'])

    # Plugin versions table
    op.create_table(
        'plugin_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plugin_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('changelog', sa.Text(), nullable=True),
        sa.Column('package_url', sa.String(length=500), nullable=False),
        sa.Column('package_checksum', sa.String(length=128), nullable=False),
        sa.Column('min_platform_version', sa.String(length=50), nullable=True),
        sa.Column('max_platform_version', sa.String(length=50), nullable=True),
        sa.Column('is_stable', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_deprecated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('downloads_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['plugin_id'], ['plugins.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('plugin_id', 'version', name='uq_plugin_version')
    )

    # Plugin installations table
    op.create_table(
        'plugin_installations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plugin_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('installed_version', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('installed_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.text('now()')),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['plugin_id'], ['plugins.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('plugin_id', 'organization_id', 'user_id', name='uq_plugin_installation')
    )
    op.create_index('ix_installations_org_id', 'plugin_installations', ['organization_id'])
    op.create_index('ix_installations_user_id', 'plugin_installations', ['user_id'])

    # Plugin reviews table
    op.create_table(
        'plugin_reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plugin_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('helpful_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_flagged', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['plugin_id'], ['plugins.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('plugin_id', 'user_id', name='uq_plugin_user_review')
    )

    # Plugin comments table
    op.create_table(
        'plugin_comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plugin_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('upvotes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('downvotes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_flagged', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['plugin_id'], ['plugins.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['plugin_comments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Plugin collections table
    op.create_table(
        'plugin_collections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('followers_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('views_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_plugin_collections_slug', 'plugin_collections', ['slug'], unique=True)

    # Plugin collection items table
    op.create_table(
        'plugin_collection_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('collection_id', sa.Integer(), nullable=False),
        sa.Column('plugin_id', sa.Integer(), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('added_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['collection_id'], ['plugin_collections.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['plugin_id'], ['plugins.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('collection_id', 'plugin_id', name='uq_collection_plugin')
    )


def downgrade() -> None:
    # Drop plugin system tables
    op.drop_table('plugin_collection_items')
    op.drop_table('plugin_collections')
    op.drop_table('plugin_comments')
    op.drop_table('plugin_reviews')
    op.drop_table('plugin_installations')
    op.drop_table('plugin_versions')
    op.drop_table('plugins')

    # Drop enterprise tables
    op.drop_table('sso_providers')
    op.drop_table('audit_logs')
    op.drop_table('usage_records')
    op.drop_table('quotas')
    op.drop_table('user_roles')
    op.drop_table('role_permissions')
    op.drop_table('roles')
    op.drop_table('permissions')
    op.drop_table('team_members')
    op.drop_table('teams')
    op.drop_table('organizations')
