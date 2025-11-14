"""
Contributors API Routes

Provides endpoints for:
- Contributor profiles
- Contributor statistics
- Leaderboards
- Badges and achievements
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from resoftai.db import get_db
from resoftai.auth.dependencies import get_current_active_user
from resoftai.models.user import User
from resoftai.crud import template as template_crud

router = APIRouter(prefix="/contributors", tags=["contributors"])


# =============================================================================
# Request/Response Models
# =============================================================================

class ContributorProfileCreate(BaseModel):
    """Request model for creating contributor profile"""
    display_name: str = Field(..., min_length=1, max_length=200)
    bio: Optional[str] = None
    website: Optional[str] = None
    github_url: Optional[str] = None
    twitter_url: Optional[str] = None


class ContributorProfileUpdate(BaseModel):
    """Request model for updating contributor profile"""
    display_name: Optional[str] = Field(None, min_length=1, max_length=200)
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    website: Optional[str] = None
    github_url: Optional[str] = None
    twitter_url: Optional[str] = None


class ContributorProfileResponse(BaseModel):
    """Response model for contributor profile"""
    id: int
    user_id: int
    display_name: str
    bio: Optional[str]
    avatar_url: Optional[str]
    website: Optional[str]
    github_url: Optional[str]
    twitter_url: Optional[str]
    plugins_count: int
    templates_count: int
    total_downloads: int
    total_installs: int
    average_rating: float
    badges: List[str]
    is_verified: bool
    is_featured: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ContributorStatsResponse(BaseModel):
    """Response model for contributor statistics"""
    plugins_count: int
    templates_count: int
    total_downloads: int
    total_installs: int
    average_rating: float
    badges_earned: int
    rank: Optional[int] = None


class BadgeResponse(BaseModel):
    """Response model for badge"""
    id: int
    code: str
    name: str
    description: Optional[str]
    icon_url: Optional[str]
    color: Optional[str]
    tier: Optional[str]

    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    """Response model for leaderboard entry"""
    rank: int
    user_id: int
    display_name: str
    avatar_url: Optional[str]
    plugins_count: int
    templates_count: int
    total_downloads: int
    total_installs: int
    average_rating: float
    badges: List[str]
    is_verified: bool


# =============================================================================
# Contributor Profile Endpoints
# =============================================================================

@router.get("", response_model=List[ContributorProfileResponse])
async def list_contributors(
    is_verified: Optional[bool] = Query(None),
    is_featured: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    List all contributors

    Public endpoint - no authentication required.
    """
    from resoftai.models.template import ContributorProfile
    from sqlalchemy import select, desc

    query = select(ContributorProfile)

    if is_verified is not None:
        query = query.where(ContributorProfile.is_verified == is_verified)
    if is_featured is not None:
        query = query.where(ContributorProfile.is_featured == is_featured)

    query = query.order_by(desc(ContributorProfile.total_downloads)).offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_contributor_leaderboard(
    sort_by: str = Query("total_downloads", regex="^(total_downloads|total_installs|average_rating|contributions)$"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get contributor leaderboard

    Sort options:
    - total_downloads: Most downloaded contributions
    - total_installs: Most installed contributions
    - average_rating: Highest rated contributors
    - contributions: Most prolific contributors (plugins + templates)
    """
    profiles = await template_crud.get_contributor_leaderboard(
        db=db,
        sort_by=sort_by,
        limit=limit
    )

    # Add rank to each entry
    leaderboard = []
    for rank, profile in enumerate(profiles, start=1):
        leaderboard.append(
            LeaderboardEntry(
                rank=rank,
                user_id=profile.user_id,
                display_name=profile.display_name,
                avatar_url=profile.avatar_url,
                plugins_count=profile.plugins_count,
                templates_count=profile.templates_count,
                total_downloads=profile.total_downloads,
                total_installs=profile.total_installs,
                average_rating=profile.average_rating,
                badges=profile.badges or [],
                is_verified=profile.is_verified
            )
        )

    return leaderboard


@router.get("/me", response_model=ContributorProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's contributor profile
    """
    profile = await template_crud.get_contributor_profile(db, current_user.id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contributor profile not found. Create one first."
        )

    return profile


@router.post("/me", response_model=ContributorProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_my_profile(
    profile_data: ContributorProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create contributor profile for current user
    """
    # Check if profile already exists
    existing = await template_crud.get_contributor_profile(db, current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contributor profile already exists"
        )

    profile = await template_crud.create_contributor_profile(
        db=db,
        user_id=current_user.id,
        display_name=profile_data.display_name,
        bio=profile_data.bio,
        website=profile_data.website,
        github_url=profile_data.github_url,
        twitter_url=profile_data.twitter_url
    )

    return profile


@router.put("/me", response_model=ContributorProfileResponse)
async def update_my_profile(
    profile_data: ContributorProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user's contributor profile
    """
    profile = await template_crud.update_contributor_profile(
        db=db,
        user_id=current_user.id,
        **profile_data.dict(exclude_unset=True)
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contributor profile not found. Create one first."
        )

    return profile


@router.get("/me/stats", response_model=ContributorStatsResponse)
async def get_my_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's contributor statistics
    """
    # Update stats first
    await template_crud.update_contributor_stats(db, current_user.id)

    profile = await template_crud.get_contributor_profile(db, current_user.id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contributor profile not found"
        )

    # Get rank (optional, could be expensive for large datasets)
    # For now, we'll skip rank calculation
    rank = None

    return ContributorStatsResponse(
        plugins_count=profile.plugins_count,
        templates_count=profile.templates_count,
        total_downloads=profile.total_downloads,
        total_installs=profile.total_installs,
        average_rating=profile.average_rating,
        badges_earned=len(profile.badges or []),
        rank=rank
    )


@router.get("/{user_id}", response_model=ContributorProfileResponse)
async def get_contributor_profile(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get contributor profile by user ID
    """
    profile = await template_crud.get_contributor_profile(db, user_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contributor profile not found"
        )

    return profile


# =============================================================================
# Badge Endpoints
# =============================================================================

@router.get("/badges/available", response_model=List[BadgeResponse])
async def list_available_badges(
    db: AsyncSession = Depends(get_db)
):
    """
    List all available badges
    """
    badges = await template_crud.list_badges(db)
    return badges


@router.get("/badges/my", response_model=List[BadgeResponse])
async def get_my_badges(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's earned badges
    """
    profile = await template_crud.get_contributor_profile(db, current_user.id)

    if not profile or not profile.badges:
        return []

    # Get badge details
    badge_list = []
    for badge_code in profile.badges:
        badge = await template_crud.get_badge_by_code(db, badge_code)
        if badge:
            badge_list.append(badge)

    return badge_list


# =============================================================================
# Admin Endpoints (Badge Management)
# =============================================================================

@router.post("/admin/badges", response_model=BadgeResponse, status_code=status.HTTP_201_CREATED)
async def create_badge(
    code: str = Field(..., min_length=1, max_length=100),
    name: str = Field(..., min_length=1, max_length=200),
    description: Optional[str] = None,
    requirements: dict = Field(..., description="Badge requirements (JSON)"),
    icon_url: Optional[str] = None,
    color: Optional[str] = None,
    tier: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new badge (admin only)
    """
    # Check admin permission
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # Check if badge code already exists
    existing = await template_crud.get_badge_by_code(db, code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Badge with code '{code}' already exists"
        )

    badge = await template_crud.create_badge(
        db=db,
        code=code,
        name=name,
        requirements=requirements,
        description=description,
        icon_url=icon_url,
        color=color,
        tier=tier
    )

    return badge


@router.post("/admin/{user_id}/award-badge", status_code=status.HTTP_200_OK)
async def award_badge_to_user(
    user_id: int,
    badge_code: str = Field(..., description="Badge code to award"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Award a badge to a contributor (admin only)
    """
    # Check admin permission
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # Verify badge exists
    badge = await template_crud.get_badge_by_code(db, badge_code)
    if not badge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Badge '{badge_code}' not found"
        )

    # Award badge
    success = await template_crud.award_badge(db, user_id, badge_code)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to award badge (user may already have it or profile doesn't exist)"
        )

    return {"message": f"Badge '{badge_code}' awarded successfully"}
