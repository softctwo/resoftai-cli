"""
Notification Service

Handles creation and delivery of notifications across multiple channels.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from resoftai.models.notification import (
    Notification, NotificationPreference, EmailTemplate,
    NotificationType, NotificationChannel, NotificationPriority
)
from resoftai.models.user import User

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Central notification service for creating and delivering notifications
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(
        self,
        user_id: int,
        notification_type: NotificationType,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        action_url: Optional[str] = None,
        action_text: Optional[str] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        channels: Optional[List[NotificationChannel]] = None,
        expires_in_days: Optional[int] = None
    ) -> Notification:
        """
        Create and deliver a notification

        Args:
            user_id: Recipient user ID
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            data: Additional context data
            action_url: URL for action button
            action_text: Text for action button
            priority: Notification priority
            channels: Delivery channels (defaults to user preferences)
            expires_in_days: Days until notification expires

        Returns:
            Created notification
        """
        # Get user preferences
        prefs = await self._get_user_preferences(user_id)

        # Determine delivery channels
        if channels is None:
            channels = await self._get_enabled_channels(user_id, notification_type, prefs)

        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        # Create notification
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            priority=priority,
            title=title,
            message=message,
            data=data or {},
            action_url=action_url,
            action_text=action_text,
            channels=[ch.value for ch in channels],
            expires_at=expires_at
        )

        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)

        # Deliver via channels
        if NotificationChannel.EMAIL in channels:
            await self._send_email(notification, prefs)

        if NotificationChannel.WEBHOOK in channels:
            await self._send_webhook(notification, prefs)

        logger.info(
            f"Created notification {notification.id} for user {user_id}: {notification_type}"
        )

        return notification

    async def notify_plugin_approved(
        self,
        user_id: int,
        plugin_name: str,
        plugin_id: int,
        plugin_url: str
    ):
        """Notify user that their plugin was approved"""
        await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.PLUGIN_APPROVED,
            title=f"Plugin '{plugin_name}' Approved!",
            message=f"Your plugin '{plugin_name}' has been approved and is now available in the marketplace.",
            data={"plugin_id": plugin_id, "plugin_name": plugin_name},
            action_url=plugin_url,
            action_text="View Plugin",
            priority=NotificationPriority.HIGH
        )

    async def notify_plugin_rejected(
        self,
        user_id: int,
        plugin_name: str,
        plugin_id: int,
        feedback: str
    ):
        """Notify user that their plugin was rejected"""
        await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.PLUGIN_REJECTED,
            title=f"Plugin '{plugin_name}' Needs Changes",
            message=f"Your plugin requires some changes before approval.\n\nFeedback: {feedback}",
            data={"plugin_id": plugin_id, "plugin_name": plugin_name, "feedback": feedback},
            action_url=f"/plugins/{plugin_id}/edit",
            action_text="Update Plugin",
            priority=NotificationPriority.HIGH
        )

    async def notify_template_approved(
        self,
        user_id: int,
        template_name: str,
        template_id: int,
        template_url: str
    ):
        """Notify user that their template was approved"""
        await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.TEMPLATE_APPROVED,
            title=f"Template '{template_name}' Approved!",
            message=f"Your template '{template_name}' has been approved and is now available in the marketplace.",
            data={"template_id": template_id, "template_name": template_name},
            action_url=template_url,
            action_text="View Template",
            priority=NotificationPriority.HIGH
        )

    async def notify_template_rejected(
        self,
        user_id: int,
        template_name: str,
        template_id: int,
        feedback: str
    ):
        """Notify user that their template was rejected"""
        await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.TEMPLATE_REJECTED,
            title=f"Template '{template_name}' Needs Changes",
            message=f"Your template requires some changes before approval.\n\nFeedback: {feedback}",
            data={"template_id": template_id, "template_name": template_name, "feedback": feedback},
            action_url=f"/templates/{template_id}/edit",
            action_text="Update Template",
            priority=NotificationPriority.HIGH
        )

    async def notify_new_review(
        self,
        user_id: int,
        item_name: str,
        item_type: str,  # "plugin" or "template"
        item_id: int,
        reviewer_name: str,
        rating: int
    ):
        """Notify user of a new review on their plugin/template"""
        await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.NEW_REVIEW,
            title=f"New Review on '{item_name}'",
            message=f"{reviewer_name} left a {rating}-star review on your {item_type}.",
            data={
                "item_id": item_id,
                "item_type": item_type,
                "item_name": item_name,
                "reviewer": reviewer_name,
                "rating": rating
            },
            action_url=f"/{item_type}s/{item_id}/reviews",
            action_text="View Reviews",
            priority=NotificationPriority.NORMAL
        )

    async def notify_badge_awarded(
        self,
        user_id: int,
        badge_name: str,
        badge_code: str,
        badge_description: str
    ):
        """Notify user of a new badge award"""
        await self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.BADGE_AWARDED,
            title=f"🎖️ Badge Earned: {badge_name}",
            message=f"Congratulations! You've earned the '{badge_name}' badge.\n\n{badge_description}",
            data={"badge_code": badge_code, "badge_name": badge_name},
            action_url="/contributors/me",
            action_text="View Profile",
            priority=NotificationPriority.HIGH
        )

    async def mark_as_read(self, notification_id: int) -> bool:
        """Mark notification as read"""
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()

        if not notification:
            return False

        notification.is_read = True
        notification.read_at = datetime.utcnow()
        await self.db.commit()
        return True

    async def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user"""
        from sqlalchemy import update

        result = await self.db.execute(
            update(Notification)
            .where(and_(Notification.user_id == user_id, Notification.is_read == False))
            .values(is_read=True, read_at=datetime.utcnow())
        )
        await self.db.commit()
        return result.rowcount

    async def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """Get notifications for a user"""
        query = select(Notification).where(Notification.user_id == user_id)

        if unread_only:
            query = query.where(Notification.is_read == False)

        query = query.order_by(Notification.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications"""
        from sqlalchemy import func

        result = await self.db.execute(
            select(func.count(Notification.id))
            .where(and_(Notification.user_id == user_id, Notification.is_read == False))
        )
        return result.scalar_one()

    async def _get_user_preferences(self, user_id: int) -> Optional[NotificationPreference]:
        """Get user notification preferences"""
        result = await self.db.execute(
            select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def _get_enabled_channels(
        self,
        user_id: int,
        notification_type: NotificationType,
        prefs: Optional[NotificationPreference]
    ) -> List[NotificationChannel]:
        """Determine which channels are enabled for this notification"""
        channels = [NotificationChannel.IN_APP]  # Always show in-app

        if not prefs:
            # Default: email + in-app
            return [NotificationChannel.EMAIL, NotificationChannel.IN_APP]

        # Check user preferences
        type_prefs = prefs.preferences.get(notification_type.value, True)

        if type_prefs and prefs.email_enabled:
            channels.append(NotificationChannel.EMAIL)

        if type_prefs and prefs.webhook_enabled and prefs.webhook_url:
            channels.append(NotificationChannel.WEBHOOK)

        return channels

    async def _send_email(
        self,
        notification: Notification,
        prefs: Optional[NotificationPreference]
    ):
        """Send notification via email"""
        try:
            # Get user email
            result = await self.db.execute(
                select(User).where(User.id == notification.user_id)
            )
            user = result.scalar_one_or_none()

            if not user or not user.email:
                logger.warning(f"No email found for user {notification.user_id}")
                return

            # TODO: Implement actual email sending
            # This would integrate with an email service (SendGrid, AWS SES, etc.)
            logger.info(f"Email would be sent to {user.email}: {notification.title}")

            # Update notification
            notification.email_sent = True
            notification.email_sent_at = datetime.utcnow()
            await self.db.commit()

        except Exception as e:
            logger.error(f"Failed to send email for notification {notification.id}: {e}")
            notification.email_error = str(e)
            await self.db.commit()

    async def _send_webhook(
        self,
        notification: Notification,
        prefs: Optional[NotificationPreference]
    ):
        """Send notification via webhook"""
        try:
            if not prefs or not prefs.webhook_url:
                return

            # TODO: Implement actual webhook sending
            # This would make HTTP POST to user's webhook URL
            logger.info(f"Webhook would be sent to {prefs.webhook_url}: {notification.title}")

            # Update notification
            notification.webhook_sent = True
            notification.webhook_sent_at = datetime.utcnow()
            await self.db.commit()

        except Exception as e:
            logger.error(f"Failed to send webhook for notification {notification.id}: {e}")
            notification.webhook_error = str(e)
            await self.db.commit()


# Convenience function to get notification service
async def get_notification_service(db: AsyncSession) -> NotificationService:
    """Get notification service instance"""
    return NotificationService(db)
