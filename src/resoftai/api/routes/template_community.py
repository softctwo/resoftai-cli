"""
Template Community API Routes

Handles community-contributed templates, versions, ratings, and comments.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, validator

from resoftai.api.dependencies import get_db, get_current_user
from resoftai.models.user import User
from resoftai.models.template_community import (
    TemplateVisibility,
    TemplateStatus
)
from resoftai.crud import template_community as crud


router = APIRouter(prefix="/api/v1/community/templates", tags=["template-community"])


# ===== Pydantic Models =====

class TemplateVariableSchema(BaseModel):
    """Template variable definition."""
    name: str
    type: str  # string, integer, boolean, choice
    description: str
    required: bool = True
    default: Optional[str] = None
    choices: Optional[List[str]] = None


class TemplateFileSchema(BaseModel):
    """Template file definition."""
    path: str
    content: str
    is_template: bool = True


class TemplateCreateRequest(BaseModel):
    """Request to create a new template."""
    template_id: str = Field(..., min_length=3, max_length=100)
    name: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    category: str
    visibility: TemplateVisibility = TemplateVisibility.PUBLIC
    tags: List[str] = []
    icon_url: Optional[str] = None

    @validator('template_id')
    def validate_template_id(cls, v):
        """Validate template ID format."""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('template_id must contain only alphanumeric characters, hyphens, and underscores')
        return v.lower()


class TemplateUpdateRequest(BaseModel):
    """Request to update a template."""
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    icon_url: Optional[str] = None
    screenshot_urls: Optional[List[str]] = None
    visibility: Optional[TemplateVisibility] = None


class TemplateVersionCreateRequest(BaseModel):
    """Request to create a new template version."""
    version: str = Field(..., pattern=r'^\d+\.\d+\.\d+$')  # Semantic versioning
    version_name: Optional[str] = None
    changelog: Optional[str] = None
    variables: List[TemplateVariableSchema]
    files: List[TemplateFileSchema]
    directories: List[str]
    setup_commands: List[str] = []
    requirements: dict = {}
    dependencies: List[str] = []
    is_stable: bool = False


class RatingCreateRequest(BaseModel):
    """Request to create/update a rating."""
    rating: int = Field(..., ge=1, le=5)
    review: Optional[str] = Field(None, max_length=2000)


class CommentCreateRequest(BaseModel):
    """Request to create a comment."""
    content: str = Field(..., min_length=1, max_length=2000)
    parent_id: Optional[int] = None


class CommentUpdateRequest(BaseModel):
    """Request to update a comment."""
    content: str = Field(..., min_length=1, max_length=2000)


# ===== Response Models =====

class TemplateResponse(BaseModel):
    """Template response model."""
    id: int
    template_id: str
    name: str
    description: str
    category: str
    author_id: int
    visibility: str
    status: str
    tags: List[str]
    icon_url: Optional[str]
    screenshot_urls: List[str]
    download_count: int
    usage_count: int
    view_count: int
    average_rating: float
    rating_count: int
    created_at: str
    updated_at: str
    published_at: Optional[str]

    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    """Template list response."""
    templates: List[TemplateResponse]
    total: int
    skip: int
    limit: int


class TemplateVersionResponse(BaseModel):
    """Template version response."""
    id: int
    template_id: int
    version: str
    version_name: Optional[str]
    changelog: Optional[str]
    is_stable: bool
    is_latest: bool
    created_at: str
    created_by_id: int

    class Config:
        from_attributes = True


class TemplateVersionDetailResponse(TemplateVersionResponse):
    """Detailed template version response with content."""
    variables: List[dict]
    files: List[dict]
    directories: List[str]
    setup_commands: List[str]
    requirements: dict
    dependencies: List[str]


class RatingResponse(BaseModel):
    """Rating response model."""
    id: int
    template_id: int
    user_id: int
    rating: int
    review: Optional[str]
    helpful_count: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    """Comment response model."""
    id: int
    template_id: int
    user_id: int
    content: str
    parent_id: Optional[int]
    is_edited: bool
    is_deleted: bool
    helpful_count: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# ===== Template Endpoints =====

@router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    request: TemplateCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new template.

    - **template_id**: Unique identifier (lowercase alphanumeric with hyphens/underscores)
    - **name**: Display name
    - **description**: Detailed description
    - **category**: Template category
    - **visibility**: public, private, or organization
    - **tags**: List of tags for discovery
    """
    # Check if template_id already exists
    existing = await crud.get_template_by_template_id(db, request.template_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Template with ID '{request.template_id}' already exists"
        )

    template = await crud.create_template(
        db=db,
        author_id=current_user.id,
        **request.dict()
    )

    return template


@router.get("", response_model=TemplateListResponse)
async def list_templates(
    category: Optional[str] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    search: Optional[str] = None,
    visibility: Optional[TemplateVisibility] = None,
    status: Optional[TemplateStatus] = None,
    sort_by: str = Query("created_at", regex="^(created_at|updated_at|rating|downloads)$"),
    sort_desc: bool = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    List templates with filters.

    - **category**: Filter by category
    - **tags**: Filter by tags (comma-separated)
    - **search**: Search in name and description
    - **visibility**: Filter by visibility (requires authentication for non-public)
    - **status**: Filter by status
    - **sort_by**: Sort field (created_at, updated_at, rating, downloads)
    - **sort_desc**: Sort descending (default: true)
    """
    tag_list = tags.split(',') if tags else None
    user_id = current_user.id if current_user else None

    templates, total = await crud.list_templates(
        db=db,
        user_id=user_id,
        category=category,
        tags=tag_list,
        visibility=visibility,
        status=status,
        search=search,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_desc=sort_desc
    )

    return {
        "templates": templates,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get template by ID."""
    user_id = current_user.id if current_user else None
    template = await crud.get_template(db, template_id, user_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Increment view count
    await crud.increment_template_stats(db, template_id, "view_count")

    return template


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    request: TemplateUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update template (only by author)."""
    template = await crud.update_template(
        db=db,
        template_id=template_id,
        user_id=current_user.id,
        **request.dict(exclude_unset=True)
    )

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or you're not the author"
        )

    return template


@router.post("/{template_id}/publish", response_model=TemplateResponse)
async def publish_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Publish a template."""
    template = await crud.publish_template(db, template_id, current_user.id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or you're not the author"
        )

    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete template (only by author)."""
    success = await crud.delete_template(db, template_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or you're not the author"
        )


# ===== Version Endpoints =====

@router.post("/{template_id}/versions", response_model=TemplateVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_template_version(
    template_id: int,
    request: TemplateVersionCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new version of a template."""
    version = await crud.create_template_version(
        db=db,
        template_id=template_id,
        user_id=current_user.id,
        **request.dict()
    )

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or you're not the author"
        )

    return version


@router.get("/{template_id}/versions", response_model=List[TemplateVersionResponse])
async def list_template_versions(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """List all versions of a template."""
    versions = await crud.get_template_versions(db, template_id)
    return versions


@router.get("/{template_id}/versions/{version}", response_model=TemplateVersionDetailResponse)
async def get_template_version(
    template_id: int,
    version: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific version of a template."""
    template_version = await crud.get_template_version(db, template_id, version)

    if not template_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template version not found"
        )

    return template_version


# ===== Rating Endpoints =====

@router.post("/{template_id}/ratings", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
async def create_rating(
    template_id: int,
    request: RatingCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update a rating for a template."""
    # Verify template exists
    template = await crud.get_template(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    rating = await crud.create_or_update_rating(
        db=db,
        template_id=template_id,
        user_id=current_user.id,
        **request.dict()
    )

    return rating


@router.get("/{template_id}/ratings", response_model=dict)
async def list_ratings(
    template_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List ratings for a template."""
    ratings, total = await crud.get_template_ratings(
        db=db,
        template_id=template_id,
        skip=skip,
        limit=limit
    )

    return {
        "ratings": ratings,
        "total": total,
        "skip": skip,
        "limit": limit
    }


# ===== Comment Endpoints =====

@router.post("/{template_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    template_id: int,
    request: CommentCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a comment on a template."""
    # Verify template exists
    template = await crud.get_template(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    comment = await crud.create_comment(
        db=db,
        template_id=template_id,
        user_id=current_user.id,
        **request.dict()
    )

    return comment


@router.get("/{template_id}/comments", response_model=dict)
async def list_comments(
    template_id: int,
    parent_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List comments for a template."""
    comments, total = await crud.get_template_comments(
        db=db,
        template_id=template_id,
        parent_id=parent_id,
        skip=skip,
        limit=limit
    )

    return {
        "comments": comments,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    request: CommentUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a comment (only by author)."""
    comment = await crud.update_comment(
        db=db,
        comment_id=comment_id,
        user_id=current_user.id,
        content=request.content
    )

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you're not the author"
        )

    return comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a comment (only by author)."""
    success = await crud.delete_comment(db, comment_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you're not the author"
        )


# ===== Like/Favorite Endpoints =====

@router.post("/{template_id}/like", response_model=dict)
async def toggle_like(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle like status for a template."""
    # Verify template exists
    template = await crud.get_template(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    liked = await crud.toggle_like(db, template_id, current_user.id)

    return {
        "liked": liked,
        "message": "Template liked" if liked else "Template unliked"
    }


@router.get("/liked", response_model=TemplateListResponse)
async def list_liked_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List templates liked by the current user."""
    templates, total = await crud.get_user_liked_templates(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )

    return {
        "templates": templates,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/my-templates", response_model=TemplateListResponse)
async def list_my_templates(
    status: Optional[TemplateStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List templates created by the current user."""
    templates, total = await crud.list_templates(
        db=db,
        user_id=current_user.id,
        status=status,
        skip=skip,
        limit=limit,
        sort_by="updated_at",
        sort_desc=True
    )

    # Filter to only user's templates
    user_templates = [t for t in templates if t.author_id == current_user.id]

    return {
        "templates": user_templates,
        "total": len(user_templates),
        "skip": skip,
        "limit": limit
    }
