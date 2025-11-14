"""
Template Community Database Models

Models for community-contributed templates, versions, ratings, and comments.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float,
    ForeignKey, JSON, Enum as SQLEnum, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship

from resoftai.models.base import Base


class TemplateVisibility(str, Enum):
    """Template visibility options."""
    PUBLIC = "public"
    PRIVATE = "private"
    ORGANIZATION = "organization"


class TemplateStatus(str, Enum):
    """Template publication status."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class TemplateModel(Base):
    """
    Community-contributed template model.

    Represents a user-created template that can be shared with the community.
    """
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)

    # Basic Info
    template_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, index=True)

    # Author Info
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    author = relationship("User", back_populates="templates")

    # Visibility & Status
    visibility = Column(
        SQLEnum(TemplateVisibility),
        default=TemplateVisibility.PUBLIC,
        nullable=False,
        index=True
    )
    status = Column(
        SQLEnum(TemplateStatus),
        default=TemplateStatus.DRAFT,
        nullable=False,
        index=True
    )

    # Metadata
    tags = Column(JSON, default=list)  # List of tags
    icon_url = Column(String(500))
    screenshot_urls = Column(JSON, default=list)  # List of screenshot URLs

    # Statistics
    download_count = Column(Integer, default=0)
    usage_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)

    # Template Content (current version)
    current_version_id = Column(Integer, ForeignKey("template_versions.id"))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)

    # Relationships
    versions = relationship("TemplateVersion", back_populates="template", cascade="all, delete-orphan")
    ratings = relationship("TemplateRating", back_populates="template", cascade="all, delete-orphan")
    comments = relationship("TemplateComment", back_populates="template", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_template_author_status', 'author_id', 'status'),
        Index('idx_template_category_status', 'category', 'status'),
        Index('idx_template_visibility_status', 'visibility', 'status'),
    )


class TemplateVersion(Base):
    """
    Template version model.

    Each template can have multiple versions for tracking changes.
    """
    __tablename__ = "template_versions"

    id = Column(Integer, primary_key=True, index=True)

    # Template Reference
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False, index=True)
    template = relationship("TemplateModel", back_populates="versions")

    # Version Info
    version = Column(String(50), nullable=False)  # e.g., "1.0.0", "1.1.0"
    version_name = Column(String(200))  # Optional friendly name
    changelog = Column(Text)  # What changed in this version

    # Template Content
    variables = Column(JSON, nullable=False)  # Template variables definition
    files = Column(JSON, nullable=False)  # List of template files
    directories = Column(JSON, nullable=False)  # Directory structure
    setup_commands = Column(JSON, default=list)  # Setup commands
    requirements = Column(JSON, default=dict)  # Requirements (Python, Node, etc.)
    dependencies = Column(JSON, default=list)  # Dependencies

    # Status
    is_stable = Column(Boolean, default=False)  # Stable release
    is_latest = Column(Boolean, default=True)  # Latest version

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = relationship("User")

    # Unique constraint: one version number per template
    __table_args__ = (
        UniqueConstraint('template_id', 'version', name='uq_template_version'),
        Index('idx_template_version_latest', 'template_id', 'is_latest'),
    )


class TemplateRating(Base):
    """
    Template rating model.

    Users can rate templates on a 1-5 scale.
    """
    __tablename__ = "template_ratings"

    id = Column(Integer, primary_key=True, index=True)

    # References
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False, index=True)
    template = relationship("TemplateModel", back_populates="ratings")

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User")

    # Rating
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review = Column(Text)  # Optional review text

    # Metadata
    helpful_count = Column(Integer, default=0)  # How many found this helpful

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Constraints: One rating per user per template
    __table_args__ = (
        UniqueConstraint('template_id', 'user_id', name='uq_template_user_rating'),
        Index('idx_template_rating_score', 'template_id', 'rating'),
    )


class TemplateComment(Base):
    """
    Template comment model.

    Users can leave comments on templates.
    """
    __tablename__ = "template_comments"

    id = Column(Integer, primary_key=True, index=True)

    # References
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False, index=True)
    template = relationship("TemplateModel", back_populates="comments")

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User")

    # Comment Content
    content = Column(Text, nullable=False)

    # Threading Support
    parent_id = Column(Integer, ForeignKey("template_comments.id"), index=True)
    parent = relationship("TemplateComment", remote_side=[id], backref="replies")

    # Metadata
    is_edited = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index('idx_template_comment_created', 'template_id', 'created_at'),
        Index('idx_template_comment_parent', 'parent_id'),
    )


class TemplateLike(Base):
    """
    Template like/favorite model.

    Users can like/favorite templates for quick access.
    """
    __tablename__ = "template_likes"

    id = Column(Integer, primary_key=True, index=True)

    # References
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Constraints: One like per user per template
    __table_args__ = (
        UniqueConstraint('template_id', 'user_id', name='uq_template_user_like'),
    )


# Update User model to include relationships
# Add to resoftai/models/user.py:
# templates = relationship("TemplateModel", back_populates="author")
