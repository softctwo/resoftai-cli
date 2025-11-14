"""
Notifications API Routes

Provides endpoints for managing user notifications and preferences.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from resoftai.db import get_db
from resoftai.auth.dependencies import get_current_active_user
from resoftai.models.user import User
from resoftai.services.notification_service import get_notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


# =============================================================================
# Request/Response Models
# =============================================================================

class NotificationResponse(BaseModel):
    """Response model for notification"""
    id: int
    type: str
    priority: str
    title: str
    message: str
    data: Optional[dict]
    action_url: Optional[str]
    action_text: Optional[str]
    is_read: bool
    read_at: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class NotificationPreferenceUpdate(BaseModel):
    """Request model for updating notification preferences"""
    email_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    webhook_enabled: Optional[bool] = None
    webhook_url: Optional[str] = None
    preferences: Optional[dict] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = Field(None, pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    quiet_hours_end: Optional[str] = Field(None, pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    digest_enabled: Optional[bool] = None
    digest_frequency: Optional[str] = Field(None, regex="^(daily|weekly)$")


class NotificationPreferenceResponse(BaseModel):
    """Response model for notification preferences"""
    id: int
    user_id: int
    email_enabled: bool
    in_app_enabled: bool
    webhook_enabled: bool
    webhook_url: Optional[str]
    preferences: dict
    quiet_hours_enabled: bool
    quiet_hours_start: Optional[str]
    quiet_hours_end: Optional[str]
    digest_enabled: bool
    digest_frequency: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# =============================================================================
# Notification Endpoints
# =============================================================================

@router.get("", response_model=List[NotificationResponse])
async def list_notifications(
    unread_only: bool = Query(False, description="Only return unread notifications"),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List notifications for current user
    """
    service = await get_notification_service(db)
    notifications = await service.get_user_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit
    )
    return notifications


@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get count of unread notifications
    """
    service = await get_notification_service(db)
    count = await service.get_unread_count(current_user.id)
    return {"unread_count": count}


@router.post("/{notification_id}/read", status_code=status.HTTP_200_OK)
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a notification as read
    """
    from resoftai.models.notification import Notification
    from sqlalchemy import select

    # Verify notification belongs to current user
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this notification"
        )

    service = await get_notification_service(db)
    await service.mark_as_read(notification_id)

    return {"message": "Notification marked as read"}


@router.post("/mark-all-read", status_code=status.HTTP_200_OK)
async def mark_all_as_read(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark all notifications as read for current user
    """
    service = await get_notification_service(db)
    count = await service.mark_all_as_read(current_user.id)

    return {
        "message": f"Marked {count} notifications as read",
        "count": count
    }


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a notification
    """
    from resoftai.models.notification import Notification
    from sqlalchemy import select, delete

    # Verify notification belongs to current user
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this notification"
        )

    await db.execute(
        delete(Notification).where(Notification.id == notification_id)
    )
    await db.commit()


# =============================================================================
# Notification Preference Endpoints
# =============================================================================

@router.get("/preferences", response_model=NotificationPreferenceResponse)
async def get_notification_preferences(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get notification preferences for current user
    """
    from resoftai.models.notification import NotificationPreference
    from sqlalchemy import select

    result = await db.execute(
        select(NotificationPreference).where(NotificationPreference.user_id == current_user.id)
    )
    preferences = result.scalar_one_or_none()

    if not preferences:
        # Create default preferences
        preferences = NotificationPreference(
            user_id=current_user.id,
            preferences={}
        )
        db.add(preferences)
        await db.commit()
        await db.refresh(preferences)

    return preferences


@router.put("/preferences", response_model=NotificationPreferenceResponse)
async def update_notification_preferences(
    prefs_data: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update notification preferences for current user
    """
    from resoftai.models.notification import NotificationPreference
    from sqlalchemy import select
    from datetime import datetime

    result = await db.execute(
        select(NotificationPreference).where(NotificationPreference.user_id == current_user.id)
    )
    preferences = result.scalar_one_or_none()

    if not preferences:
        # Create new preferences
        preferences = NotificationPreference(
            user_id=current_user.id,
            preferences={}
        )
        db.add(preferences)

    # Update fields
    for field, value in prefs_data.dict(exclude_unset=True).items():
        if hasattr(preferences, field):
            setattr(preferences, field, value)

    preferences.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(preferences)

    return preferences


# =============================================================================
# Test Notification Endpoint (for development)
# =============================================================================

@router.post("/test", status_code=status.HTTP_201_CREATED)
async def send_test_notification(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a test notification to current user (for testing)
    """
    from resoftai.models.notification import NotificationType, NotificationPriority

    service = await get_notification_service(db)
    notification = await service.create_notification(
        user_id=current_user.id,
        notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
        title="Test Notification",
        message="This is a test notification to verify the notification system is working.",
        priority=NotificationPriority.NORMAL,
        action_url="/notifications",
        action_text="View Notifications"
    )

    return {
        "message": "Test notification sent",
        "notification_id": notification.id
    }
