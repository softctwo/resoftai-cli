"""Log model."""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from resoftai.db import Base


class Log(Base):
    """Log model for system and project logs."""

    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("projects.id"), nullable=True, index=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False)  # debug, info, warning, error
    message: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Agent role or system component
    extra_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)  # Renamed from 'metadata' to avoid SQLAlchemy conflict

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    project = relationship("Project", back_populates="logs")

    def __repr__(self) -> str:
        return f"<Log(id={self.id}, level='{self.level}', source='{self.source}')>"
