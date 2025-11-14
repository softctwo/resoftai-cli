"""
Plugin System Models - Extensibility and Marketplace

This module contains models for the plugin system:
- Plugin definitions and metadata
- Plugin marketplace
- Plugin installations and configurations
- Plugin ratings and reviews
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


class PluginStatus(str, enum.Enum):
    """Plugin lifecycle status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEPRECATED = "deprecated"


class PluginCategory(str, enum.Enum):
    """Plugin categories for marketplace organization"""
    AGENT = "agent"  # Custom agents
    LLM_PROVIDER = "llm_provider"  # Additional LLM providers
    CODE_QUALITY = "code_quality"  # Linters, formatters
    INTEGRATION = "integration"  # Third-party integrations (Jira, Slack, etc.)
    TEMPLATE = "template"  # Project templates
    GENERATOR = "generator"  # Code generators
    WORKFLOW = "workflow"  # Custom workflows
    UI = "ui"  # UI extensions
    UTILITY = "utility"  # General utilities


class InstallationStatus(str, enum.Enum):
    """Plugin installation status"""
    INSTALLING = "installing"
    ACTIVE = "active"
    DISABLED = "disabled"
    FAILED = "failed"
    UPDATING = "updating"


# =============================================================================
# Plugin Registry and Marketplace
# =============================================================================

class Plugin(Base):
    """
    Plugin registry model

    Represents a plugin available in the marketplace or custom-developed.
    Contains metadata, version info, and marketplace details.
    """
    __tablename__ = "plugins"

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
    category = Column(SQLEnum(PluginCategory), nullable=False, index=True)
    tags = Column(JSON, nullable=True)  # List of tag strings

    # Version information
    version = Column(String(50), nullable=False)  # Semantic versioning (e.g., "1.2.3")
    min_platform_version = Column(String(50), nullable=True)  # Minimum ResoftAI version required
    max_platform_version = Column(String(50), nullable=True)

    # Plugin package
    package_url = Column(String(500), nullable=True)  # Download URL
    package_checksum = Column(String(128), nullable=True)  # SHA256 checksum
    source_url = Column(String(500), nullable=True)  # Source code repository

    # Marketplace status
    status = Column(SQLEnum(PluginStatus), default=PluginStatus.DRAFT, nullable=False, index=True)
    is_featured = Column(Boolean, default=False)
    is_official = Column(Boolean, default=False)  # Official ResoftAI plugin

    # Pricing (for future paid plugins)
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

    # Configuration schema (JSON Schema for plugin settings)
    config_schema = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

    # Relationships
    installations = relationship("PluginInstallation", back_populates="plugin", cascade="all, delete-orphan")
    reviews = relationship("PluginReview", back_populates="plugin", cascade="all, delete-orphan")
    versions = relationship("PluginVersion", back_populates="plugin", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Plugin(slug='{self.slug}', version='{self.version}', status='{self.status}')>"


class PluginVersion(Base):
    """
    Plugin version history

    Tracks all versions of a plugin for version management and rollback.
    """
    __tablename__ = "plugin_versions"

    id = Column(Integer, primary_key=True, index=True)
    plugin_id = Column(Integer, ForeignKey("plugins.id", ondelete="CASCADE"), nullable=False)

    # Version details
    version = Column(String(50), nullable=False)
    changelog = Column(Text, nullable=True)  # Release notes

    # Package info
    package_url = Column(String(500), nullable=False)
    package_checksum = Column(String(128), nullable=False)

    # Compatibility
    min_platform_version = Column(String(50), nullable=True)
    max_platform_version = Column(String(50), nullable=True)

    # Status
    is_stable = Column(Boolean, default=True)
    is_deprecated = Column(Boolean, default=False)

    # Statistics
    downloads_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    plugin = relationship("Plugin", back_populates="versions")

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('plugin_id', 'version', name='uq_plugin_version'),
    )

    def __repr__(self):
        return f"<PluginVersion(plugin_id={self.plugin_id}, version='{self.version}')>"


# =============================================================================
# Plugin Installation and Configuration
# =============================================================================

class PluginInstallation(Base):
    """
    Plugin installation record

    Tracks which plugins are installed for each organization/user.
    """
    __tablename__ = "plugin_installations"

    id = Column(Integer, primary_key=True, index=True)
    plugin_id = Column(Integer, ForeignKey("plugins.id", ondelete="CASCADE"), nullable=False)

    # Installation scope
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    # Version installed
    installed_version = Column(String(50), nullable=False)

    # Status
    status = Column(SQLEnum(InstallationStatus), default=InstallationStatus.INSTALLING, nullable=False)

    # Configuration (user-provided settings)
    config = Column(JSON, nullable=True, default=dict)

    # Error tracking
    error_message = Column(Text, nullable=True)

    # Timestamps
    installed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)

    # Relationships
    plugin = relationship("Plugin", back_populates="installations")

    # Unique constraint: plugin can only be installed once per scope
    __table_args__ = (
        UniqueConstraint('plugin_id', 'organization_id', 'user_id', name='uq_plugin_installation'),
        Index('ix_installations_org_id', 'organization_id'),
        Index('ix_installations_user_id', 'user_id'),
    )

    def __repr__(self):
        return f"<PluginInstallation(plugin_id={self.plugin_id}, status='{self.status}')>"


# =============================================================================
# Plugin Reviews and Ratings
# =============================================================================

class PluginReview(Base):
    """
    Plugin reviews and ratings from users
    """
    __tablename__ = "plugin_reviews"

    id = Column(Integer, primary_key=True, index=True)
    plugin_id = Column(Integer, ForeignKey("plugins.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Rating (1-5 stars)
    rating = Column(Integer, nullable=False)  # 1, 2, 3, 4, 5

    # Review content
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=True)

    # Helpful votes
    helpful_count = Column(Integer, default=0)

    # Moderation
    is_verified = Column(Boolean, default=False)  # Verified purchase/installation
    is_flagged = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    plugin = relationship("Plugin", back_populates="reviews")

    # Unique constraint: one review per user per plugin
    __table_args__ = (
        UniqueConstraint('plugin_id', 'user_id', name='uq_plugin_user_review'),
    )

    def __repr__(self):
        return f"<PluginReview(plugin_id={self.plugin_id}, user_id={self.user_id}, rating={self.rating})>"


# =============================================================================
# Community and Social Features
# =============================================================================

class PluginComment(Base):
    """
    Comments and discussions on plugins
    """
    __tablename__ = "plugin_comments"

    id = Column(Integer, primary_key=True, index=True)
    plugin_id = Column(Integer, ForeignKey("plugins.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Comment content
    content = Column(Text, nullable=False)

    # Threading support
    parent_id = Column(Integer, ForeignKey("plugin_comments.id", ondelete="CASCADE"), nullable=True)

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
    replies = relationship("PluginComment", backref="parent", remote_side=[id])

    def __repr__(self):
        return f"<PluginComment(plugin_id={self.plugin_id}, user_id={self.user_id})>"


class PluginCollection(Base):
    """
    User-created plugin collections/lists

    Allows users to organize and share curated plugin lists.
    """
    __tablename__ = "plugin_collections"

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
    items = relationship("PluginCollectionItem", back_populates="collection", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PluginCollection(slug='{self.slug}', name='{self.name}')>"


class PluginCollectionItem(Base):
    """
    Items in a plugin collection
    """
    __tablename__ = "plugin_collection_items"

    id = Column(Integer, primary_key=True, index=True)
    collection_id = Column(Integer, ForeignKey("plugin_collections.id", ondelete="CASCADE"), nullable=False)
    plugin_id = Column(Integer, ForeignKey("plugins.id", ondelete="CASCADE"), nullable=False)

    # Optional note from collection curator
    note = Column(Text, nullable=True)

    # Order in collection
    position = Column(Integer, default=0)

    # Timestamp
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    collection = relationship("PluginCollection", back_populates="items")

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('collection_id', 'plugin_id', name='uq_collection_plugin'),
    )

    def __repr__(self):
        return f"<PluginCollectionItem(collection_id={self.collection_id}, plugin_id={self.plugin_id})>"
