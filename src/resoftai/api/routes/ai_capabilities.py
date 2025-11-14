"""API routes for AI capabilities (multi-model, code review, predictive analysis)."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from resoftai.db import get_db
from resoftai.auth import get_current_user, require_admin
from resoftai.models.user import User
from resoftai.models.project import Project
from resoftai.models.ai_analysis import CodeReview, PredictiveAnalysis, MultiModelExecution
from resoftai.ai.multi_model_coordinator import (
    MultiModelCoordinator,
    CombinationStrategy,
    TaskComplexity,
    ModelConfig
)
from resoftai.ai.code_reviewer import IntelligentCodeReviewer, IssueSeverity, IssueCategory
from resoftai.ai.predictive_analyzer import PredictiveAnalyzer
from resoftai.llm.factory import LLMFactory
from sqlalchemy import select, desc

router = APIRouter(prefix="/ai", tags=["AI Capabilities"])


# ==================== Pydantic Models ====================

class ModelConfigRequest(BaseModel):
    """Request model for adding a model to coordinator."""
    provider: str = Field(..., description="LLM provider name")
    model_name: str = Field(..., description="Model name")
    weight: float = Field(1.0, ge=0.0, le=10.0, description="Model weight")
    priority: int = Field(1, ge=1, le=100, description="Model priority")
    cost_per_token: float = Field(0.0, ge=0.0, description="Cost per token")
    quality_score: float = Field(1.0, ge=0.0, le=1.0, description="Quality score")
    max_tokens: int = Field(4096, ge=1, le=128000, description="Max tokens")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperature")


class MultiModelExecuteRequest(BaseModel):
    """Request to execute prompt with multiple models."""
    prompt: str = Field(..., min_length=1, description="Prompt to execute")
    strategy: CombinationStrategy = Field(CombinationStrategy.VOTING, description="Combination strategy")
    task_complexity: TaskComplexity = Field(TaskComplexity.MODERATE, description="Task complexity")
    max_models: Optional[int] = Field(None, ge=1, le=10, description="Max models to use")
    quality_threshold: float = Field(0.7, ge=0.0, le=1.0, description="Quality threshold")
    project_id: Optional[int] = Field(None, description="Associated project ID")


class CodeReviewRequest(BaseModel):
    """Request to review code."""
    code: str = Field(..., min_length=1, description="Code to review")
    language: str = Field("python", description="Programming language")
    file_path: str = Field("", description="File path")
    project_id: Optional[int] = Field(None, description="Project ID")


class PredictiveAnalysisRequest(BaseModel):
    """Request for predictive analysis."""
    project_id: int = Field(..., gt=0, description="Project ID")
    current_data: dict = Field(..., description="Current project metrics")


class CodeIssueResponse(BaseModel):
    """Response model for code issue."""
    id: str
    severity: str
    category: str
    title: str
    description: str
    file_path: str
    line_start: int
    line_end: int
    code_snippet: str
    suggestion: str
    auto_fixable: bool
    confidence: float

    class Config:
        from_attributes = True


class CodeReviewResponse(BaseModel):
    """Response model for code review."""
    id: int
    project_id: int
    file_path: str
    language: str
    files_reviewed: int
    total_lines: int
    quality_score: float
    maintainability_index: float
    security_score: float
    summary: str
    recommendations: List[str]
    issues_count: int

    class Config:
        from_attributes = True


class PredictiveAnalysisResponse(BaseModel):
    """Response model for predictive analysis."""
    id: int
    project_id: int
    current_progress: float
    estimated_completion: str
    risk_level: str
    risk_score: float
    quality_trend: str
    key_insights: List[str]
    recommended_actions: List[str]
    confidence_score: float

    class Config:
        from_attributes = True


class MultiModelResponse(BaseModel):
    """Response from multi-model execution."""
    final_output: str
    strategy_used: str
    total_tokens: int
    total_cost: float
    avg_latency: float
    consensus_score: float
    models_used: int
    successful_responses: int


# ==================== Multi-Model Coordination ====================

# Global coordinator instance (in production, use dependency injection)
_coordinator: Optional[MultiModelCoordinator] = None


def get_coordinator() -> MultiModelCoordinator:
    """Get or create multi-model coordinator."""
    global _coordinator
    if _coordinator is None:
        llm_factory = LLMFactory()
        _coordinator = MultiModelCoordinator(llm_factory)
    return _coordinator


@router.post("/multi-model/configure", status_code=status.HTTP_200_OK)
async def configure_models(
    models: List[ModelConfigRequest],
    current_user: User = Depends(require_admin)
):
    """
    Configure models for multi-model coordination.

    Requires admin privileges.
    """
    coordinator = get_coordinator()

    # Clear existing models
    coordinator.models.clear()

    # Add new models
    for model_req in models:
        config = ModelConfig(
            provider=model_req.provider,
            model_name=model_req.model_name,
            weight=model_req.weight,
            priority=model_req.priority,
            cost_per_token=model_req.cost_per_token,
            quality_score=model_req.quality_score,
            max_tokens=model_req.max_tokens,
            temperature=model_req.temperature
        )
        coordinator.add_model(config)

    return {
        "status": "success",
        "message": f"Configured {len(models)} models for multi-model coordination",
        "models": [f"{m.provider}/{m.model_name}" for m in models]
    }


@router.post("/multi-model/execute", response_model=MultiModelResponse)
async def execute_multi_model(
    request: MultiModelExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Execute prompt using multiple AI models with specified strategy.

    Combines outputs from multiple models for improved quality.
    """
    coordinator = get_coordinator()

    # Execute with multi-model coordination
    result = await coordinator.execute(
        prompt=request.prompt,
        strategy=request.strategy,
        task_complexity=request.task_complexity,
        max_models=request.max_models,
        quality_threshold=request.quality_threshold
    )

    # Save execution to database
    execution = MultiModelExecution(
        project_id=request.project_id,
        prompt=request.prompt,
        strategy=request.strategy.value,
        task_complexity=request.task_complexity.value,
        final_output=result.final_output,
        total_tokens=result.total_tokens,
        total_cost=result.total_cost,
        avg_latency=result.avg_latency,
        consensus_score=result.consensus_score,
        models_used=result.metadata.get('models_used', 0),
        successful_responses=result.metadata.get('successful_responses', 0),
        individual_responses=[
            {
                'provider': r.provider,
                'model': r.model_name,
                'content': r.content,
                'success': r.success,
                'latency': r.latency
            }
            for r in result.individual_responses
        ],
        metadata=result.metadata
    )
    db.add(execution)
    await db.commit()

    return MultiModelResponse(
        final_output=result.final_output,
        strategy_used=result.strategy_used.value,
        total_tokens=result.total_tokens,
        total_cost=result.total_cost,
        avg_latency=result.avg_latency,
        consensus_score=result.consensus_score,
        models_used=result.metadata.get('models_used', 0),
        successful_responses=result.metadata.get('successful_responses', 0)
    )


@router.get("/multi-model/performance")
async def get_performance_stats(
    current_user: User = Depends(require_admin)
):
    """
    Get performance statistics for all configured models.

    Requires admin privileges.
    """
    coordinator = get_coordinator()
    stats = coordinator.get_performance_stats()

    return {
        "models": stats,
        "configured_models": len(coordinator.models)
    }


# ==================== Intelligent Code Review ====================

@router.post("/code-review", response_model=CodeReviewResponse)
async def review_code(
    request: CodeReviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform intelligent AI-powered code review.

    Analyzes code for security, performance, bugs, and best practices.
    """
    # Initialize code reviewer
    coordinator = get_coordinator()
    reviewer = IntelligentCodeReviewer(coordinator)

    # Perform review
    context = {"project_id": request.project_id} if request.project_id else {}
    report = await reviewer.review_code(
        code=request.code,
        language=request.language,
        file_path=request.file_path,
        context=context
    )

    # Save review to database
    code_review = CodeReview(
        project_id=request.project_id or 0,
        file_path=request.file_path,
        language=request.language,
        files_reviewed=report.files_reviewed,
        total_lines=report.total_lines,
        quality_score=report.quality_score,
        maintainability_index=report.maintainability_index,
        security_score=report.security_score,
        summary=report.summary,
        recommendations=report.recommendations,
        reviewed_at=report.reviewed_at,
        review_duration=report.review_duration,
        ai_models_used=report.ai_models_used
    )
    db.add(code_review)
    await db.flush()

    # Save issues
    from resoftai.models.ai_analysis import CodeIssueModel
    for issue in report.issues:
        db_issue = CodeIssueModel(
            review_id=code_review.id,
            issue_id=issue.id,
            severity=issue.severity.value,
            category=issue.category.value,
            title=issue.title,
            description=issue.description,
            file_path=issue.file_path,
            line_start=issue.line_start,
            line_end=issue.line_end,
            code_snippet=issue.code_snippet,
            suggestion=issue.suggestion,
            auto_fixable=1 if issue.auto_fixable else 0,
            fix_code=issue.fix_code,
            confidence=issue.confidence,
            references=issue.references
        )
        db.add(db_issue)

    await db.commit()
    await db.refresh(code_review)

    return CodeReviewResponse(
        id=code_review.id,
        project_id=code_review.project_id,
        file_path=code_review.file_path,
        language=code_review.language,
        files_reviewed=code_review.files_reviewed,
        total_lines=code_review.total_lines,
        quality_score=code_review.quality_score,
        maintainability_index=code_review.maintainability_index,
        security_score=code_review.security_score,
        summary=code_review.summary,
        recommendations=code_review.recommendations or [],
        issues_count=len(report.issues)
    )


@router.get("/code-review/{review_id}", response_model=CodeReviewResponse)
async def get_code_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific code review by ID."""
    result = await db.execute(
        select(CodeReview).where(CodeReview.id == review_id)
    )
    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Code review not found"
        )

    # Count issues
    from resoftai.models.ai_analysis import CodeIssueModel
    issues_result = await db.execute(
        select(CodeIssueModel).where(CodeIssueModel.review_id == review_id)
    )
    issues_count = len(issues_result.scalars().all())

    return CodeReviewResponse(
        id=review.id,
        project_id=review.project_id,
        file_path=review.file_path,
        language=review.language,
        files_reviewed=review.files_reviewed,
        total_lines=review.total_lines,
        quality_score=review.quality_score,
        maintainability_index=review.maintainability_index,
        security_score=review.security_score,
        summary=review.summary,
        recommendations=review.recommendations or [],
        issues_count=issues_count
    )


@router.get("/code-review/{review_id}/issues", response_model=List[CodeIssueResponse])
async def get_review_issues(
    review_id: int,
    severity: Optional[IssueSeverity] = None,
    category: Optional[IssueCategory] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get issues for a specific code review."""
    from resoftai.models.ai_analysis import CodeIssueModel

    query = select(CodeIssueModel).where(CodeIssueModel.review_id == review_id)

    if severity:
        query = query.where(CodeIssueModel.severity == severity.value)
    if category:
        query = query.where(CodeIssueModel.category == category.value)

    result = await db.execute(query)
    issues = result.scalars().all()

    return [
        CodeIssueResponse(
            id=issue.issue_id,
            severity=issue.severity,
            category=issue.category,
            title=issue.title,
            description=issue.description,
            file_path=issue.file_path,
            line_start=issue.line_start,
            line_end=issue.line_end,
            code_snippet=issue.code_snippet or "",
            suggestion=issue.suggestion or "",
            auto_fixable=bool(issue.auto_fixable),
            confidence=issue.confidence
        )
        for issue in issues
    ]


# ==================== Predictive Analysis ====================

@router.post("/predictive-analysis", response_model=PredictiveAnalysisResponse)
async def create_predictive_analysis(
    request: PredictiveAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform predictive analysis for a project.

    Provides progress prediction, risk assessment, effort estimation, and quality trends.
    """
    # Verify project exists and user has access
    project_result = await db.execute(
        select(Project).where(Project.id == request.project_id)
    )
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Initialize analyzer
    coordinator = get_coordinator()
    analyzer = PredictiveAnalyzer(coordinator)

    # Perform analysis
    insights = await analyzer.analyze_project(
        project_id=request.project_id,
        current_data=request.current_data
    )

    # Save to database
    analysis = PredictiveAnalysis(
        project_id=insights.project_id,
        analysis_timestamp=insights.analysis_timestamp,
        # Progress
        estimated_completion=insights.progress_prediction.estimated_completion,
        progress_confidence=insights.progress_prediction.confidence,
        current_progress=insights.progress_prediction.current_progress,
        projected_velocity=insights.progress_prediction.projected_velocity,
        remaining_tasks=insights.progress_prediction.remaining_tasks,
        bottlenecks=insights.progress_prediction.bottlenecks,
        acceleration_opportunities=insights.progress_prediction.acceleration_opportunities,
        # Risk
        risk_level=insights.risk_assessment.risk_level.value,
        risk_score=insights.risk_assessment.risk_score,
        identified_risks=insights.risk_assessment.identified_risks,
        mitigation_strategies=insights.risk_assessment.mitigation_strategies,
        risk_factors=insights.risk_assessment.risk_factors,
        # Effort
        estimated_hours=insights.effort_estimation.estimated_hours,
        estimated_days=insights.effort_estimation.estimated_days,
        confidence_range_min=insights.effort_estimation.confidence_range[0],
        confidence_range_max=insights.effort_estimation.confidence_range[1],
        complexity_score=insights.effort_estimation.complexity_score,
        similar_projects=insights.effort_estimation.similar_projects,
        assumptions=insights.effort_estimation.assumptions,
        # Quality
        current_quality=insights.quality_trend.current_quality,
        quality_trend=insights.quality_trend.trend.value,
        predicted_quality=insights.quality_trend.predicted_quality,
        quality_velocity=insights.quality_trend.quality_velocity,
        improvement_areas=insights.quality_trend.improvement_areas,
        regression_risks=insights.quality_trend.regression_risks,
        # Resources
        predicted_team_size=insights.resource_forecast.predicted_team_size,
        predicted_budget=insights.resource_forecast.predicted_budget,
        predicted_infrastructure=insights.resource_forecast.predicted_infrastructure,
        scaling_timeline=insights.resource_forecast.scaling_timeline,
        optimization_opportunities=insights.resource_forecast.optimization_opportunities,
        # Overall
        key_insights=insights.key_insights,
        recommended_actions=insights.recommended_actions,
        confidence_score=insights.confidence_score
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    return PredictiveAnalysisResponse(
        id=analysis.id,
        project_id=analysis.project_id,
        current_progress=analysis.current_progress,
        estimated_completion=str(analysis.estimated_completion),
        risk_level=analysis.risk_level,
        risk_score=analysis.risk_score,
        quality_trend=analysis.quality_trend,
        key_insights=analysis.key_insights or [],
        recommended_actions=analysis.recommended_actions or [],
        confidence_score=analysis.confidence_score
    )


@router.get("/predictive-analysis/project/{project_id}")
async def get_project_analyses(
    project_id: int,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all predictive analyses for a project."""
    result = await db.execute(
        select(PredictiveAnalysis)
        .where(PredictiveAnalysis.project_id == project_id)
        .order_by(desc(PredictiveAnalysis.analysis_timestamp))
        .limit(limit)
    )
    analyses = result.scalars().all()

    return [
        PredictiveAnalysisResponse(
            id=a.id,
            project_id=a.project_id,
            current_progress=a.current_progress,
            estimated_completion=str(a.estimated_completion),
            risk_level=a.risk_level,
            risk_score=a.risk_score,
            quality_trend=a.quality_trend,
            key_insights=a.key_insights or [],
            recommended_actions=a.recommended_actions or [],
            confidence_score=a.confidence_score
        )
        for a in analyses
    ]
