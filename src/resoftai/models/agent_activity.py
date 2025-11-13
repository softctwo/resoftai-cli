"""Agent activity model."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from resoftai.db import Base


class AgentActivity(Base):
    """Agent activity model for tracking agent work."""

    __tablename__ = "agent_activities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    agent_role: Mapped[str] = mapped_column(String(50), nullable=False)  # pm, requirements, architect, etc.
    status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # idle, working, completed, failed
    current_task: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completed_tasks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="agent_activities")

    def __repr__(self) -> str:
        return f"<AgentActivity(id={self.id}, role='{self.agent_role}', status='{self.status}')>"
