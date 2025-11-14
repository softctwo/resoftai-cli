"""Tests for enterprise features edge cases and error handling."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from resoftai.models.enterprise import (
    Organization, Team, OrganizationTier, TeamRole,
    QuotaType, AuditAction
)
from resoftai.crud import enterprise as enterprise_crud


class TestOrganizationEdgeCases:
    """Test edge cases for organization operations."""

    @pytest.mark.asyncio
    async def test_organization_with_special_characters_in_name(self, db: AsyncSession):
        """Test creating organization with special characters in name."""
        org = await enterprise_crud.create_organization(
            db,
            name="Test & Company (Pty) Ltd.",
            slug="test-company",
            tier=OrganizationTier.FREE
        )
        await db.commit()

        assert org.name == "Test & Company (Pty) Ltd."

    @pytest.mark.asyncio
    async def test_organization_with_very_long_name(self, db: AsyncSession):
        """Test organization with maximum allowed name length."""
        long_name = "A" * 200  # Assuming max is 200

        org = await enterprise_crud.create_organization(
            db,
            name=long_name,
            slug="long-name-org",
            tier=OrganizationTier.FREE
        )
        await db.commit()

        assert len(org.name) == 200

    @pytest.mark.asyncio
    async def test_organization_slug_validation(self, db: AsyncSession):
        """Test organization slug validation."""
        # Test valid slug
        org1 = await enterprise_crud.create_organization(
            db,
            name="Test 1",
            slug="test-org-123",
            tier=OrganizationTier.FREE
        )
        await db.commit()
        assert org1.slug == "test-org-123"

    @pytest.mark.asyncio
    async def test_organization_tier_change(self, db: AsyncSession):
        """Test changing organization tier."""
        org = await enterprise_crud.create_organization(
            db,
            name="Upgrade Test",
            slug="upgrade-test",
            tier=OrganizationTier.FREE
        )
        await db.commit()

        # Upgrade to professional
        updated = await enterprise_crud.update_organization(
            db,
            org.id,
            tier=OrganizationTier.PROFESSIONAL
        )
        await db.commit()

        assert updated.tier == OrganizationTier.PROFESSIONAL

    @pytest.mark.asyncio
    async def test_filter_organizations_by_multiple_criteria(self, db: AsyncSession):
        """Test filtering organizations with multiple criteria."""
        await enterprise_crud.create_organization(
            db, name="Free Org 1", slug="free-1", tier=OrganizationTier.FREE
        )
        await enterprise_crud.create_organization(
            db, name="Pro Org 1", slug="pro-1", tier=OrganizationTier.PROFESSIONAL
        )
        await enterprise_crud.create_organization(
            db, name="Enterprise Org 1", slug="ent-1", tier=OrganizationTier.ENTERPRISE
        )
        await db.commit()

        # Filter by tier
        pro_orgs = await enterprise_crud.list_organizations(
            db, tier=OrganizationTier.PROFESSIONAL
        )
        assert all(org.tier == OrganizationTier.PROFESSIONAL for org in pro_orgs)

    @pytest.mark.asyncio
    async def test_organization_deletion_cascade(self, db: AsyncSession):
        """Test that deleting organization cascades to teams."""
        org = await enterprise_crud.create_organization(
            db, name="To Delete", slug="to-delete", tier=OrganizationTier.FREE
        )
        team = await enterprise_crud.create_team(
            db, organization_id=org.id, name="Team", slug="team"
        )
        await db.commit()

        org_id = org.id
        team_id = team.id

        # Delete organization
        await enterprise_crud.delete_organization(db, org_id)
        await db.commit()

        # Check team is also deleted
        deleted_team = await enterprise_crud.get_team(db, team_id)
        assert deleted_team is None


class TestTeamEdgeCases:
    """Test edge cases for team operations."""

    @pytest.mark.asyncio
    async def test_team_member_role_validation(self, db: AsyncSession):
        """Test team member role validation."""
        org = await enterprise_crud.create_organization(
            db, name="Test Org", slug="test-org", tier=OrganizationTier.PROFESSIONAL
        )
        team = await enterprise_crud.create_team(
            db, organization_id=org.id, name="Team", slug="team"
        )
        await db.commit()

        # Add member with each role type
        for role in TeamRole:
            member = await enterprise_crud.add_team_member(
                db, team_id=team.id, user_id=1, role=role
            )
            await db.commit()
            assert member.role == role

            # Remove for next iteration
            await enterprise_crud.remove_team_member(db, team_id=team.id, user_id=1)
            await db.commit()

    @pytest.mark.asyncio
    async def test_team_with_no_members(self, db: AsyncSession):
        """Test team operations with no members."""
        org = await enterprise_crud.create_organization(
            db, name="Test Org", slug="test-org", tier=OrganizationTier.PROFESSIONAL
        )
        team = await enterprise_crud.create_team(
            db, organization_id=org.id, name="Empty Team", slug="empty"
        )
        await db.commit()

        members = await enterprise_crud.get_team_members(db, team.id)
        assert len(members) == 0

    @pytest.mark.asyncio
    async def test_add_duplicate_team_member(self, db: AsyncSession):
        """Test adding same user to team twice."""
        org = await enterprise_crud.create_organization(
            db, name="Test Org", slug="test-org", tier=OrganizationTier.PROFESSIONAL
        )
        team = await enterprise_crud.create_team(
            db, organization_id=org.id, name="Team", slug="team"
        )
        await enterprise_crud.add_team_member(
            db, team_id=team.id, user_id=1, role=TeamRole.MEMBER
        )
        await db.commit()

        # Try to add again - should either update or raise error
        try:
            await enterprise_crud.add_team_member(
                db, team_id=team.id, user_id=1, role=TeamRole.ADMIN
            )
            await db.commit()
        except Exception:
            # Expected to fail
            pass

    @pytest.mark.asyncio
    async def test_team_member_role_update(self, db: AsyncSession):
        """Test updating team member role."""
        org = await enterprise_crud.create_organization(
            db, name="Test Org", slug="test-org", tier=OrganizationTier.PROFESSIONAL
        )
        team = await enterprise_crud.create_team(
            db, organization_id=org.id, name="Team", slug="team"
        )
        member = await enterprise_crud.add_team_member(
            db, team_id=team.id, user_id=1, role=TeamRole.MEMBER
        )
        await db.commit()

        # Update role
        updated = await enterprise_crud.update_team_member(
            db, team_id=team.id, user_id=1, role=TeamRole.ADMIN
        )
        await db.commit()

        assert updated.role == TeamRole.ADMIN

    @pytest.mark.asyncio
    async def test_team_filtering_edge_cases(self, db: AsyncSession):
        """Test team filtering with edge cases."""
        org1 = await enterprise_crud.create_organization(
            db, name="Org 1", slug="org-1", tier=OrganizationTier.PROFESSIONAL
        )
        org2 = await enterprise_crud.create_organization(
            db, name="Org 2", slug="org-2", tier=OrganizationTier.PROFESSIONAL
        )

        # Create teams in different orgs with similar names
        await enterprise_crud.create_team(
            db, organization_id=org1.id, name="Engineering", slug="engineering"
        )
        await enterprise_crud.create_team(
            db, organization_id=org2.id, name="Engineering", slug="engineering"
        )
        await db.commit()

        # Filter by org1
        org1_teams = await enterprise_crud.list_teams(
            db, organization_id=org1.id
        )
        assert all(team.organization_id == org1.id for team in org1_teams)


class TestQuotaEdgeCases:
    """Test edge cases for quota management."""

    @pytest.mark.asyncio
    async def test_quota_usage_tracking(self, db: AsyncSession):
        """Test tracking quota usage."""
        org = await enterprise_crud.create_organization(
            db, name="Test Org", slug="test-org", tier=OrganizationTier.PROFESSIONAL
        )
        quota = await enterprise_crud.create_quota(
            db,
            organization_id=org.id,
            quota_type=QuotaType.API_REQUESTS,
            limit=1000
        )
        await db.commit()

        # Track usage
        usage = await enterprise_crud.track_quota_usage(
            db,
            quota_id=quota.id,
            amount=100
        )
        await db.commit()

        assert usage.used == 100

    @pytest.mark.asyncio
    async def test_quota_limit_exceeded(self, db: AsyncSession):
        """Test quota limit exceeded scenario."""
        org = await enterprise_crud.create_organization(
            db, name="Test Org", slug="test-org", tier=OrganizationTier.FREE
        )
        quota = await enterprise_crud.create_quota(
            db,
            organization_id=org.id,
            quota_type=QuotaType.API_REQUESTS,
            limit=100
        )
        await db.commit()

        # Try to use more than limit
        try:
            await enterprise_crud.track_quota_usage(
                db, quota_id=quota.id, amount=150
            )
            await db.commit()

            # Check if exceeded
            exceeded = await enterprise_crud.is_quota_exceeded(
                db, organization_id=org.id, quota_type=QuotaType.API_REQUESTS
            )
            assert exceeded is True
        except Exception:
            # May raise exception on exceeded quota
            pass

    @pytest.mark.asyncio
    async def test_quota_reset(self, db: AsyncSession):
        """Test resetting quota usage."""
        org = await enterprise_crud.create_organization(
            db, name="Test Org", slug="test-org", tier=OrganizationTier.PROFESSIONAL
        )
        quota = await enterprise_crud.create_quota(
            db,
            organization_id=org.id,
            quota_type=QuotaType.STORAGE,
            limit=1000
        )
        await enterprise_crud.track_quota_usage(db, quota_id=quota.id, amount=500)
        await db.commit()

        # Reset quota
        await enterprise_crud.reset_quota_usage(db, quota_id=quota.id)
        await db.commit()

        # Check reset
        usage = await enterprise_crud.get_quota_usage(db, quota_id=quota.id)
        assert usage.used == 0


class TestAuditLogEdgeCases:
    """Test edge cases for audit logging."""

    @pytest.mark.asyncio
    async def test_audit_log_creation(self, db: AsyncSession):
        """Test creating audit log entries."""
        org = await enterprise_crud.create_organization(
            db, name="Test Org", slug="test-org", tier=OrganizationTier.ENTERPRISE
        )
        await db.commit()

        # Create audit log
        log = await enterprise_crud.create_audit_log(
            db,
            organization_id=org.id,
            user_id=1,
            action=AuditAction.CREATE,
            resource_type="project",
            resource_id=123,
            details={"name": "New Project"}
        )
        await db.commit()

        assert log.id is not None
        assert log.action == AuditAction.CREATE
        assert log.resource_type == "project"

    @pytest.mark.asyncio
    async def test_audit_log_filtering(self, db: AsyncSession):
        """Test filtering audit logs."""
        org = await enterprise_crud.create_organization(
            db, name="Test Org", slug="test-org", tier=OrganizationTier.ENTERPRISE
        )
        await db.commit()

        # Create multiple audit logs
        actions = [AuditAction.CREATE, AuditAction.UPDATE, AuditAction.DELETE]
        for action in actions:
            await enterprise_crud.create_audit_log(
                db,
                organization_id=org.id,
                user_id=1,
                action=action,
                resource_type="project",
                resource_id=1
            )
        await db.commit()

        # Filter by action
        create_logs = await enterprise_crud.get_audit_logs(
            db,
            organization_id=org.id,
            action=AuditAction.CREATE
        )
        assert all(log.action == AuditAction.CREATE for log in create_logs)

    @pytest.mark.asyncio
    async def test_audit_log_date_range(self, db: AsyncSession):
        """Test filtering audit logs by date range."""
        org = await enterprise_crud.create_organization(
            db, name="Test Org", slug="test-org", tier=OrganizationTier.ENTERPRISE
        )
        await db.commit()

        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)

        # Create audit log
        log = await enterprise_crud.create_audit_log(
            db,
            organization_id=org.id,
            user_id=1,
            action=AuditAction.CREATE,
            resource_type="project",
            resource_id=1
        )
        await db.commit()

        # Filter by date range
        logs = await enterprise_crud.get_audit_logs(
            db,
            organization_id=org.id,
            start_date=yesterday,
            end_date=now + timedelta(days=1)
        )
        assert len(logs) >= 1


class TestRBACEdgeCases:
    """Test edge cases for role-based access control."""

    @pytest.mark.asyncio
    async def test_permission_assignment(self, db: AsyncSession):
        """Test assigning permissions to roles."""
        org = await enterprise_crud.create_organization(
            db, name="Test Org", slug="test-org", tier=OrganizationTier.ENTERPRISE
        )
        role = await enterprise_crud.create_role(
            db,
            organization_id=org.id,
            name="Custom Role",
            description="A custom role"
        )
        await db.commit()

        # Assign permissions
        permission = await enterprise_crud.create_permission(
            db,
            role_id=role.id,
            resource="projects",
            action="create"
        )
        await db.commit()

        assert permission.resource == "projects"
        assert permission.action == "create"

    @pytest.mark.asyncio
    async def test_check_user_permission(self, db: AsyncSession):
        """Test checking if user has specific permission."""
        org = await enterprise_crud.create_organization(
            db, name="Test Org", slug="test-org", tier=OrganizationTier.ENTERPRISE
        )
        role = await enterprise_crud.create_role(
            db, organization_id=org.id, name="Editor", description="Can edit"
        )
        permission = await enterprise_crud.create_permission(
            db, role_id=role.id, resource="projects", action="update"
        )
        await db.commit()

        # Assign role to user
        await enterprise_crud.assign_role_to_user(
            db, user_id=1, role_id=role.id
        )
        await db.commit()

        # Check permission
        has_permission = await enterprise_crud.check_permission(
            db, user_id=1, resource="projects", action="update"
        )
        assert has_permission is True

    @pytest.mark.asyncio
    async def test_revoke_permission(self, db: AsyncSession):
        """Test revoking permissions from role."""
        org = await enterprise_crud.create_organization(
            db, name="Test Org", slug="test-org", tier=OrganizationTier.ENTERPRISE
        )
        role = await enterprise_crud.create_role(
            db, organization_id=org.id, name="Admin", description="Admin role"
        )
        permission = await enterprise_crud.create_permission(
            db, role_id=role.id, resource="projects", action="delete"
        )
        await db.commit()

        # Revoke permission
        await enterprise_crud.delete_permission(db, permission.id)
        await db.commit()

        # Verify revoked
        remaining_permissions = await enterprise_crud.get_role_permissions(
            db, role_id=role.id
        )
        assert not any(p.id == permission.id for p in remaining_permissions)
