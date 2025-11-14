"""Data models for AI analysis features."""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from resoftai.db.base import Base


class AnalysisType(str, enum.Enum):
    """Types of AI analysis."""
    CODE_REVIEW = "code_review"
    PREDICTIVE = "predictive"
    MULTI_MODEL = "multi_model"


class CodeIssueModel(Base):
    """Database model for code review issues."""
    __tablename__ = "code_issues"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("code_reviews.id"), nullable=False)
    issue_id = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)  # critical, high, medium, low, info
    category = Column(String(50), nullable=False)  # security, performance, bug, etc.
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    file_path = Column(String(500), nullable=False)
    line_start = Column(Integer, nullable=False)
    line_end = Column(Integer, nullable=False)
    code_snippet = Column(Text)
    suggestion = Column(Text)
    auto_fixable = Column(Integer, default=0)  # Boolean: 0 or 1
    fix_code = Column(Text)
    confidence = Column(Float, default=1.0)
    references = Column(JSON)  # List of reference links
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    review = relationship("CodeReview", back_populates="issues")


class CodeReview(Base):
    """Database model for code reviews."""
    __tablename__ = "code_reviews"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    language = Column(String(50), nullable=False)
    code_hash = Column(String(64))  # SHA-256 hash of code
    files_reviewed = Column(Integer, default=1)
    total_lines = Column(Integer, default=0)
    quality_score = Column(Float, default=0.0)
    maintainability_index = Column(Float, default=0.0)
    security_score = Column(Float, default=0.0)
    summary = Column(Text)
    recommendations = Column(JSON)  # List of recommendations
    reviewed_at = Column(DateTime, default=datetime.utcnow)
    review_duration = Column(Float, default=0.0)  # seconds
    ai_models_used = Column(JSON)  # List of AI models

    # Relationships
    project = relationship("Project", back_populates="code_reviews")
    issues = relationship("CodeIssueModel", back_populates="review", cascade="all, delete-orphan")


class PredictiveAnalysis(Base):
    """Database model for predictive analysis."""
    __tablename__ = "predictive_analyses"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    analysis_timestamp = Column(DateTime, default=datetime.utcnow)

    # Progress Prediction
    estimated_completion = Column(DateTime)
    progress_confidence = Column(Float, default=0.0)
    current_progress = Column(Float, default=0.0)
    projected_velocity = Column(Float, default=0.0)
    remaining_tasks = Column(Integer, default=0)
    bottlenecks = Column(JSON)  # List of bottlenecks
    acceleration_opportunities = Column(JSON)

    # Risk Assessment
    risk_level = Column(String(20))  # low, medium, high, critical
    risk_score = Column(Float, default=0.0)
    identified_risks = Column(JSON)  # List of risk objects
    mitigation_strategies = Column(JSON)
    risk_factors = Column(JSON)  # Dict of risk factors

    # Effort Estimation
    estimated_hours = Column(Float, default=0.0)
    estimated_days = Column(Float, default=0.0)
    confidence_range_min = Column(Float, default=0.0)
    confidence_range_max = Column(Float, default=0.0)
    complexity_score = Column(Float, default=0.0)
    similar_projects = Column(JSON)
    assumptions = Column(JSON)

    # Quality Trend
    current_quality = Column(Float, default=0.0)
    quality_trend = Column(String(20))  # improving, stable, declining
    predicted_quality = Column(Float, default=0.0)
    quality_velocity = Column(Float, default=0.0)
    improvement_areas = Column(JSON)
    regression_risks = Column(JSON)

    # Resource Forecast
    predicted_team_size = Column(Integer, default=0)
    predicted_budget = Column(Float, default=0.0)
    predicted_infrastructure = Column(JSON)
    scaling_timeline = Column(JSON)
    optimization_opportunities = Column(JSON)

    # Overall
    key_insights = Column(JSON)
    recommended_actions = Column(JSON)
    confidence_score = Column(Float, default=0.0)

    # Relationships
    project = relationship("Project", back_populates="predictive_analyses")


class MultiModelExecution(Base):
    """Database model for multi-model executions."""
    __tablename__ = "multi_model_executions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    prompt = Column(Text, nullable=False)
    strategy = Column(String(50), nullable=False)  # voting, weighted, cascade, etc.
    task_complexity = Column(String(20), nullable=False)  # simple, moderate, complex, critical

    # Results
    final_output = Column(Text)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    avg_latency = Column(Float, default=0.0)
    consensus_score = Column(Float, default=0.0)
    models_used = Column(Integer, default=0)
    successful_responses = Column(Integer, default=0)

    # Model Responses
    individual_responses = Column(JSON)  # List of response objects
    metadata = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="multi_model_executions")
