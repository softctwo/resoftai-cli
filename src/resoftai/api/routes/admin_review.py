"""
Admin Review Workflow API Routes

Provides endpoints for:
- Plugin and template review/approval
- Moderation and quality control
- Admin dashboard statistics
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel, Field
from datetime import datetime

from resoftai.db import get_db
from resoftai.auth.dependencies import get_current_active_user
from resoftai.models.user import User
from resoftai.models.plugin import Plugin, PluginStatus
from resoftai.models.template import TemplateModel, TemplateStatus
from resoftai.crud import plugin as plugin_crud
from resoftai.crud import template as template_crud

router = APIRouter(prefix="/admin", tags=["admin-review"])


# =============================================================================
# Request/Response Models
# =============================================================================

class ReviewAction(BaseModel):
    """Request model for review action"""
    status: str = Field(..., regex="^(approved|rejected)$")
    feedback: Optional[str] = Field(None, description="Feedback for the author")
    is_featured: bool = Field(default=False)


class PluginReviewResponse(BaseModel):
    """Response model for plugin in review"""
    id: int
    name: str
    slug: str
    category: str
    version: str
    description: Optional[str]
    author_id: Optional[int]
    author_name: Optional[str]
    status: str
    package_url: Optional[str]
    source_url: Optional[str]
    submitted_at: str  # created_at
    license: Optional[str]

    class Config:
        from_attributes = True


class TemplateReviewResponse(BaseModel):
    """Response model for template in review"""
    id: int
    name: str
    slug: str
    category: str
    version: str
    description: Optional[str]
    author_id: Optional[int]
    author_name: Optional[str]
    status: str
    source_url: Optional[str]
    submitted_at: str  # created_at
    license: Optional[str]

    class Config:
        from_attributes = True


class AdminStatsResponse(BaseModel):
    """Response model for admin dashboard statistics"""
    pending_plugins: int
    pending_templates: int
    approved_plugins: int
    approved_templates: int
    rejected_plugins: int
    rejected_templates: int
    total_contributors: int
    total_downloads: int
    total_installs: int


# =============================================================================
# Dependency: Admin Access Check
# =============================================================================

async def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency to check if user is admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# =============================================================================
# Plugin Review Endpoints
# =============================================================================

@router.get("/plugins/pending", response_model=List[PluginReviewResponse])
async def list_pending_plugins(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    List plugins pending review
    """
    plugins = await plugin_crud.list_plugins(
        db=db,
        status=PluginStatus.SUBMITTED,
        skip=skip,
        limit=limit
    )

    return plugins


@router.get("/plugins/all-statuses", response_model=List[PluginReviewResponse])
async def list_all_plugins_for_review(
    status_filter: Optional[PluginStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    List all plugins with optional status filter (for admin dashboard)
    """
    plugins = await plugin_crud.list_plugins(
        db=db,
        status=status_filter,
        skip=skip,
        limit=limit
    )

    return plugins


@router.post("/plugins/{plugin_id}/approve", status_code=status.HTTP_200_OK)
async def approve_plugin(
    plugin_id: int,
    action: ReviewAction,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Approve a plugin

    Sets status to APPROVED and optionally features it.
    """
    plugin = await plugin_crud.get_plugin_by_id(db, plugin_id)

    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin not found"
        )

    if plugin.status != PluginStatus.SUBMITTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plugin is in '{plugin.status}' status and cannot be approved"
        )

    # Update plugin status
    await plugin_crud.update_plugin(
        db=db,
        plugin_id=plugin_id,
        status=PluginStatus.APPROVED,
        is_featured=action.is_featured,
        published_at=datetime.utcnow()
    )

    # Send notification to author
    from resoftai.services.notification_service import get_notification_service
    service = await get_notification_service(db)
    await service.notify_plugin_approved(
        user_id=plugin.author_id,
        plugin_name=plugin.name,
        plugin_id=plugin_id,
        plugin_url=f"/plugins/marketplace/{plugin_id}"
    )

    # TODO: Log admin action in audit log

    return {
        "message": f"Plugin '{plugin.name}' has been approved",
        "plugin_id": plugin_id,
        "status": "approved"
    }


@router.post("/plugins/{plugin_id}/reject", status_code=status.HTTP_200_OK)
async def reject_plugin(
    plugin_id: int,
    action: ReviewAction,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Reject a plugin

    Sets status to REJECTED and provides feedback to author.
    """
    plugin = await plugin_crud.get_plugin_by_id(db, plugin_id)

    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin not found"
        )

    if plugin.status != PluginStatus.SUBMITTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plugin is in '{plugin.status}' status and cannot be rejected"
        )

    if not action.feedback:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feedback is required when rejecting a plugin"
        )

    # Update plugin status
    await plugin_crud.update_plugin(
        db=db,
        plugin_id=plugin_id,
        status=PluginStatus.REJECTED
    )

    # Send rejection notification to author with feedback
    from resoftai.services.notification_service import get_notification_service
    service = await get_notification_service(db)
    await service.notify_plugin_rejected(
        user_id=plugin.author_id,
        plugin_name=plugin.name,
        plugin_id=plugin_id,
        feedback=action.feedback
    )

    # TODO: Log admin action in audit log

    return {
        "message": f"Plugin '{plugin.name}' has been rejected",
        "plugin_id": plugin_id,
        "status": "rejected",
        "feedback": action.feedback
    }


@router.post("/plugins/{plugin_id}/feature", status_code=status.HTTP_200_OK)
async def feature_plugin(
    plugin_id: int,
    is_featured: bool = True,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Feature or unfeature a plugin
    """
    plugin = await plugin_crud.get_plugin_by_id(db, plugin_id)

    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin not found"
        )

    await plugin_crud.update_plugin(
        db=db,
        plugin_id=plugin_id,
        is_featured=is_featured
    )

    action = "featured" if is_featured else "unfeatured"
    return {
        "message": f"Plugin '{plugin.name}' has been {action}",
        "plugin_id": plugin_id,
        "is_featured": is_featured
    }


# =============================================================================
# Template Review Endpoints
# =============================================================================

@router.get("/templates/pending", response_model=List[TemplateReviewResponse])
async def list_pending_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    List templates pending review
    """
    templates = await template_crud.list_templates(
        db=db,
        status=TemplateStatus.SUBMITTED,
        skip=skip,
        limit=limit
    )

    return templates


@router.get("/templates/all-statuses", response_model=List[TemplateReviewResponse])
async def list_all_templates_for_review(
    status_filter: Optional[TemplateStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    List all templates with optional status filter (for admin dashboard)
    """
    templates = await template_crud.list_templates(
        db=db,
        status=status_filter,
        skip=skip,
        limit=limit
    )

    return templates


@router.post("/templates/{template_id}/approve", status_code=status.HTTP_200_OK)
async def approve_template(
    template_id: int,
    action: ReviewAction,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Approve a template

    Sets status to APPROVED and optionally features it.
    """
    template = await template_crud.get_template_by_id(db, template_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    if template.status != TemplateStatus.SUBMITTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Template is in '{template.status}' status and cannot be approved"
        )

    # Update template status
    await template_crud.update_template(
        db=db,
        template_id=template_id,
        status=TemplateStatus.APPROVED,
        is_featured=action.is_featured,
        published_at=datetime.utcnow()
    )

    # Send notification to author
    from resoftai.services.notification_service import get_notification_service
    service = await get_notification_service(db)
    await service.notify_template_approved(
        user_id=template.author_id,
        template_name=template.name,
        template_id=template_id,
        template_url=f"/templates/marketplace/{template_id}"
    )

    # TODO: Log admin action in audit log

    return {
        "message": f"Template '{template.name}' has been approved",
        "template_id": template_id,
        "status": "approved"
    }


@router.post("/templates/{template_id}/reject", status_code=status.HTTP_200_OK)
async def reject_template(
    template_id: int,
    action: ReviewAction,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Reject a template

    Sets status to REJECTED and provides feedback to author.
    """
    template = await template_crud.get_template_by_id(db, template_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    if template.status != TemplateStatus.SUBMITTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Template is in '{template.status}' status and cannot be rejected"
        )

    if not action.feedback:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feedback is required when rejecting a template"
        )

    # Update template status
    await template_crud.update_template(
        db=db,
        template_id=template_id,
        status=TemplateStatus.REJECTED
    )

    # Send rejection notification to author with feedback
    from resoftai.services.notification_service import get_notification_service
    service = await get_notification_service(db)
    await service.notify_template_rejected(
        user_id=template.author_id,
        template_name=template.name,
        template_id=template_id,
        feedback=action.feedback
    )

    # TODO: Log admin action in audit log

    return {
        "message": f"Template '{template.name}' has been rejected",
        "template_id": template_id,
        "status": "rejected",
        "feedback": action.feedback
    }


@router.post("/templates/{template_id}/feature", status_code=status.HTTP_200_OK)
async def feature_template(
    template_id: int,
    is_featured: bool = True,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Feature or unfeature a template
    """
    template = await template_crud.get_template_by_id(db, template_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    await template_crud.update_template(
        db=db,
        template_id=template_id,
        is_featured=is_featured
    )

    action = "featured" if is_featured else "unfeatured"
    return {
        "message": f"Template '{template.name}' has been {action}",
        "template_id": template_id,
        "is_featured": is_featured
    }


# =============================================================================
# Admin Dashboard Statistics
# =============================================================================

@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get admin dashboard statistics
    """
    # Count plugins by status
    pending_plugins = await db.execute(
        select(func.count(Plugin.id)).where(Plugin.status == PluginStatus.SUBMITTED)
    )
    approved_plugins = await db.execute(
        select(func.count(Plugin.id)).where(Plugin.status == PluginStatus.APPROVED)
    )
    rejected_plugins = await db.execute(
        select(func.count(Plugin.id)).where(Plugin.status == PluginStatus.REJECTED)
    )

    # Count templates by status
    pending_templates = await db.execute(
        select(func.count(TemplateModel.id)).where(TemplateModel.status == TemplateStatus.SUBMITTED)
    )
    approved_templates = await db.execute(
        select(func.count(TemplateModel.id)).where(TemplateModel.status == TemplateStatus.APPROVED)
    )
    rejected_templates = await db.execute(
        select(func.count(TemplateModel.id)).where(TemplateModel.status == TemplateStatus.REJECTED)
    )

    # Count total contributors
    from resoftai.models.template import ContributorProfile
    total_contributors = await db.execute(
        select(func.count(ContributorProfile.id))
    )

    # Calculate total downloads and installs
    plugin_downloads = await db.execute(
        select(func.sum(Plugin.downloads_count))
    )
    template_downloads = await db.execute(
        select(func.sum(TemplateModel.downloads_count))
    )
    plugin_installs = await db.execute(
        select(func.sum(Plugin.installs_count))
    )
    template_installs = await db.execute(
        select(func.sum(TemplateModel.installs_count))
    )

    return AdminStatsResponse(
        pending_plugins=pending_plugins.scalar_one(),
        pending_templates=pending_templates.scalar_one(),
        approved_plugins=approved_plugins.scalar_one(),
        approved_templates=approved_templates.scalar_one(),
        rejected_plugins=rejected_plugins.scalar_one(),
        rejected_templates=rejected_templates.scalar_one(),
        total_contributors=total_contributors.scalar_one(),
        total_downloads=(plugin_downloads.scalar_one() or 0) + (template_downloads.scalar_one() or 0),
        total_installs=(plugin_installs.scalar_one() or 0) + (template_installs.scalar_one() or 0)
    )


# =============================================================================
# Content Moderation
# =============================================================================

@router.post("/plugins/{plugin_id}/deprecate", status_code=status.HTTP_200_OK)
async def deprecate_plugin(
    plugin_id: int,
    reason: str = Field(..., description="Reason for deprecation"),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Deprecate a plugin (e.g., due to security issues, policy violations)
    """
    plugin = await plugin_crud.get_plugin_by_id(db, plugin_id)

    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin not found"
        )

    await plugin_crud.update_plugin(
        db=db,
        plugin_id=plugin_id,
        status=PluginStatus.DEPRECATED
    )

    # TODO: Notify author and users
    # TODO: Log action

    return {
        "message": f"Plugin '{plugin.name}' has been deprecated",
        "plugin_id": plugin_id,
        "reason": reason
    }


@router.post("/templates/{template_id}/deprecate", status_code=status.HTTP_200_OK)
async def deprecate_template(
    template_id: int,
    reason: str = Field(..., description="Reason for deprecation"),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Deprecate a template (e.g., due to security issues, policy violations)
    """
    template = await template_crud.get_template_by_id(db, template_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    await template_crud.update_template(
        db=db,
        template_id=template_id,
        status=TemplateStatus.DEPRECATED
    )

    # TODO: Notify author and users
    # TODO: Log action

    return {
        "message": f"Template '{template.name}' has been deprecated",
        "template_id": template_id,
        "reason": reason
    }
