"""
Template Marketplace API Routes

Provides endpoints for:
- Template publishing and management
- Template discovery and browsing
- Template reviews and ratings
- Template version management
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from resoftai.db import get_db
from resoftai.auth.dependencies import get_current_active_user
from resoftai.models.user import User
from resoftai.models.template import TemplateCategory, TemplateStatus
from resoftai.crud import template as template_crud

router = APIRouter(prefix="/templates/marketplace", tags=["template-marketplace"])


# =============================================================================
# Request/Response Models
# =============================================================================

class TemplatePublishRequest(BaseModel):
    """Request model for publishing a template"""
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200, pattern="^[a-z0-9-]+$")
    category: TemplateCategory
    version: str = Field(..., pattern="^[0-9]+\\.[0-9]+\\.[0-9]+$")
    description: Optional[str] = None
    long_description: Optional[str] = None
    tags: Optional[List[str]] = None
    template_data: Dict[str, Any] = Field(..., description="Serialized template structure")
    package_url: Optional[str] = None
    source_url: Optional[str] = None
    documentation_url: Optional[str] = None
    license: str = "MIT"


class TemplateUpdateRequest(BaseModel):
    """Request model for updating a template"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    long_description: Optional[str] = None
    tags: Optional[List[str]] = None
    documentation_url: Optional[str] = None
    status: Optional[TemplateStatus] = None


class TemplateVersionRequest(BaseModel):
    """Request model for publishing a new version"""
    version: str = Field(..., pattern="^[0-9]+\\.[0-9]+\\.[0-9]+$")
    changelog: Optional[str] = None
    template_data: Dict[str, Any] = Field(..., description="Serialized template structure")
    package_url: Optional[str] = None


class TemplateResponse(BaseModel):
    """Response model for template"""
    id: int
    name: str
    slug: str
    category: str
    version: str
    description: Optional[str]
    author_name: Optional[str]
    is_official: bool
    is_featured: bool
    status: str
    downloads_count: int
    installs_count: int
    rating_average: float
    rating_count: int
    tags: Optional[List[str]]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class TemplateDetailResponse(TemplateResponse):
    """Detailed template response"""
    long_description: Optional[str]
    template_data: Dict[str, Any]
    package_url: Optional[str]
    source_url: Optional[str]
    documentation_url: Optional[str]
    license: Optional[str]
    icon_url: Optional[str]
    screenshots: Optional[List[str]]


class TemplateVersionResponse(BaseModel):
    """Response model for template version"""
    id: int
    template_id: int
    version: str
    changelog: Optional[str]
    is_stable: bool
    downloads_count: int
    installs_count: int
    created_at: str

    class Config:
        from_attributes = True


class TemplateReviewCreate(BaseModel):
    """Request model for creating a review"""
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None


class TemplateReviewResponse(BaseModel):
    """Response model for template review"""
    id: int
    template_id: int
    user_id: int
    rating: int
    title: Optional[str]
    content: Optional[str]
    helpful_count: int
    created_at: str

    class Config:
        from_attributes = True


# =============================================================================
# Template Marketplace Endpoints
# =============================================================================

@router.get("", response_model=List[TemplateResponse])
async def list_marketplace_templates(
    category: Optional[TemplateCategory] = Query(None),
    is_featured: Optional[bool] = Query(None),
    is_official: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    sort_by: str = Query("created_at", regex="^(created_at|downloads|installs|rating|name)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Browse template marketplace

    Supports filtering by category, tags, search, and sorting.
    Public endpoint - no authentication required.
    """
    templates = await template_crud.list_templates(
        db=db,
        category=category,
        status=TemplateStatus.APPROVED,  # Only show approved templates
        is_featured=is_featured,
        is_official=is_official,
        search=search,
        tags=tags,
        sort_by=sort_by,
        skip=skip,
        limit=limit
    )

    return templates


@router.get("/search", response_model=List[TemplateResponse])
async def search_templates(
    q: str = Query(..., min_length=2),
    category: Optional[TemplateCategory] = Query(None),
    tags: Optional[List[str]] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Search templates in marketplace

    Full-text search across name, description, and tags.
    """
    templates = await template_crud.search_templates(
        db=db,
        query_text=q,
        category=category,
        tags=tags,
        limit=limit
    )

    return templates


@router.get("/trending", response_model=List[TemplateResponse])
async def get_trending_templates(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Get trending templates based on recent activity
    """
    templates = await template_crud.get_trending_templates(
        db=db,
        days=days,
        limit=limit
    )

    return templates


@router.get("/recommended", response_model=List[TemplateResponse])
async def get_recommended_templates(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized template recommendations

    Based on user's usage history and preferences.
    """
    templates = await template_crud.get_recommended_templates(
        db=db,
        user_id=current_user.id,
        limit=limit
    )

    return templates


@router.get("/{template_id}", response_model=TemplateDetailResponse)
async def get_marketplace_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a template
    """
    template = await template_crud.get_template_by_id(db, template_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    return template


# =============================================================================
# Template Publishing Endpoints
# =============================================================================

@router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def publish_template(
    template_data: TemplatePublishRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Publish a new template to the marketplace

    Template will be in 'submitted' status and requires approval.
    """
    # Check if slug already exists
    existing = await template_crud.get_template_by_slug(db, template_data.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Template with slug '{template_data.slug}' already exists"
        )

    # Validate template data structure
    if not _validate_template_data(template_data.template_data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid template data structure"
        )

    template = await template_crud.create_template(
        db=db,
        name=template_data.name,
        slug=template_data.slug,
        category=template_data.category,
        version=template_data.version,
        template_data=template_data.template_data,
        author_id=current_user.id,
        author_name=current_user.username,
        description=template_data.description,
        long_description=template_data.long_description,
        tags=template_data.tags,
        package_url=template_data.package_url,
        source_url=template_data.source_url,
        documentation_url=template_data.documentation_url,
        license=template_data.license,
        status=TemplateStatus.SUBMITTED
    )

    # Update contributor profile statistics
    await template_crud.update_contributor_stats(db, current_user.id)

    return template


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template_data: TemplateUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update template information

    Only the template author can update their templates.
    """
    template = await template_crud.get_template_by_id(db, template_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Check ownership
    if template.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this template"
        )

    updated_template = await template_crud.update_template(
        db=db,
        template_id=template_id,
        **template_data.dict(exclude_unset=True)
    )

    return updated_template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete (deprecate) a template

    Only the template author or admin can delete templates.
    """
    template = await template_crud.get_template_by_id(db, template_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Check ownership
    if template.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this template"
        )

    await template_crud.delete_template(db, template_id)


# =============================================================================
# Template Version Endpoints
# =============================================================================

@router.post("/{template_id}/versions", response_model=TemplateVersionResponse, status_code=status.HTTP_201_CREATED)
async def publish_template_version(
    template_id: int,
    version_data: TemplateVersionRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Publish a new version of a template

    Only the template author can publish new versions.
    """
    template = await template_crud.get_template_by_id(db, template_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Check ownership
    if template.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to publish versions for this template"
        )

    # Validate template data
    if not _validate_template_data(version_data.template_data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid template data structure"
        )

    # Check if version already exists
    existing_version = await template_crud.get_template_version(
        db, template_id, version_data.version
    )
    if existing_version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Version {version_data.version} already exists"
        )

    # Create new version
    version = await template_crud.create_template_version(
        db=db,
        template_id=template_id,
        version=version_data.version,
        template_data=version_data.template_data,
        changelog=version_data.changelog,
        package_url=version_data.package_url
    )

    # Update template's current version
    await template_crud.update_template(
        db=db,
        template_id=template_id,
        version=version_data.version,
        template_data=version_data.template_data
    )

    return version


@router.get("/{template_id}/versions", response_model=List[TemplateVersionResponse])
async def list_template_versions(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    List all versions for a template
    """
    template = await template_crud.get_template_by_id(db, template_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    versions = await template_crud.get_template_versions(db, template_id)
    return versions


# =============================================================================
# Template Usage Tracking
# =============================================================================

@router.post("/{template_id}/track-usage", status_code=status.HTTP_201_CREATED)
async def track_template_usage(
    template_id: int,
    project_id: Optional[int] = None,
    variables_used: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Track template usage/installation

    Called after successfully applying a template.
    """
    template = await template_crud.get_template_by_id(db, template_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    await template_crud.track_template_usage(
        db=db,
        template_id=template_id,
        user_id=current_user.id,
        installed_version=template.version,
        project_id=project_id,
        variables_used=variables_used
    )

    return {"message": "Template usage tracked successfully"}


@router.get("/my/installations", response_model=List[Dict[str, Any]])
async def list_my_template_installations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List current user's template installations
    """
    installations = await template_crud.list_template_installations(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )

    return installations


# =============================================================================
# Template Review Endpoints
# =============================================================================

@router.post("/{template_id}/reviews", response_model=TemplateReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_template_review(
    template_id: int,
    review_data: TemplateReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a review for a template

    Users can only review templates they have used.
    """
    template = await template_crud.get_template_by_id(db, template_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Check if user has used the template
    installations = await template_crud.list_template_installations(
        db=db,
        user_id=current_user.id,
        template_id=template_id,
        limit=1
    )

    if not installations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must use the template before reviewing it"
        )

    # Check if user has already reviewed
    existing_review = await template_crud.get_user_template_review(
        db=db,
        template_id=template_id,
        user_id=current_user.id
    )

    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this template"
        )

    review = await template_crud.create_template_review(
        db=db,
        template_id=template_id,
        user_id=current_user.id,
        rating=review_data.rating,
        title=review_data.title,
        content=review_data.content
    )

    return review


@router.get("/{template_id}/reviews", response_model=List[TemplateReviewResponse])
async def list_template_reviews(
    template_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    List reviews for a template
    """
    reviews = await template_crud.list_template_reviews(
        db=db,
        template_id=template_id,
        skip=skip,
        limit=limit
    )

    return reviews


# =============================================================================
# Helper Functions
# =============================================================================

def _validate_template_data(template_data: Dict[str, Any]) -> bool:
    """
    Validate template data structure

    Required fields:
    - variables: list of variable definitions
    - files: list of file definitions
    - directories: list of directory paths
    """
    required_keys = ["variables", "files", "directories"]

    for key in required_keys:
        if key not in template_data:
            return False

    # Validate variables structure
    if not isinstance(template_data["variables"], list):
        return False

    # Validate files structure
    if not isinstance(template_data["files"], list):
        return False

    # Validate directories structure
    if not isinstance(template_data["directories"], list):
        return False

    return True
