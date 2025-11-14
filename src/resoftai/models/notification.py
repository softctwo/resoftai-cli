"""
Notification System Models

Provides notification tracking and delivery for:
- Plugin/Template review status changes
- Comments and reviews
- Badge awards
- System announcements
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean, Column, Integer, String, Text, DateTime,
    ForeignKey, JSON, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship
import enum

from resoftai.db.connection import Base


class NotificationType(str, enum.Enum):
    """Notification types"""
    PLUGIN_APPROVED = "plugin_approved"
    PLUGIN_REJECTED = "plugin_rejected"
    TEMPLATE_APPROVED = "template_approved"
    TEMPLATE_REJECTED = "template_rejected"
    NEW_REVIEW = "new_review"
    NEW_COMMENT = "new_comment"
    BADGE_AWARDED = "badge_awarded"
    VERSION_PUBLISHED = "version_published"
    SYSTEM_ANNOUNCEMENT = "system_announcement"


class NotificationChannel(str, enum.Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class NotificationPriority(str, enum.Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base):
    """
    Notification model for user notifications

    Supports multiple delivery channels and tracks delivery status.
    """
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    # Recipient
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Notification details
    type = Column(SQLEnum(NotificationType), nullable=False)
    priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.NORMAL)

    # Content
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON, nullable=True)  # Additional context data

    # Links
    action_url = Column(String(500), nullable=True)  # URL to navigate to
    action_text = Column(String(100), nullable=True)  # Button text

    # Delivery channels
    channels = Column(JSON, nullable=False)  # List of NotificationChannel values

    # Status tracking
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)

    # Email delivery tracking
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime, nullable=True)
    email_error = Column(Text, nullable=True)

    # Webhook delivery tracking
    webhook_sent = Column(Boolean, default=False)
    webhook_sent_at = Column(DateTime, nullable=True)
    webhook_error = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration

    # Indexes
    __table_args__ = (
        Index('ix_notifications_user_created', 'user_id', 'created_at'),
        Index('ix_notifications_user_unread', 'user_id', 'is_read'),
    )

    def __repr__(self):
        return f"<Notification(user_id={self.user_id}, type='{self.type}', title='{self.title}')>"


class NotificationPreference(Base):
    """
    User notification preferences

    Controls which notifications are sent via which channels.
    """
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Channel preferences
    email_enabled = Column(Boolean, default=True)
    in_app_enabled = Column(Boolean, default=True)
    webhook_enabled = Column(Boolean, default=False)
    webhook_url = Column(String(500), nullable=True)

    # Notification type preferences (JSON)
    # Example: {"plugin_approved": True, "new_review": False, ...}
    preferences = Column(JSON, nullable=False, default=dict)

    # Quiet hours
    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(String(5), nullable=True)  # HH:MM format
    quiet_hours_end = Column(String(5), nullable=True)    # HH:MM format

    # Digest settings
    digest_enabled = Column(Boolean, default=False)
    digest_frequency = Column(String(20), nullable=True)  # daily, weekly

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<NotificationPreference(user_id={self.user_id})>"


class EmailTemplate(Base):
    """
    Email templates for notifications

    Stores HTML and text templates for different notification types.
    """
    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True)

    # Template identification
    template_key = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Template content
    subject_template = Column(String(500), nullable=False)  # Jinja2 template
    html_template = Column(Text, nullable=False)            # HTML Jinja2 template
    text_template = Column(Text, nullable=False)            # Plain text Jinja2 template

    # Variables required by template
    variables = Column(JSON, nullable=True)  # List of variable names

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<EmailTemplate(key='{self.template_key}', name='{self.name}')>"
