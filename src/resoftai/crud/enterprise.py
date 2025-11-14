"""
CRUD operations for Enterprise Edition features

Provides database operations for:
- Organizations
- Teams
- Permissions and Roles
- Quotas and Usage
- Audit Logs
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from resoftai.models.enterprise import (
    Organization, Team, TeamMember, Permission, Role,
    RolePermission, UserRole, Quota, UsageRecord, AuditLog,
    SSOProvider, OrganizationTier, TeamRole, ResourceType, AuditAction
)


# =============================================================================
# Organization Operations
# =============================================================================

async def create_organization(
    db: AsyncSession,
    name: str,
    slug: str,
    tier: OrganizationTier = OrganizationTier.FREE,
    contact_email: Optional[str] = None,
    description: Optional[str] = None
) -> Organization:
    """Create a new organization"""
    org = Organization(
        name=name,
        slug=slug,
        tier=tier,
        contact_email=contact_email,
        description=description,
        is_active=True
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org


async def get_organization_by_id(db: AsyncSession, org_id: int) -> Optional[Organization]:
    """Get organization by ID"""
    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    return result.scalar_one_or_none()


async def get_organization_by_slug(db: AsyncSession, slug: str) -> Optional[Organization]:
    """Get organization by slug"""
    result = await db.execute(
        select(Organization).where(Organization.slug == slug)
    )
    return result.scalar_one_or_none()


async def list_organizations(
    db: AsyncSession,
    tier: Optional[OrganizationTier] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Organization]:
    """List organizations with optional filters"""
    query = select(Organization)

    if tier:
        query = query.where(Organization.tier == tier)
    if is_active is not None:
        query = query.where(Organization.is_active == is_active)

    query = query.offset(skip).limit(limit).order_by(Organization.created_at.desc())

    result = await db.execute(query)
    return list(result.scalars().all())


async def update_organization(
    db: AsyncSession,
    org_id: int,
    **kwargs
) -> Optional[Organization]:
    """Update organization"""
    org = await get_organization_by_id(db, org_id)
    if not org:
        return None

    for key, value in kwargs.items():
        if hasattr(org, key):
            setattr(org, key, value)

    org.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(org)
    return org


async def delete_organization(db: AsyncSession, org_id: int) -> bool:
    """Delete organization"""
    org = await get_organization_by_id(db, org_id)
    if not org:
        return False

    await db.delete(org)
    await db.commit()
    return True


# =============================================================================
# Team Operations
# =============================================================================

async def create_team(
    db: AsyncSession,
    organization_id: int,
    name: str,
    description: Optional[str] = None,
    is_default: bool = False
) -> Team:
    """Create a new team"""
    team = Team(
        organization_id=organization_id,
        name=name,
        description=description,
        is_default=is_default
    )
    db.add(team)
    await db.commit()
    await db.refresh(team)
    return team


async def get_team_by_id(db: AsyncSession, team_id: int) -> Optional[Team]:
    """Get team by ID"""
    result = await db.execute(
        select(Team).where(Team.id == team_id).options(selectinload(Team.members))
    )
    return result.scalar_one_or_none()


async def list_teams(
    db: AsyncSession,
    organization_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Team]:
    """List teams"""
    query = select(Team)

    if organization_id:
        query = query.where(Team.organization_id == organization_id)

    query = query.offset(skip).limit(limit).order_by(Team.created_at.desc())

    result = await db.execute(query)
    return list(result.scalars().all())


async def add_team_member(
    db: AsyncSession,
    team_id: int,
    user_id: int,
    role: TeamRole = TeamRole.MEMBER
) -> TeamMember:
    """Add member to team"""
    member = TeamMember(
        team_id=team_id,
        user_id=user_id,
        role=role
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member


async def remove_team_member(db: AsyncSession, team_id: int, user_id: int) -> bool:
    """Remove member from team"""
    result = await db.execute(
        select(TeamMember).where(
            and_(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        return False

    await db.delete(member)
    await db.commit()
    return True


async def update_team_member_role(
    db: AsyncSession,
    team_id: int,
    user_id: int,
    role: TeamRole
) -> Optional[TeamMember]:
    """Update team member role"""
    result = await db.execute(
        select(TeamMember).where(
            and_(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        return None

    member.role = role
    await db.commit()
    await db.refresh(member)
    return member


# =============================================================================
# Permission and Role Operations
# =============================================================================

async def create_permission(
    db: AsyncSession,
    code: str,
    name: str,
    resource_type: str,
    description: Optional[str] = None
) -> Permission:
    """Create a new permission"""
    permission = Permission(
        code=code,
        name=name,
        resource_type=resource_type,
        description=description
    )
    db.add(permission)
    await db.commit()
    await db.refresh(permission)
    return permission


async def create_role(
    db: AsyncSession,
    name: str,
    code: str,
    description: Optional[str] = None,
    is_system_role: bool = False,
    organization_id: Optional[int] = None
) -> Role:
    """Create a new role"""
    role = Role(
        name=name,
        code=code,
        description=description,
        is_system_role=is_system_role,
        organization_id=organization_id
    )
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


async def assign_permission_to_role(
    db: AsyncSession,
    role_id: int,
    permission_id: int
) -> RolePermission:
    """Assign permission to role"""
    role_perm = RolePermission(
        role_id=role_id,
        permission_id=permission_id
    )
    db.add(role_perm)
    await db.commit()
    await db.refresh(role_perm)
    return role_perm


async def assign_role_to_user(
    db: AsyncSession,
    user_id: int,
    role_id: int,
    organization_id: Optional[int] = None,
    team_id: Optional[int] = None
) -> UserRole:
    """Assign role to user"""
    user_role = UserRole(
        user_id=user_id,
        role_id=role_id,
        organization_id=organization_id,
        team_id=team_id
    )
    db.add(user_role)
    await db.commit()
    await db.refresh(user_role)
    return user_role


async def get_user_permissions(db: AsyncSession, user_id: int) -> List[str]:
    """Get all permission codes for a user"""
    # This is a complex query that joins UserRole -> Role -> RolePermission -> Permission
    result = await db.execute(
        select(Permission.code)
        .join(RolePermission, Permission.id == RolePermission.permission_id)
        .join(Role, RolePermission.role_id == Role.id)
        .join(UserRole, Role.id == UserRole.role_id)
        .where(UserRole.user_id == user_id)
        .distinct()
    )
    return list(result.scalars().all())


async def check_user_permission(
    db: AsyncSession,
    user_id: int,
    permission_code: str
) -> bool:
    """Check if user has a specific permission"""
    permissions = await get_user_permissions(db, user_id)
    return permission_code in permissions


# =============================================================================
# Quota Operations
# =============================================================================

async def create_quota(
    db: AsyncSession,
    organization_id: int,
    resource_type: ResourceType,
    limit_value: int,
    period: Optional[str] = None,
    warning_threshold: float = 0.8
) -> Quota:
    """Create a quota"""
    quota = Quota(
        organization_id=organization_id,
        resource_type=resource_type,
        limit_value=limit_value,
        period=period,
        warning_threshold=warning_threshold
    )
    db.add(quota)
    await db.commit()
    await db.refresh(quota)
    return quota


async def get_quota(
    db: AsyncSession,
    organization_id: int,
    resource_type: ResourceType,
    period: Optional[str] = None
) -> Optional[Quota]:
    """Get quota for organization and resource type"""
    query = select(Quota).where(
        and_(
            Quota.organization_id == organization_id,
            Quota.resource_type == resource_type
        )
    )

    if period:
        query = query.where(Quota.period == period)
    else:
        query = query.where(Quota.period.is_(None))

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def record_usage(
    db: AsyncSession,
    organization_id: int,
    resource_type: ResourceType,
    amount: int,
    user_id: Optional[int] = None,
    project_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> UsageRecord:
    """Record resource usage"""
    # Get quota to link
    quota = await get_quota(db, organization_id, resource_type)

    usage = UsageRecord(
        quota_id=quota.id if quota else None,
        organization_id=organization_id,
        resource_type=resource_type,
        amount=amount,
        user_id=user_id,
        project_id=project_id,
        metadata=metadata
    )
    db.add(usage)
    await db.commit()
    await db.refresh(usage)
    return usage


async def get_usage_stats(
    db: AsyncSession,
    organization_id: int,
    resource_type: ResourceType,
    period_start: Optional[datetime] = None,
    period_end: Optional[datetime] = None
) -> Dict[str, Any]:
    """Get usage statistics"""
    query = select(func.sum(UsageRecord.amount)).where(
        and_(
            UsageRecord.organization_id == organization_id,
            UsageRecord.resource_type == resource_type
        )
    )

    if period_start:
        query = query.where(UsageRecord.recorded_at >= period_start)
    if period_end:
        query = query.where(UsageRecord.recorded_at <= period_end)

    result = await db.execute(query)
    total_usage = result.scalar() or 0

    # Get quota
    quota = await get_quota(db, organization_id, resource_type)

    return {
        "resource_type": resource_type,
        "total_usage": total_usage,
        "limit": quota.limit_value if quota else None,
        "percentage": (total_usage / quota.limit_value * 100) if quota and quota.limit_value > 0 else 0,
        "period_start": period_start,
        "period_end": period_end
    }


async def check_quota(
    db: AsyncSession,
    organization_id: int,
    resource_type: ResourceType,
    amount: int = 1
) -> tuple[bool, Optional[str]]:
    """
    Check if organization can consume resource

    Returns:
        (can_consume, error_message)
    """
    quota = await get_quota(db, organization_id, resource_type)

    if not quota:
        # No quota means unlimited
        return True, None

    # Calculate current usage
    stats = await get_usage_stats(db, organization_id, resource_type)
    current_usage = stats["total_usage"]

    if current_usage + amount > quota.limit_value:
        return False, f"Quota exceeded for {resource_type}. Limit: {quota.limit_value}, Current: {current_usage}"

    return True, None


# =============================================================================
# Audit Log Operations
# =============================================================================

async def create_audit_log(
    db: AsyncSession,
    action: AuditAction,
    resource_type: str,
    resource_id: Optional[int] = None,
    user_id: Optional[int] = None,
    organization_id: Optional[int] = None,
    description: Optional[str] = None,
    changes: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    success: bool = True,
    error_message: Optional[str] = None
) -> AuditLog:
    """Create an audit log entry"""
    log = AuditLog(
        user_id=user_id,
        organization_id=organization_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        changes=changes,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        error_message=error_message
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


async def list_audit_logs(
    db: AsyncSession,
    organization_id: Optional[int] = None,
    user_id: Optional[int] = None,
    action: Optional[AuditAction] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
) -> List[AuditLog]:
    """List audit logs with filters"""
    query = select(AuditLog)

    if organization_id:
        query = query.where(AuditLog.organization_id == organization_id)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if action:
        query = query.where(AuditLog.action == action)
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)
    if start_date:
        query = query.where(AuditLog.created_at >= start_date)
    if end_date:
        query = query.where(AuditLog.created_at <= end_date)

    query = query.order_by(desc(AuditLog.created_at)).offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


# =============================================================================
# SSO Provider Operations
# =============================================================================

async def create_sso_provider(
    db: AsyncSession,
    organization_id: int,
    name: str,
    provider_type: str,
    config: Dict[str, Any],
    attribute_mapping: Optional[Dict[str, Any]] = None
) -> SSOProvider:
    """Create SSO provider configuration"""
    provider = SSOProvider(
        organization_id=organization_id,
        name=name,
        provider_type=provider_type,
        config=config,
        attribute_mapping=attribute_mapping,
        is_active=True
    )
    db.add(provider)
    await db.commit()
    await db.refresh(provider)
    return provider


async def get_sso_provider_by_org(
    db: AsyncSession,
    organization_id: int
) -> Optional[SSOProvider]:
    """Get active SSO provider for organization"""
    result = await db.execute(
        select(SSOProvider).where(
            and_(
                SSOProvider.organization_id == organization_id,
                SSOProvider.is_active == True
            )
        )
    )
    return result.scalar_one_or_none()
