"""Tests for organization API routes."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from resoftai.models.user import User
from resoftai.models.enterprise import Organization, OrganizationTier
from resoftai.crud import enterprise as enterprise_crud


@pytest.mark.asyncio
async def test_create_organization(client: AsyncClient, admin_token: str):
    """Test creating a new organization."""
    response = await client.post(
        "/api/organizations",
        json={
            "name": "Test Organization",
            "slug": "test-org",
            "tier": "professional"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Organization"
    assert data["slug"] == "test-org"
    assert data["tier"] == "professional"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_organization_duplicate_slug(client: AsyncClient, admin_token: str, db: AsyncSession):
    """Test creating organization with duplicate slug fails."""
    # Create first organization
    org = await enterprise_crud.create_organization(
        db,
        name="Existing Org",
        slug="existing-org",
        tier=OrganizationTier.FREE
    )
    await db.commit()

    # Try to create another with same slug
    response = await client.post(
        "/api/organizations",
        json={
            "name": "Another Org",
            "slug": "existing-org",
            "tier": "free"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_organization_requires_admin(client: AsyncClient, user_token: str):
    """Test that non-admin users cannot create organizations."""
    response = await client.post(
        "/api/organizations",
        json={
            "name": "Test Organization",
            "slug": "test-org",
            "tier": "free"
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_organizations(client: AsyncClient, admin_token: str, db: AsyncSession):
    """Test listing organizations."""
    # Create test organizations
    await enterprise_crud.create_organization(db, name="Org 1", slug="org-1", tier=OrganizationTier.FREE)
    await enterprise_crud.create_organization(db, name="Org 2", slug="org-2", tier=OrganizationTier.PROFESSIONAL)
    await db.commit()

    response = await client.get(
        "/api/organizations",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert any(org["slug"] == "org-1" for org in data)
    assert any(org["slug"] == "org-2" for org in data)


@pytest.mark.asyncio
async def test_get_organization(client: AsyncClient, admin_token: str, db: AsyncSession):
    """Test getting a specific organization."""
    org = await enterprise_crud.create_organization(
        db,
        name="Test Organization",
        slug="test-org",
        tier=OrganizationTier.ENTERPRISE
    )
    await db.commit()

    response = await client.get(
        f"/api/organizations/{org.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == org.id
    assert data["name"] == "Test Organization"
    assert data["slug"] == "test-org"
    assert data["tier"] == "enterprise"


@pytest.mark.asyncio
async def test_get_organization_not_found(client: AsyncClient, admin_token: str):
    """Test getting non-existent organization returns 404."""
    response = await client.get(
        "/api/organizations/99999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_organization(client: AsyncClient, admin_token: str, db: AsyncSession):
    """Test updating an organization."""
    org = await enterprise_crud.create_organization(
        db,
        name="Original Name",
        slug="test-org",
        tier=OrganizationTier.FREE
    )
    await db.commit()

    response = await client.put(
        f"/api/organizations/{org.id}",
        json={
            "name": "Updated Name",
            "tier": "professional"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["tier"] == "professional"


@pytest.mark.asyncio
async def test_delete_organization(client: AsyncClient, admin_token: str, db: AsyncSession):
    """Test deleting an organization."""
    org = await enterprise_crud.create_organization(
        db,
        name="To Delete",
        slug="to-delete",
        tier=OrganizationTier.FREE
    )
    await db.commit()
    org_id = org.id

    response = await client.delete(
        f"/api/organizations/{org_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204

    # Verify it's deleted
    result = await enterprise_crud.get_organization(db, org_id)
    assert result is None


@pytest.mark.asyncio
async def test_filter_organizations_by_tier(client: AsyncClient, admin_token: str, db: AsyncSession):
    """Test filtering organizations by tier."""
    await enterprise_crud.create_organization(db, name="Free Org", slug="free-org", tier=OrganizationTier.FREE)
    await enterprise_crud.create_organization(db, name="Pro Org", slug="pro-org", tier=OrganizationTier.PROFESSIONAL)
    await db.commit()

    response = await client.get(
        "/api/organizations?tier=free",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert all(org["tier"] == "free" for org in data)


@pytest.mark.asyncio
async def test_organization_pagination(client: AsyncClient, admin_token: str, db: AsyncSession):
    """Test organization listing pagination."""
    # Create multiple organizations
    for i in range(15):
        await enterprise_crud.create_organization(
            db,
            name=f"Org {i}",
            slug=f"org-{i}",
            tier=OrganizationTier.FREE
        )
    await db.commit()

    # Test with limit
    response = await client.get(
        "/api/organizations?skip=0&limit=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10

    # Test with offset
    response = await client.get(
        "/api/organizations?skip=10&limit=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5


@pytest.mark.asyncio
async def test_organization_requires_authentication(client: AsyncClient):
    """Test that all organization endpoints require authentication."""
    # Test without token
    response = await client.get("/api/organizations")
    assert response.status_code == 401

    response = await client.post("/api/organizations", json={"name": "Test"})
    assert response.status_code == 401

    response = await client.get("/api/organizations/1")
    assert response.status_code == 401

    response = await client.put("/api/organizations/1", json={"name": "Test"})
    assert response.status_code == 401

    response = await client.delete("/api/organizations/1")
    assert response.status_code == 401
