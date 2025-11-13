"""LLM configuration model."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from resoftai.db import Base


class LLMConfigModel(Base):
    """LLM configuration model for storing user's AI model configurations."""

    __tablename__ = "llm_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Configuration name
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # anthropic, deepseek, zhipu, etc.
    api_key_encrypted: Mapped[str] = mapped_column(Text, nullable=False)  # Encrypted API key
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    max_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="llm_configs")

    def __repr__(self) -> str:
        return f"<LLMConfigModel(id={self.id}, provider='{self.provider}', model='{self.model_name}')>"
