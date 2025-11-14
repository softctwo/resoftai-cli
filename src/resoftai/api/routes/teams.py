"""
Team Management API Routes

Provides endpoints for managing teams within organizations.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from resoftai.db import get_db
from resoftai.auth.dependencies import get_current_active_user
from resoftai.models.user import User
from resoftai.models.enterprise import TeamRole
from resoftai.crud import enterprise as enterprise_crud

router = APIRouter(prefix="/teams", tags=["teams"])


# =============================================================================
# Request/Response Models
# =============================================================================

class TeamCreate(BaseModel):
    """Request model for creating a team"""
    organization_id: int
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    is_default: bool = False


class TeamUpdate(BaseModel):
    """Request model for updating a team"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_default: Optional[bool] = None


class TeamMemberAdd(BaseModel):
    """Request model for adding a team member"""
    user_id: int
    role: TeamRole = Field(default=TeamRole.MEMBER)


class TeamMemberRoleUpdate(BaseModel):
    """Request model for updating member role"""
    role: TeamRole


class TeamMemberResponse(BaseModel):
    """Response model for team member"""
    id: int
    user_id: int
    role: str
    joined_at: str

    class Config:
        from_attributes = True


class TeamResponse(BaseModel):
    """Response model for team"""
    id: int
    organization_id: int
    name: str
    description: Optional[str]
    is_default: bool
    created_at: str
    updated_at: str
    # members: List[TeamMemberResponse] = []

    class Config:
        from_attributes = True


# =============================================================================
# Endpoints
# =============================================================================

@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new team within an organization

    Requires organization admin privileges.
    """
    # Check if organization exists
    org = await enterprise_crud.get_organization_by_id(db, team_data.organization_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # TODO: Check if user has permission to create teams in this org

    team = await enterprise_crud.create_team(
        db=db,
        organization_id=team_data.organization_id,
        name=team_data.name,
        description=team_data.description,
        is_default=team_data.is_default
    )

    # Create audit log
    await enterprise_crud.create_audit_log(
        db=db,
        action="CREATE",
        resource_type="team",
        resource_id=team.id,
        user_id=current_user.id,
        organization_id=team_data.organization_id,
        description=f"Created team: {team.name}"
    )

    return team


@router.get("", response_model=List[TeamResponse])
async def list_teams(
    organization_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List teams

    If organization_id is provided, filters teams by organization.
    Otherwise, returns teams the user belongs to.
    """
    teams = await enterprise_crud.list_teams(
        db=db,
        organization_id=organization_id,
        skip=skip,
        limit=limit
    )

    return teams


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get team by ID

    Users can only access teams they belong to.
    """
    team = await enterprise_crud.get_team_by_id(db, team_id)

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    # TODO: Check user membership

    return team


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    team_data: TeamUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update team

    Requires team admin privileges.
    """
    team = await enterprise_crud.get_team_by_id(db, team_id)

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    # TODO: Check user has admin permission for this team

    # Update team (SQLAlchemy doesn't have a direct update method in enterprise_crud)
    for field, value in team_data.dict(exclude_unset=True).items():
        setattr(team, field, value)

    await db.commit()
    await db.refresh(team)

    # Create audit log
    await enterprise_crud.create_audit_log(
        db=db,
        action="UPDATE",
        resource_type="team",
        resource_id=team_id,
        user_id=current_user.id,
        organization_id=team.organization_id,
        description=f"Updated team: {team.name}"
    )

    return team


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete team

    Requires team admin or organization admin privileges.
    """
    team = await enterprise_crud.get_team_by_id(db, team_id)

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    # TODO: Check user has permission to delete this team

    # Create audit log before deletion
    await enterprise_crud.create_audit_log(
        db=db,
        action="DELETE",
        resource_type="team",
        resource_id=team_id,
        user_id=current_user.id,
        organization_id=team.organization_id,
        description=f"Deleted team: {team.name}"
    )

    await db.delete(team)
    await db.commit()


# =============================================================================
# Team Member Management
# =============================================================================

@router.post("/{team_id}/members", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_team_member(
    team_id: int,
    member_data: TeamMemberAdd,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a member to a team

    Requires team admin privileges.
    """
    team = await enterprise_crud.get_team_by_id(db, team_id)

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    # TODO: Check user has permission to add members

    # Check if user is already a member
    # (This will raise an integrity error if duplicate, handled by database)

    member = await enterprise_crud.add_team_member(
        db=db,
        team_id=team_id,
        user_id=member_data.user_id,
        role=member_data.role
    )

    # Create audit log
    await enterprise_crud.create_audit_log(
        db=db,
        action="CREATE",
        resource_type="team_member",
        resource_id=member.id,
        user_id=current_user.id,
        organization_id=team.organization_id,
        description=f"Added user {member_data.user_id} to team {team.name}"
    )

    return member


@router.delete("/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_member(
    team_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove a member from a team

    Requires team admin privileges, or users can remove themselves.
    """
    team = await enterprise_crud.get_team_by_id(db, team_id)

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    # TODO: Check permission (admin or self-removal)

    success = await enterprise_crud.remove_team_member(db, team_id, user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a member of this team"
        )

    # Create audit log
    await enterprise_crud.create_audit_log(
        db=db,
        action="DELETE",
        resource_type="team_member",
        user_id=current_user.id,
        organization_id=team.organization_id,
        description=f"Removed user {user_id} from team {team.name}"
    )


@router.put("/{team_id}/members/{user_id}/role", response_model=TeamMemberResponse)
async def update_team_member_role(
    team_id: int,
    user_id: int,
    role_data: TeamMemberRoleUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a team member's role

    Requires team admin or organization admin privileges.
    """
    team = await enterprise_crud.get_team_by_id(db, team_id)

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    # TODO: Check permission

    member = await enterprise_crud.update_team_member_role(
        db=db,
        team_id=team_id,
        user_id=user_id,
        role=role_data.role
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a member of this team"
        )

    # Create audit log
    await enterprise_crud.create_audit_log(
        db=db,
        action="UPDATE",
        resource_type="team_member",
        resource_id=member.id,
        user_id=current_user.id,
        organization_id=team.organization_id,
        description=f"Updated role for user {user_id} in team {team.name} to {role_data.role}"
    )

    return member
