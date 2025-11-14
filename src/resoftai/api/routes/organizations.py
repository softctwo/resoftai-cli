"""
Organization Management API Routes

Provides endpoints for managing organizations in enterprise mode.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from resoftai.db import get_db
from resoftai.auth.dependencies import get_current_active_user, require_admin
from resoftai.models.user import User
from resoftai.models.enterprise import OrganizationTier
from resoftai.crud import enterprise as enterprise_crud

router = APIRouter(prefix="/organizations", tags=["organizations"])


# =============================================================================
# Request/Response Models
# =============================================================================

class OrganizationCreate(BaseModel):
    """Request model for creating an organization"""
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=100, pattern="^[a-z0-9-]+$")
    tier: OrganizationTier = Field(default=OrganizationTier.FREE)
    contact_email: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None


class OrganizationUpdate(BaseModel):
    """Request model for updating an organization"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    tier: Optional[OrganizationTier] = None
    contact_email: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    sso_enabled: Optional[bool] = None


class OrganizationResponse(BaseModel):
    """Response model for organization"""
    id: int
    name: str
    slug: str
    tier: str
    is_active: bool
    contact_email: Optional[str]
    description: Optional[str]
    sso_enabled: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# =============================================================================
# Endpoints
# =============================================================================

@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new organization

    Requires admin privileges.
    """
    # Check if slug already exists
    existing = await enterprise_crud.get_organization_by_slug(db, org_data.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization with slug '{org_data.slug}' already exists"
        )

    org = await enterprise_crud.create_organization(
        db=db,
        name=org_data.name,
        slug=org_data.slug,
        tier=org_data.tier,
        contact_email=org_data.contact_email,
        description=org_data.description
    )

    # Create audit log
    await enterprise_crud.create_audit_log(
        db=db,
        action="CREATE",
        resource_type="organization",
        resource_id=org.id,
        user_id=current_user.id,
        organization_id=org.id,
        description=f"Created organization: {org.name}"
    )

    return org


@router.get("", response_model=List[OrganizationResponse])
async def list_organizations(
    tier: Optional[OrganizationTier] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List organizations

    Supports filtering by tier and active status.
    Regular users can only see organizations they belong to.
    Admins can see all organizations.
    """
    organizations = await enterprise_crud.list_organizations(
        db=db,
        tier=tier,
        is_active=is_active,
        skip=skip,
        limit=limit
    )

    # TODO: Filter by user membership for non-admins

    return organizations


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get organization by ID

    Users can only access organizations they belong to, unless they're admins.
    """
    org = await enterprise_crud.get_organization_by_id(db, org_id)

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # TODO: Check user membership

    return org


@router.get("/slug/{slug}", response_model=OrganizationResponse)
async def get_organization_by_slug(
    slug: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get organization by slug
    """
    org = await enterprise_crud.get_organization_by_slug(db, slug)

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with slug '{slug}' not found"
        )

    return org


@router.put("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: int,
    org_data: OrganizationUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update organization

    Requires admin privileges.
    """
    org = await enterprise_crud.get_organization_by_id(db, org_id)

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Get changes for audit log
    changes = {}
    for field, value in org_data.dict(exclude_unset=True).items():
        old_value = getattr(org, field)
        if old_value != value:
            changes[field] = {"old": str(old_value), "new": str(value)}

    updated_org = await enterprise_crud.update_organization(
        db=db,
        org_id=org_id,
        **org_data.dict(exclude_unset=True)
    )

    # Create audit log
    if changes:
        await enterprise_crud.create_audit_log(
            db=db,
            action="UPDATE",
            resource_type="organization",
            resource_id=org_id,
            user_id=current_user.id,
            organization_id=org_id,
            description=f"Updated organization: {org.name}",
            changes=changes
        )

    return updated_org


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    org_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete organization

    Requires admin privileges.
    This will also delete all teams, projects, and related data.
    """
    org = await enterprise_crud.get_organization_by_id(db, org_id)

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Create audit log before deletion
    await enterprise_crud.create_audit_log(
        db=db,
        action="DELETE",
        resource_type="organization",
        resource_id=org_id,
        user_id=current_user.id,
        organization_id=org_id,
        description=f"Deleted organization: {org.name}"
    )

    await enterprise_crud.delete_organization(db, org_id)
