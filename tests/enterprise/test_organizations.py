"""
Tests for organization management
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from resoftai.crud import enterprise as enterprise_crud
from resoftai.models.enterprise import OrganizationTier


@pytest.mark.asyncio
async def test_create_organization(db: AsyncSession):
    """Test creating an organization"""
    org = await enterprise_crud.create_organization(
        db=db,
        name="Test Organization",
        slug="test-org",
        tier=OrganizationTier.FREE,
        contact_email="test@example.com"
    )

    assert org.id is not None
    assert org.name == "Test Organization"
    assert org.slug == "test-org"
    assert org.tier == OrganizationTier.FREE
    assert org.is_active is True


@pytest.mark.asyncio
async def test_get_organization_by_slug(db: AsyncSession):
    """Test retrieving organization by slug"""
    # Create org
    org = await enterprise_crud.create_organization(
        db=db,
        name="Test Org 2",
        slug="test-org-2",
        tier=OrganizationTier.STARTER
    )

    # Retrieve by slug
    retrieved = await enterprise_crud.get_organization_by_slug(db, "test-org-2")

    assert retrieved is not None
    assert retrieved.id == org.id
    assert retrieved.name == "Test Org 2"


@pytest.mark.asyncio
async def test_update_organization(db: AsyncSession):
    """Test updating organization"""
    # Create org
    org = await enterprise_crud.create_organization(
        db=db,
        name="Original Name",
        slug="update-test",
        tier=OrganizationTier.FREE
    )

    # Update
    updated = await enterprise_crud.update_organization(
        db=db,
        org_id=org.id,
        name="Updated Name",
        tier=OrganizationTier.PROFESSIONAL
    )

    assert updated.name == "Updated Name"
    assert updated.tier == OrganizationTier.PROFESSIONAL


@pytest.mark.asyncio
async def test_delete_organization(db: AsyncSession):
    """Test deleting organization"""
    # Create org
    org = await enterprise_crud.create_organization(
        db=db,
        name="Delete Me",
        slug="delete-test",
        tier=OrganizationTier.FREE
    )

    # Delete
    success = await enterprise_crud.delete_organization(db, org.id)
    assert success is True

    # Verify deleted
    retrieved = await enterprise_crud.get_organization_by_id(db, org.id)
    assert retrieved is None
