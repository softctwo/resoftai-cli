"""Tests for team API routes."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from resoftai.models.enterprise import Organization, Team, TeamRole, OrganizationTier
from resoftai.crud import enterprise as enterprise_crud


@pytest.mark.asyncio
async def test_create_team(client: AsyncClient, admin_token: str, db: AsyncSession):
    """Test creating a new team."""
    # Create organization first
    org = await enterprise_crud.create_organization(
        db,
        name="Test Org",
        slug="test-org",
        tier=OrganizationTier.PROFESSIONAL
    )
    await db.commit()

    response = await client.post(
        "/api/teams",
        json={
            "name": "Engineering Team",
            "slug": "engineering",
            "organization_id": org.id,
            "description": "Software engineering team"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Engineering Team"
    assert data["slug"] == "engineering"
    assert data["organization_id"] == org.id
    assert data["description"] == "Software engineering team"


@pytest.mark.asyncio
async def test_create_team_duplicate_slug_in_org(client: AsyncClient, admin_token: str, db: AsyncSession):
    """Test creating team with duplicate slug in same organization fails."""
    org = await enterprise_crud.create_organization(
        db,
        name="Test Org",
        slug="test-org",
        tier=OrganizationTier.PROFESSIONAL
    )
    team = await enterprise_crud.create_team(
        db,
        organization_id=org.id,
        name="Team 1",
        slug="team-1"
    )
    await db.commit()

    response = await client.post(
        "/api/teams",
        json={
            "name": "Team 2",
            "slug": "team-1",
            "organization_id": org.id
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_team_same_slug_different_org(client: AsyncClient, admin_token: str, db: AsyncSession):
    """Test creating team with same slug in different organizations is allowed."""
    org1 = await enterprise_crud.create_organization(db, name="Org 1", slug="org-1", tier=OrganizationTier.PROFESSIONAL)
    org2 = await enterprise_crud.create_organization(db, name="Org 2", slug="org-2", tier=OrganizationTier.PROFESSIONAL)
    await enterprise_crud.create_team(db, organization_id=org1.id, name="Team", slug="team")
    await db.commit()

    response = await client.post(
        "/api/teams",
        json={
            "name": "Team",
            "slug": "team",
            "organization_id": org2.id
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_list_teams(client: AsyncClient, admin_token: str, db: AsyncSession):
    """Test listing teams."""
    org = await enterprise_crud.create_organization(db, name="Test Org", slug="test-org", tier=OrganizationTier.PROFESSIONAL)
    await enterprise_crud.create_team(db, organization_id=org.id, name="Team 1", slug="team-1")
    await enterprise_crud.create_team(db, organization_id=org.id, name="Team 2", slug="team-2")
    await db.commit()

    response = await client.get(
        "/api/teams",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_filter_teams_by_organization(client: AsyncClient, admin_token: str, db: AsyncSession):
    """Test filtering teams by organization."""
    org1 = await enterprise_crud.create_organization(db, name="Org 1", slug="org-1", tier=OrganizationTier.PROFESSIONAL)
    org2 = await enterprise_crud.create_organization(db, name="Org 2", slug="org-2", tier=OrganizationTier.PROFESSIONAL)
    await enterprise_crud.create_team(db, organization_id=org1.id, name="Team 1", slug="team-1")
    await enterprise_crud.create_team(db, organization_id=org2.id, name="Team 2", slug="team-2")
    await db.commit()

    response = await client.get(
        f"/api/teams?organization_id={org1.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert all(team["organization_id"] == org1.id for team in data)


@pytest.mark.asyncio
async def test_get_team(client: AsyncClient, admin_token: str, db: AsyncSession):
    """Test getting a specific team."""
    org = await enterprise_crud.create_organization(db, name="Test Org", slug="test-org", tier=OrganizationTier.PROFESSIONAL)
    team = await enterprise_crud.create_team(
        db,
        organization_id=org.id,
        name="Engineering",
        slug="engineering",
        description="Engineering team"
    )
    await db.commit()

    response = await client.get(
        f"/api/teams/{team.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == team.id
    assert data["name"] == "Engineering"
    assert data["slug"] == "engineering"
    assert data["description"] == "Engineering team"


@pytest.mark.asyncio
async def test_update_team(client: AsyncClient, admin_token: str, db: AsyncSession):
    """Test updating a team."""
    org = await enterprise_crud.create_organization(db, name="Test Org", slug="test-org", tier=OrganizationTier.PROFESSIONAL)
    team = await enterprise_crud.create_team(db, organization_id=org.id, name="Old Name", slug="team")
    await db.commit()

    response = await client.put(
        f"/api/teams/{team.id}",
        json={
            "name": "New Name",
            "description": "Updated description"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_team(client: AsyncClient, admin_token: str, db: AsyncSession):
    """Test deleting a team."""
    org = await enterprise_crud.create_organization(db, name="Test Org", slug="test-org", tier=OrganizationTier.PROFESSIONAL)
    team = await enterprise_crud.create_team(db, organization_id=org.id, name="To Delete", slug="to-delete")
    await db.commit()
    team_id = team.id

    response = await client.delete(
        f"/api/teams/{team_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204

    # Verify it's deleted
    result = await enterprise_crud.get_team(db, team_id)
    assert result is None


@pytest.mark.asyncio
async def test_add_team_member(client: AsyncClient, admin_token: str, admin_user: User, db: AsyncSession):
    """Test adding a member to a team."""
    org = await enterprise_crud.create_organization(db, name="Test Org", slug="test-org", tier=OrganizationTier.PROFESSIONAL)
    team = await enterprise_crud.create_team(db, organization_id=org.id, name="Team", slug="team")
    await db.commit()

    response = await client.post(
        f"/api/teams/{team.id}/members",
        json={
            "user_id": admin_user.id,
            "role": "admin"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == admin_user.id
    assert data["team_id"] == team.id
    assert data["role"] == "admin"


@pytest.mark.asyncio
async def test_list_team_members(client: AsyncClient, admin_token: str, admin_user: User, db: AsyncSession):
    """Test listing team members."""
    org = await enterprise_crud.create_organization(db, name="Test Org", slug="test-org", tier=OrganizationTier.PROFESSIONAL)
    team = await enterprise_crud.create_team(db, organization_id=org.id, name="Team", slug="team")
    await enterprise_crud.add_team_member(db, team_id=team.id, user_id=admin_user.id, role=TeamRole.OWNER)
    await db.commit()

    response = await client.get(
        f"/api/teams/{team.id}/members",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(m["user_id"] == admin_user.id for m in data)


@pytest.mark.asyncio
async def test_update_team_member_role(client: AsyncClient, admin_token: str, admin_user: User, db: AsyncSession):
    """Test updating a team member's role."""
    org = await enterprise_crud.create_organization(db, name="Test Org", slug="test-org", tier=OrganizationTier.PROFESSIONAL)
    team = await enterprise_crud.create_team(db, organization_id=org.id, name="Team", slug="team")
    member = await enterprise_crud.add_team_member(db, team_id=team.id, user_id=admin_user.id, role=TeamRole.MEMBER)
    await db.commit()

    response = await client.put(
        f"/api/teams/{team.id}/members/{admin_user.id}",
        json={"role": "admin"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"


@pytest.mark.asyncio
async def test_remove_team_member(client: AsyncClient, admin_token: str, admin_user: User, db: AsyncSession):
    """Test removing a member from a team."""
    org = await enterprise_crud.create_organization(db, name="Test Org", slug="test-org", tier=OrganizationTier.PROFESSIONAL)
    team = await enterprise_crud.create_team(db, organization_id=org.id, name="Team", slug="team")
    await enterprise_crud.add_team_member(db, team_id=team.id, user_id=admin_user.id, role=TeamRole.MEMBER)
    await db.commit()

    response = await client.delete(
        f"/api/teams/{team.id}/members/{admin_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204

    # Verify member removed
    members = await enterprise_crud.get_team_members(db, team.id)
    assert not any(m.user_id == admin_user.id for m in members)


@pytest.mark.asyncio
async def test_team_requires_authentication(client: AsyncClient):
    """Test that all team endpoints require authentication."""
    response = await client.get("/api/teams")
    assert response.status_code == 401

    response = await client.post("/api/teams", json={"name": "Test"})
    assert response.status_code == 401

    response = await client.get("/api/teams/1")
    assert response.status_code == 401

    response = await client.put("/api/teams/1", json={"name": "Test"})
    assert response.status_code == 401

    response = await client.delete("/api/teams/1")
    assert response.status_code == 401
