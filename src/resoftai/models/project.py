"""Project model."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from resoftai.db import Base


class Project(Base):
    """Project model for software development projects."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    requirements: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False, index=True
    )  # pending, planning, developing, testing, completed, failed
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-100
    current_stage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # LLM configuration
    llm_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    llm_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # User relationship
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="projects")
    agent_activities = relationship("AgentActivity", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    files = relationship("File", back_populates="project", cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="project", cascade="all, delete-orphan")
    workflow_metrics = relationship("WorkflowMetrics", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}', progress={self.progress}%)>"
