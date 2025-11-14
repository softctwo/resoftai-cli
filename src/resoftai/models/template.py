"""
Template Marketplace Models - Community-Contributed Templates

This module contains models for the template marketplace system:
- Template definitions and metadata
- Template marketplace
- Template usage tracking
- Template ratings and reviews
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean, Column, Integer, String, Text, DateTime,
    ForeignKey, JSON, Float, Enum as SQLEnum,
    UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
import enum

from resoftai.db.connection import Base


class TemplateStatus(str, enum.Enum):
    """Template lifecycle status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEPRECATED = "deprecated"


class TemplateCategory(str, enum.Enum):
    """Template categories for marketplace organization"""
    WEB_APP = "web_app"
    REST_API = "rest_api"
    CLI_TOOL = "cli_tool"
    MICROSERVICE = "microservice"
    DATA_PIPELINE = "data_pipeline"
    ML_PROJECT = "ml_project"
    MOBILE_APP = "mobile_app"
    DESKTOP_APP = "desktop_app"


# =============================================================================
# Template Registry and Marketplace
# =============================================================================

class TemplateModel(Base):
    """
    Template registry model for marketplace

    Represents a template available in the marketplace or custom-developed.
    Contains metadata, version info, and marketplace details.
    """
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)

    # Basic information
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(200), unique=True, nullable=False, index=True)  # URL-friendly identifier
    description = Column(Text, nullable=True)
    long_description = Column(Text, nullable=True)  # Markdown supported

    # Author/Publisher
    author_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    author_name = Column(String(200), nullable=True)  # Display name
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)

    # Classification
    category = Column(SQLEnum(TemplateCategory), nullable=False, index=True)
    tags = Column(JSON, nullable=True)  # List of tag strings

    # Version information
    version = Column(String(50), nullable=False)  # Semantic versioning (e.g., "1.2.3")
    min_platform_version = Column(String(50), nullable=True)  # Minimum ResoftAI version required

    # Template content (serialized Template object from templates.base)
    template_data = Column(JSON, nullable=False)  # Full template structure

    # Template package
    package_url = Column(String(500), nullable=True)  # Git repo or download URL
    source_url = Column(String(500), nullable=True)  # Source code repository

    # Marketplace status
    status = Column(SQLEnum(TemplateStatus), default=TemplateStatus.DRAFT, nullable=False, index=True)
    is_featured = Column(Boolean, default=False)
    is_official = Column(Boolean, default=False)  # Official ResoftAI template

    # Pricing (for future paid templates)
    is_free = Column(Boolean, default=True)
    price = Column(Float, nullable=True)  # In USD
    license = Column(String(100), nullable=True)  # MIT, Apache-2.0, proprietary, etc.

    # Statistics
    downloads_count = Column(Integer, default=0)
    installs_count = Column(Integer, default=0)
    rating_average = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)

    # Documentation and support
    documentation_url = Column(String(500), nullable=True)
    support_url = Column(String(500), nullable=True)
    homepage_url = Column(String(500), nullable=True)

    # Screenshots and media
    icon_url = Column(String(500), nullable=True)
    screenshots = Column(JSON, nullable=True)  # List of screenshot URLs

    # Preview images (generated from template)
    preview_images = Column(JSON, nullable=True)  # List of preview image URLs

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

    # Relationships
    versions = relationship("TemplateVersion", back_populates="template", cascade="all, delete-orphan")
    installations = relationship("TemplateInstallation", back_populates="template", cascade="all, delete-orphan")
    reviews = relationship("TemplateReview", back_populates="template", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TemplateModel(slug='{self.slug}', version='{self.version}', status='{self.status}')>"


class TemplateVersion(Base):
    """
    Template version history

    Tracks all versions of a template for version management and rollback.
    """
    __tablename__ = "template_versions"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)

    # Version details
    version = Column(String(50), nullable=False)
    changelog = Column(Text, nullable=True)  # Release notes

    # Template content for this version
    template_data = Column(JSON, nullable=False)

    # Package info
    package_url = Column(String(500), nullable=True)

    # Compatibility
    min_platform_version = Column(String(50), nullable=True)

    # Status
    is_stable = Column(Boolean, default=True)
    is_deprecated = Column(Boolean, default=False)

    # Statistics
    downloads_count = Column(Integer, default=0)
    installs_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    template = relationship("TemplateModel", back_populates="versions")

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('template_id', 'version', name='uq_template_version'),
    )

    def __repr__(self):
        return f"<TemplateVersion(template_id={self.template_id}, version='{self.version}')>"


# =============================================================================
# Template Usage Tracking
# =============================================================================

class TemplateInstallation(Base):
    """
    Template installation/usage record

    Tracks when and how templates are used in projects.
    """
    __tablename__ = "template_installations"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)

    # Installation scope
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)

    # Version installed
    installed_version = Column(String(50), nullable=False)

    # Variables used during installation
    variables_used = Column(JSON, nullable=True)

    # Output location
    output_path = Column(String(500), nullable=True)

    # Success/failure
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

    # Timestamps
    installed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    template = relationship("TemplateModel", back_populates="installations")

    # Indexes
    __table_args__ = (
        Index('ix_template_installations_user_id', 'user_id'),
        Index('ix_template_installations_template_id', 'template_id'),
    )

    def __repr__(self):
        return f"<TemplateInstallation(template_id={self.template_id}, user_id={self.user_id})>"


# =============================================================================
# Template Reviews and Ratings
# =============================================================================

class TemplateReview(Base):
    """
    Template reviews and ratings from users
    """
    __tablename__ = "template_reviews"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Rating (1-5 stars)
    rating = Column(Integer, nullable=False)  # 1, 2, 3, 4, 5

    # Review content
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=True)

    # Helpful votes
    helpful_count = Column(Integer, default=0)

    # Moderation
    is_verified = Column(Boolean, default=False)  # Verified usage
    is_flagged = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    template = relationship("TemplateModel", back_populates="reviews")

    # Unique constraint: one review per user per template
    __table_args__ = (
        UniqueConstraint('template_id', 'user_id', name='uq_template_user_review'),
    )

    def __repr__(self):
        return f"<TemplateReview(template_id={self.template_id}, user_id={self.user_id}, rating={self.rating})>"


# =============================================================================
# Community and Social Features
# =============================================================================

class TemplateComment(Base):
    """
    Comments and discussions on templates
    """
    __tablename__ = "template_comments"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Comment content
    content = Column(Text, nullable=False)

    # Threading support
    parent_id = Column(Integer, ForeignKey("template_comments.id", ondelete="CASCADE"), nullable=True)

    # Engagement
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)

    # Moderation
    is_deleted = Column(Boolean, default=False)
    is_flagged = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    replies = relationship("TemplateComment", backref="parent", remote_side=[id])

    def __repr__(self):
        return f"<TemplateComment(template_id={self.template_id}, user_id={self.user_id})>"


class TemplateCollection(Base):
    """
    User-created template collections/lists

    Allows users to organize and share curated template lists.
    """
    __tablename__ = "template_collections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Collection details
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    slug = Column(String(200), unique=True, nullable=False, index=True)

    # Visibility
    is_public = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)

    # Statistics
    followers_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = relationship("TemplateCollectionItem", back_populates="collection", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TemplateCollection(slug='{self.slug}', name='{self.name}')>"


class TemplateCollectionItem(Base):
    """
    Items in a template collection
    """
    __tablename__ = "template_collection_items"

    id = Column(Integer, primary_key=True, index=True)
    collection_id = Column(Integer, ForeignKey("template_collections.id", ondelete="CASCADE"), nullable=False)
    template_id = Column(Integer, ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)

    # Optional note from collection curator
    note = Column(Text, nullable=True)

    # Order in collection
    position = Column(Integer, default=0)

    # Timestamp
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    collection = relationship("TemplateCollection", back_populates="items")

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('collection_id', 'template_id', name='uq_collection_template'),
    )

    def __repr__(self):
        return f"<TemplateCollectionItem(collection_id={self.collection_id}, template_id={self.template_id})>"


# =============================================================================
# Contributor Recognition
# =============================================================================

class ContributorProfile(Base):
    """
    Contributor profile and statistics

    Tracks contributor achievements and recognition.
    """
    __tablename__ = "contributor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Profile information
    display_name = Column(String(200), nullable=False)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    website = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    twitter_url = Column(String(500), nullable=True)

    # Statistics
    plugins_count = Column(Integer, default=0)
    templates_count = Column(Integer, default=0)
    total_downloads = Column(Integer, default=0)
    total_installs = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)

    # Recognition
    badges = Column(JSON, nullable=True, default=list)  # List of badge codes
    is_verified = Column(Boolean, default=False)  # Verified developer
    is_featured = Column(Boolean, default=False)  # Featured contributor

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ContributorProfile(user_id={self.user_id}, display_name='{self.display_name}')>"


class ContributorBadge(Base):
    """
    Achievement badges for contributors

    Defines available badges that contributors can earn.
    """
    __tablename__ = "contributor_badges"

    id = Column(Integer, primary_key=True, index=True)

    # Badge identification
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Visual
    icon_url = Column(String(500), nullable=True)
    color = Column(String(20), nullable=True)  # Hex color code

    # Requirements (JSON schema for badge criteria)
    requirements = Column(JSON, nullable=False)

    # Badge tier/rarity
    tier = Column(String(20), nullable=True)  # bronze, silver, gold, platinum

    # Visibility
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ContributorBadge(code='{self.code}', name='{self.name}')>"
