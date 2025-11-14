"""
Enterprise Edition Models - Organizations, Teams, RBAC, Quotas, Audit Logs

This module contains all enterprise-level models for:
- Organization and Team management
- Role-Based Access Control (RBAC)
- Quota management and usage tracking
- Audit logging
- SSO/SAML configuration
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Boolean, Column, Integer, String, Text, DateTime,
    ForeignKey, JSON, Float, BigInteger, Enum as SQLEnum,
    UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
import enum

from resoftai.db.connection import Base


# Enums for type safety
class OrganizationTier(str, enum.Enum):
    """Organization subscription tiers"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class TeamRole(str, enum.Enum):
    """Team member roles"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class ResourceType(str, enum.Enum):
    """Resource types for quotas"""
    PROJECTS = "projects"
    API_CALLS = "api_calls"
    STORAGE = "storage"
    TEAM_MEMBERS = "team_members"
    LLM_TOKENS = "llm_tokens"


class AuditAction(str, enum.Enum):
    """Audit log action types"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    PERMISSION_CHANGE = "permission_change"
    EXPORT = "export"


# =============================================================================
# Organization Management
# =============================================================================

class Organization(Base):
    """
    Organization model for multi-tenant enterprise support

    An organization is the top-level entity that owns teams, projects, and users.
    It has quotas, billing information, and enterprise features.
    """
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Subscription and billing
    tier = Column(SQLEnum(OrganizationTier), default=OrganizationTier.FREE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    trial_ends_at = Column(DateTime, nullable=True)
    subscription_ends_at = Column(DateTime, nullable=True)

    # Contact and settings
    contact_email = Column(String(200), nullable=True)
    settings = Column(JSON, nullable=True, default=dict)  # Custom settings

    # SSO configuration
    sso_enabled = Column(Boolean, default=False)
    sso_provider = Column(String(50), nullable=True)  # saml, oauth2, oidc
    sso_config = Column(JSON, nullable=True)  # Provider-specific config

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    teams = relationship("Team", back_populates="organization", cascade="all, delete-orphan")
    quotas = relationship("Quota", back_populates="organization", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="organization", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', tier='{self.tier}')>"


class Team(Base):
    """
    Team model for grouping users within an organization

    Teams allow fine-grained access control and collaboration.
    Each team can have multiple members with different roles.
    """
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False)  # Default team for new members

    # Settings
    settings = Column(JSON, nullable=True, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="teams")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")

    # Unique constraint: team name must be unique within organization
    __table_args__ = (
        UniqueConstraint('organization_id', 'name', name='uq_org_team_name'),
        Index('ix_teams_org_id', 'organization_id'),
    )

    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}', org_id={self.organization_id})>"


class TeamMember(Base):
    """
    Team membership with role-based access

    Associates users with teams and defines their role within the team.
    """
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    role = Column(SQLEnum(TeamRole), default=TeamRole.MEMBER, nullable=False)

    # Timestamps
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    team = relationship("Team", back_populates="members")

    # Unique constraint: user can only be in a team once
    __table_args__ = (
        UniqueConstraint('team_id', 'user_id', name='uq_team_user'),
        Index('ix_team_members_user_id', 'user_id'),
    )

    def __repr__(self):
        return f"<TeamMember(team_id={self.team_id}, user_id={self.user_id}, role='{self.role}')>"


# =============================================================================
# Role-Based Access Control (RBAC)
# =============================================================================

class Permission(Base):
    """
    Permission model defining granular access rights

    Permissions are atomic actions that can be granted to roles.
    Examples: project.create, project.read, team.invite, etc.
    """
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)

    # Permission identifier (e.g., "project.create", "user.delete")
    code = Column(String(100), unique=True, nullable=False, index=True)

    # Human-readable name and description
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Resource type this permission applies to
    resource_type = Column(String(50), nullable=False)  # project, user, team, etc.

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    roles = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Permission(code='{self.code}', name='{self.name}')>"


class Role(Base):
    """
    Role model for RBAC

    Roles are collections of permissions that can be assigned to users.
    Roles can be organization-wide or team-specific.
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)

    # Role identifier
    name = Column(String(100), nullable=False)
    code = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Scope: global (system-wide) or organization-specific
    is_system_role = Column(Boolean, default=False)  # System roles cannot be deleted
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Role(code='{self.code}', name='{self.name}')>"


class RolePermission(Base):
    """
    Many-to-many relationship between roles and permissions
    """
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
    )


class UserRole(Base):
    """
    User role assignments

    Associates users with roles, optionally scoped to a specific team or organization.
    """
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)

    # Optional scope
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=True)

    # Timestamps
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    role = relationship("Role", back_populates="user_roles")

    # Indexes
    __table_args__ = (
        Index('ix_user_roles_user_id', 'user_id'),
        Index('ix_user_roles_org_id', 'organization_id'),
    )


# =============================================================================
# Quota Management
# =============================================================================

class Quota(Base):
    """
    Quota model for resource limits

    Defines resource limits for organizations based on their subscription tier.
    Examples: max projects, API calls per month, storage limit, etc.
    """
    __tablename__ = "quotas"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)

    # Resource type
    resource_type = Column(SQLEnum(ResourceType), nullable=False)

    # Limits
    limit_value = Column(BigInteger, nullable=False)  # Maximum allowed
    period = Column(String(20), nullable=True)  # daily, monthly, yearly, null for total

    # Soft limit warning threshold (percentage)
    warning_threshold = Column(Float, default=0.8)  # Warn at 80%

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="quotas")
    usage_records = relationship("UsageRecord", back_populates="quota", cascade="all, delete-orphan")

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('organization_id', 'resource_type', 'period', name='uq_org_resource_period'),
    )

    def __repr__(self):
        return f"<Quota(org_id={self.organization_id}, resource='{self.resource_type}', limit={self.limit_value})>"


class UsageRecord(Base):
    """
    Usage tracking for quota enforcement

    Records resource usage over time for quota monitoring and billing.
    """
    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, index=True)
    quota_id = Column(Integer, ForeignKey("quotas.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)

    # Usage details
    resource_type = Column(SQLEnum(ResourceType), nullable=False)
    amount = Column(BigInteger, nullable=False)  # Amount used

    # Reference to the entity that consumed the resource
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)

    # Metadata
    metadata = Column(JSON, nullable=True)  # Additional context (e.g., LLM model used)

    # Timestamps
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    quota = relationship("Quota", back_populates="usage_records")

    # Indexes for efficient querying
    __table_args__ = (
        Index('ix_usage_org_resource_time', 'organization_id', 'resource_type', 'recorded_at'),
    )

    def __repr__(self):
        return f"<UsageRecord(org_id={self.organization_id}, resource='{self.resource_type}', amount={self.amount})>"


# =============================================================================
# Audit Logging
# =============================================================================

class AuditLog(Base):
    """
    Audit log for compliance and security

    Tracks all important actions within the system for security auditing,
    compliance (GDPR, SOC2, etc.), and troubleshooting.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Who performed the action
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)

    # What action was performed
    action = Column(SQLEnum(AuditAction), nullable=False)
    resource_type = Column(String(50), nullable=False)  # project, user, file, etc.
    resource_id = Column(Integer, nullable=True)  # ID of the affected resource

    # Action details
    description = Column(Text, nullable=True)
    changes = Column(JSON, nullable=True)  # Before/after state for updates

    # Context
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    session_id = Column(String(100), nullable=True)

    # Result
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    organization = relationship("Organization", back_populates="audit_logs")

    # Indexes for efficient querying
    __table_args__ = (
        Index('ix_audit_user_time', 'user_id', 'created_at'),
        Index('ix_audit_org_time', 'organization_id', 'created_at'),
        Index('ix_audit_resource', 'resource_type', 'resource_id'),
    )

    def __repr__(self):
        return f"<AuditLog(action='{self.action}', resource='{self.resource_type}', user_id={self.user_id})>"


# =============================================================================
# SSO Configuration (Extended)
# =============================================================================

class SSOProvider(Base):
    """
    SSO provider configuration for enterprise authentication

    Supports SAML, OAuth2, and OpenID Connect for single sign-on.
    """
    __tablename__ = "sso_providers"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)

    # Provider details
    name = Column(String(100), nullable=False)
    provider_type = Column(String(20), nullable=False)  # saml, oauth2, oidc
    is_active = Column(Boolean, default=True)

    # Configuration (provider-specific)
    config = Column(JSON, nullable=False)  # {entity_id, sso_url, certificate, ...}

    # Attribute mapping (map SSO attributes to user fields)
    attribute_mapping = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SSOProvider(name='{self.name}', type='{self.provider_type}', org_id={self.organization_id})>"
