"""Standalone tests for linter service (no API dependencies)."""
import pytest
from unittest.mock import patch, AsyncMock
import asyncio

from resoftai.core.linter_service import (
    LinterService,
    LinterType,
    IssueSeverity,
    LintIssue,
    LintResult,
    get_linter_service,
)


def test_singleton_instance() -> None:
    """Test singleton pattern."""
    service1 = get_linter_service()
    service2 = get_linter_service()
    assert service1 is service2


def test_supported_linters() -> None:
    """Test supported linters mapping."""
    service = LinterService()
    assert "python" in service.supported_linters
    assert "javascript" in service.supported_linters
    assert "typescript" in service.supported_linters

    assert LinterType.PYLINT in service.supported_linters["python"]
    assert LinterType.MYPY in service.supported_linters["python"]
    assert LinterType.ESLINT in service.supported_linters["javascript"]


def test_map_pylint_severity() -> None:
    """Test pylint severity mapping."""
    service = LinterService()
    assert service._map_pylint_severity("error") == IssueSeverity.ERROR
    assert service._map_pylint_severity("warning") == IssueSeverity.WARNING
    assert service._map_pylint_severity("convention") == IssueSeverity.CONVENTION
    assert service._map_pylint_severity("refactor") == IssueSeverity.REFACTOR
    assert service._map_pylint_severity("info") == IssueSeverity.INFO


def test_map_eslint_severity() -> None:
    """Test eslint severity mapping."""
    service = LinterService()
    assert service._map_eslint_severity(2) == IssueSeverity.ERROR
    assert service._map_eslint_severity(1) == IssueSeverity.WARNING
    assert service._map_eslint_severity(0) == IssueSeverity.INFO


def test_aggregate_results() -> None:
    """Test result aggregation."""
    service = LinterService()
    issues = [
        LintIssue(IssueSeverity.ERROR, "Error 1", 1, source="pylint"),
        LintIssue(IssueSeverity.ERROR, "Error 2", 2, source="mypy"),
        LintIssue(IssueSeverity.WARNING, "Warning 1", 3, source="pylint"),
        LintIssue(IssueSeverity.INFO, "Info 1", 4, source="pylint"),
    ]

    result1 = LintResult(
        linter=LinterType.PYLINT,
        success=True,
        issues=issues[:3],
        execution_time=0.5
    )

    result2 = LintResult(
        linter=LinterType.MYPY,
        success=True,
        issues=issues[3:],
        execution_time=0.3
    )

    aggregated = service._aggregate_results(
        file_path="test.py",
        language="python",
        linter_results=[result1, result2]
    )

    assert aggregated.total_issues == 4
    assert aggregated.errors == 2
    assert aggregated.warnings == 1
    assert aggregated.info == 1
    assert aggregated.overall_score < 100.0
    assert len(aggregated.linter_results) == 2


@pytest.mark.asyncio
async def test_create_temp_file() -> None:
    """Test temporary file creation."""
    import os

    service = LinterService()
    code = "print('hello')"
    temp_file = await service._create_temp_file(code, "python", "test.py")

    try:
        assert os.path.exists(temp_file)
        assert temp_file.endswith(".py")

        with open(temp_file, 'r') as f:
            content = f.read()
        assert content == code
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@pytest.mark.asyncio
async def test_run_pylint_not_installed() -> None:
    """Test pylint when not installed."""
    service = LinterService()
    with patch("asyncio.create_subprocess_exec", side_effect=FileNotFoundError()):
        result = await service._run_pylint("/tmp/test.py")

        assert result.linter == LinterType.PYLINT
        assert not result.success
        assert "not installed" in result.error_message


@pytest.mark.asyncio
async def test_check_code_score_calculation() -> None:
    """Test quality score calculation."""
    service = LinterService()
    issues = [
        LintIssue(IssueSeverity.ERROR, "Error", 1),
        LintIssue(IssueSeverity.WARNING, "Warning", 2),
        LintIssue(IssueSeverity.INFO, "Info", 3),
    ]

    mock_result = LintResult(LinterType.PYLINT, True, issues, execution_time=0.1)

    with patch.object(service, "_run_pylint", return_value=mock_result), \
         patch.object(service, "_run_mypy", return_value=LintResult(LinterType.MYPY, True, [])), \
         patch.object(service, "_create_temp_file", return_value="/tmp/test.py"):

        result = await service.check_code("code", "python")

        # Score should be reduced: 100 - (1*10 + 1*2 + 1*0.5) = 87.5
        assert result.overall_score == 87.5
        assert result.errors == 1
        assert result.warnings == 1
        assert result.info == 1
