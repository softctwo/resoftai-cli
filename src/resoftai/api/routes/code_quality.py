"""Code quality check API routes."""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from resoftai.core.linter_service import (
    get_linter_service,
    LinterType,
    IssueSeverity,
    LintIssue,
    LintResult,
    CodeQualityResult,
)

router = APIRouter(prefix="/code-quality", tags=["code-quality"])


# Request/Response Models
class LintIssueResponse(BaseModel):
    """Lint issue response model."""
    severity: str
    message: str
    line: int
    column: int
    rule_id: Optional[str] = None
    source: Optional[str] = None

    @classmethod
    def from_lint_issue(cls, issue: LintIssue) -> "LintIssueResponse":
        """Convert LintIssue to response model."""
        return cls(
            severity=issue.severity.value,
            message=issue.message,
            line=issue.line,
            column=issue.column,
            rule_id=issue.rule_id,
            source=issue.source,
        )


class LintResultResponse(BaseModel):
    """Lint result response model."""
    linter: str
    success: bool
    issues: List[LintIssueResponse]
    error_message: Optional[str] = None
    execution_time: float

    @classmethod
    def from_lint_result(cls, result: LintResult) -> "LintResultResponse":
        """Convert LintResult to response model."""
        return cls(
            linter=result.linter.value,
            success=result.success,
            issues=[LintIssueResponse.from_lint_issue(i) for i in result.issues],
            error_message=result.error_message,
            execution_time=result.execution_time,
        )


class CodeQualityResponse(BaseModel):
    """Code quality response model."""
    file_path: str
    language: str
    total_issues: int
    errors: int
    warnings: int
    info: int
    overall_score: float
    linter_results: List[LintResultResponse]

    @classmethod
    def from_quality_result(cls, result: CodeQualityResult) -> "CodeQualityResponse":
        """Convert CodeQualityResult to response model."""
        return cls(
            file_path=result.file_path,
            language=result.language,
            total_issues=result.total_issues,
            errors=result.errors,
            warnings=result.warnings,
            info=result.info,
            overall_score=result.overall_score,
            linter_results=[
                LintResultResponse.from_lint_result(r) for r in result.linter_results
            ],
        )


class CodeCheckRequest(BaseModel):
    """Code quality check request."""
    code: str = Field(..., description="Source code to check")
    language: str = Field(..., description="Programming language (python, javascript, typescript)")
    filename: Optional[str] = Field(None, description="Optional filename for context")
    linters: Optional[List[str]] = Field(
        None,
        description="Specific linters to use (pylint, mypy, eslint). Defaults to all for language."
    )


@router.post("/check", response_model=CodeQualityResponse)
async def check_code_quality(request: CodeCheckRequest) -> CodeQualityResponse:
    """
    Check code quality using appropriate linters.

    Supports:
    - Python: pylint, mypy
    - JavaScript/TypeScript: eslint

    Args:
        request: Code check request with source code and options

    Returns:
        Code quality analysis results

    Raises:
        HTTPException: If language not supported or validation fails
    """
    # Validate language
    supported_languages = ["python", "javascript", "typescript"]
    if request.language.lower() not in supported_languages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language '{request.language}' not supported. Supported: {supported_languages}"
        )

    # Validate and convert linters
    linters = None
    if request.linters:
        try:
            linters = [LinterType(linter.lower()) for linter in request.linters]
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid linter specified: {e}"
            )

    # Run code quality check
    try:
        linter_service = get_linter_service()
        result = await linter_service.check_code(
            code=request.code,
            language=request.language,
            filename=request.filename,
            linters=linters,
        )

        return CodeQualityResponse.from_quality_result(result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code quality check failed: {str(e)}"
        )


@router.get("/linters", response_model=dict)
async def get_supported_linters() -> dict:
    """
    Get list of supported linters for each language.

    Returns:
        Dictionary mapping languages to their supported linters
    """
    linter_service = get_linter_service()
    return {
        language: [linter.value for linter in linters]
        for language, linters in linter_service.supported_linters.items()
    }


@router.get("/health", response_model=dict)
async def health_check() -> dict:
    """
    Check availability of linting tools.

    Returns:
        Status of each linting tool
    """
    import subprocess
    import asyncio

    async def check_tool(tool: str) -> bool:
        """Check if a tool is available."""
        try:
            process = await asyncio.create_subprocess_exec(
                tool,
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await process.communicate()
            return process.returncode == 0
        except FileNotFoundError:
            return False
        except Exception:
            return False

    # Check all tools
    tools = {
        "pylint": await check_tool("pylint"),
        "mypy": await check_tool("mypy"),
        "eslint": await check_tool("eslint"),
    }

    all_available = all(tools.values())

    return {
        "status": "healthy" if all_available else "degraded",
        "tools": tools,
        "message": "All linters available" if all_available else "Some linters unavailable"
    }
