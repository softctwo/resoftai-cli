"""File and FileVersion models."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from resoftai.db import Base


class File(Base):
    """File model for project source code files."""

    __tablename__ = "files"
    __table_args__ = (
        UniqueConstraint("project_id", "path", name="uix_project_path"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    path: Mapped[str] = mapped_column(String(500), nullable=False)  # Relative path in project
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # python, javascript, etc.
    size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # File size in bytes
    current_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    project = relationship("Project", back_populates="files")
    versions = relationship("FileVersion", back_populates="file", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<File(id={self.id}, path='{self.path}', version={self.current_version})>"


class FileVersion(Base):
    """File version model for version control."""

    __tablename__ = "file_versions"
    __table_args__ = (
        UniqueConstraint("file_id", "version", name="uix_file_version"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id", ondelete="CASCADE"), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    file = relationship("File", back_populates="versions")
    created_by_user = relationship("User", back_populates="file_versions")

    def __repr__(self) -> str:
        return f"<FileVersion(id={self.id}, file_id={self.file_id}, version={self.version})>"
