"""
Tests for team management
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from resoftai.crud import enterprise as enterprise_crud
from resoftai.models.enterprise import OrganizationTier, TeamRole


@pytest.mark.asyncio
async def test_create_team(db: AsyncSession):
    """Test creating a team"""
    # First create an organization
    org = await enterprise_crud.create_organization(
        db=db,
        name="Test Org",
        slug="test-org-team",
        tier=OrganizationTier.PROFESSIONAL
    )

    # Create team
    team = await enterprise_crud.create_team(
        db=db,
        organization_id=org.id,
        name="Engineering Team",
        description="Software engineers",
        is_default=False
    )

    assert team.id is not None
    assert team.name == "Engineering Team"
    assert team.organization_id == org.id
    assert team.is_default is False


@pytest.mark.asyncio
async def test_list_teams_by_organization(db: AsyncSession):
    """Test listing teams filtered by organization"""
    # Create org
    org = await enterprise_crud.create_organization(
        db=db,
        name="Multi Team Org",
        slug="multi-team-org",
        tier=OrganizationTier.ENTERPRISE
    )

    # Create multiple teams
    team1 = await enterprise_crud.create_team(
        db=db,
        organization_id=org.id,
        name="Team Alpha"
    )

    team2 = await enterprise_crud.create_team(
        db=db,
        organization_id=org.id,
        name="Team Beta"
    )

    # List teams
    teams = await enterprise_crud.list_teams(db=db, organization_id=org.id)

    assert len(teams) >= 2
    team_names = [t.name for t in teams]
    assert "Team Alpha" in team_names
    assert "Team Beta" in team_names
