"""
API routes for advanced AI features.

Includes endpoints for:
- Multi-model collaboration
- Automatic code review
- Intelligent bug prediction
- Technical debt analysis
- Automatic refactoring suggestions
- Automated test generation
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from resoftai.db import get_db
from resoftai.auth.dependencies import get_current_active_user
from resoftai.models.user import User
from resoftai.llm.base import LLMConfig, ModelProvider
from resoftai.crud.llm_config import get_active_llm_config

# Import AI modules
from resoftai.ai import (
    get_bug_predictor,
    get_technical_debt_analyzer,
    get_refactoring_analyzer,
    get_test_generator,
    create_default_collaborator,
    TestFramework
)

router = APIRouter(prefix="/ai", tags=["ai-features"])
logger = logging.getLogger(__name__)


# Request/Response Models
class CodeAnalysisRequest(BaseModel):
    """Request for code analysis."""
    code: str = Field(..., description="Source code to analyze")
    language: str = Field(..., description="Programming language")
    filename: Optional[str] = Field(None, description="Optional filename")


class BugPredictionResponse(BaseModel):
    """Response from bug prediction."""
    total_predictions: int
    risk_score: float
    predictions: List[dict]
    report_text: str


class TechnicalDebtResponse(BaseModel):
    """Response from technical debt analysis."""
    total_items: int
    total_hours: float
    debt_score: float
    items: List[dict]
    priority_list: List[dict]
    report_text: str


class RefactoringResponse(BaseModel):
    """Response from refactoring analysis."""
    total_suggestions: int
    suggestions: List[dict]
    high_priority: List[dict]
    report_text: str


class TestGenerationRequest(BaseModel):
    """Request for test generation."""
    code: str = Field(..., description="Source code to generate tests for")
    language: str = Field(..., description="Programming language")
    framework: str = Field(default="pytest", description="Test framework")
    filename: Optional[str] = Field(None, description="Optional filename")
    use_ai: bool = Field(default=False, description="Use AI for test generation")


class TestGenerationResponse(BaseModel):
    """Response from test generation."""
    test_file: str
    tests_generated: int
    coverage_estimate: float
    test_code: str
    report: dict


class CodeReviewRequest(BaseModel):
    """Request for multi-model code review."""
    code: str = Field(..., description="Source code to review")
    language: str = Field(..., description="Programming language")
    filename: Optional[str] = Field(None, description="Optional filename")


class CodeReviewResponse(BaseModel):
    """Response from code review."""
    review: str
    consensus_score: float
    individual_reviews: List[dict]
    execution_time: float


# Endpoints
@router.post("/predict-bugs", response_model=BugPredictionResponse)
async def predict_bugs(
    request: CodeAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Predict potential bugs in code using intelligent analysis.

    Analyzes code for common bug patterns and provides predictions with
    severity levels and fix suggestions.
    """
    try:
        predictor = get_bug_predictor()

        report = await predictor.predict_bugs(
            code=request.code,
            language=request.language,
            filename=request.filename,
            use_ai=False
        )

        # Convert predictions to dictionaries
        predictions = [
            {
                'severity': pred.severity.value,
                'category': pred.category.value,
                'confidence': pred.confidence,
                'line_number': pred.line_number,
                'message': pred.message,
                'explanation': pred.explanation,
                'fix_suggestion': pred.fix_suggestion
            }
            for pred in report.predictions
        ]

        return BugPredictionResponse(
            total_predictions=len(report.predictions),
            risk_score=report.risk_score,
            predictions=predictions,
            report_text=predictor.format_report(report)
        )

    except Exception as e:
        logger.error(f"Bug prediction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Bug prediction failed: {str(e)}")


@router.post("/analyze-debt", response_model=TechnicalDebtResponse)
async def analyze_technical_debt(
    request: CodeAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze technical debt in code.

    Identifies various forms of technical debt and provides quantified
    assessments to help prioritize refactoring efforts.
    """
    try:
        analyzer = get_technical_debt_analyzer()

        report = await analyzer.analyze(
            code=request.code,
            language=request.language,
            filename=request.filename
        )

        # Convert items to dictionaries
        items = [
            {
                'type': item.debt_type.value,
                'severity': item.severity.value,
                'title': item.title,
                'description': item.description,
                'location': item.location,
                'estimated_hours': item.estimated_effort_hours,
                'impact_score': item.impact_score
            }
            for item in report.items
        ]

        priority_items = [
            {
                'type': item.debt_type.value,
                'severity': item.severity.value,
                'title': item.title,
                'description': item.description,
                'location': item.location
            }
            for item in report.priority_list
        ]

        return TechnicalDebtResponse(
            total_items=report.total_items,
            total_hours=report.total_estimated_hours,
            debt_score=report.total_debt_score,
            items=items,
            priority_list=priority_items,
            report_text=analyzer.format_report(report)
        )

    except Exception as e:
        logger.error(f"Technical debt analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Technical debt analysis failed: {str(e)}")


@router.post("/suggest-refactoring", response_model=RefactoringResponse)
async def suggest_refactoring(
    request: CodeAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate automatic refactoring suggestions.

    Analyzes code and provides actionable refactoring suggestions
    to improve code quality, maintainability, and performance.
    """
    try:
        analyzer = get_refactoring_analyzer()

        report = await analyzer.analyze(
            code=request.code,
            language=request.language,
            filename=request.filename
        )

        # Convert suggestions to dictionaries
        suggestions = [
            {
                'type': sug.refactoring_type.value,
                'title': sug.title,
                'description': sug.description,
                'location': sug.location,
                'current_code': sug.current_code,
                'suggested_code': sug.suggested_code,
                'rationale': sug.rationale,
                'effort': sug.effort,
                'benefits': sug.benefits
            }
            for sug in report.suggestions
        ]

        high_priority = [
            {
                'type': sug.refactoring_type.value,
                'title': sug.title,
                'location': sug.location,
                'effort': sug.effort
            }
            for sug in report.high_priority
        ]

        return RefactoringResponse(
            total_suggestions=report.total_suggestions,
            suggestions=suggestions,
            high_priority=high_priority,
            report_text=analyzer.format_report(report)
        )

    except Exception as e:
        logger.error(f"Refactoring analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Refactoring analysis failed: {str(e)}")


@router.post("/generate-tests", response_model=TestGenerationResponse)
async def generate_tests(
    request: TestGenerationRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Automatically generate unit tests for code.

    Creates comprehensive test cases using templates and optional AI assistance
    for better coverage and quality.
    """
    try:
        # Get LLM provider if AI is enabled
        llm_provider = None
        if request.use_ai:
            llm_config_model = await get_active_llm_config(db, current_user.id)
            if llm_config_model:
                from resoftai.llm.factory import LLMFactory
                from resoftai.llm.base import LLMConfig, ModelProvider as MP

                llm_config = LLMConfig(
                    provider=MP(llm_config_model.provider),
                    api_key=llm_config_model.api_key,
                    model_name=llm_config_model.model
                )
                llm_provider = LLMFactory.create(llm_config)

        generator = get_test_generator(llm_provider)

        # Parse framework
        try:
            framework = TestFramework(request.framework.lower())
        except ValueError:
            framework = TestFramework.PYTEST

        report = await generator.generate_tests(
            code=request.code,
            language=request.language,
            framework=framework,
            filename=request.filename,
            use_ai=request.use_ai
        )

        return TestGenerationResponse(
            test_file=report.test_file,
            tests_generated=report.tests_generated,
            coverage_estimate=report.coverage_estimate,
            test_code=report.full_test_code,
            report={
                'source_file': report.source_file,
                'functions_analyzed': report.functions_analyzed,
                'framework': report.framework.value,
                'generation_time': report.generation_time
            }
        )

    except Exception as e:
        logger.error(f"Test generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Test generation failed: {str(e)}")


@router.post("/review-code", response_model=CodeReviewResponse)
async def review_code_multi_model(
    request: CodeReviewRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform multi-model code review.

    Uses multiple AI models collaboratively to provide comprehensive
    code review with high reliability through consensus.
    """
    try:
        # Get active LLM configuration
        llm_config_model = await get_active_llm_config(db, current_user.id)
        if not llm_config_model:
            raise HTTPException(status_code=400, detail="No active LLM configuration found")

        from resoftai.llm.base import LLMConfig, ModelProvider as MP

        llm_config = LLMConfig(
            provider=MP(llm_config_model.provider),
            api_key=llm_config_model.api_key,
            model_name=llm_config_model.model
        )

        # Create multi-model collaborator
        collaborator = create_default_collaborator(llm_config)

        from resoftai.ai import MultiModelCodeReviewer

        reviewer = MultiModelCodeReviewer(collaborator)

        result = await reviewer.review_code(
            code=request.code,
            language=request.language,
            filename=request.filename
        )

        return CodeReviewResponse(
            review=result['review'],
            consensus_score=result['consensus_score'] or 0.0,
            individual_reviews=result['individual_reviews'],
            execution_time=result['execution_time']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Code review failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Code review failed: {str(e)}")


@router.get("/features")
async def get_available_features(
    current_user: User = Depends(get_current_active_user)
):
    """Get list of available AI features."""
    return {
        "available_features": [
            {
                "name": "Bug Prediction",
                "endpoint": "/ai/predict-bugs",
                "description": "Predict potential bugs using intelligent analysis"
            },
            {
                "name": "Technical Debt Analysis",
                "endpoint": "/ai/analyze-debt",
                "description": "Identify and quantify technical debt"
            },
            {
                "name": "Refactoring Suggestions",
                "endpoint": "/ai/suggest-refactoring",
                "description": "Get automatic refactoring recommendations"
            },
            {
                "name": "Test Generation",
                "endpoint": "/ai/generate-tests",
                "description": "Automatically generate unit tests"
            },
            {
                "name": "Multi-Model Code Review",
                "endpoint": "/ai/review-code",
                "description": "Comprehensive code review using multiple AI models"
            }
        ],
        "supported_languages": ["python", "javascript", "typescript", "java", "go"],
        "test_frameworks": ["pytest", "unittest", "jest", "mocha", "junit", "gotest"]
    }
