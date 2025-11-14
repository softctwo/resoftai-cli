"""Tests for linter service."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

from resoftai.core.linter_service import (
    LinterService,
    LinterType,
    IssueSeverity,
    LintIssue,
    LintResult,
    CodeQualityResult,
    get_linter_service,
)


class TestLinterService:
    """Test cases for LinterService."""

    @pytest.fixture
    def linter_service(self) -> LinterService:
        """Create linter service instance."""
        return LinterService()

    def test_singleton_instance(self) -> None:
        """Test singleton pattern."""
        service1 = get_linter_service()
        service2 = get_linter_service()
        assert service1 is service2

    def test_supported_linters(self, linter_service: LinterService) -> None:
        """Test supported linters mapping."""
        assert "python" in linter_service.supported_linters
        assert "javascript" in linter_service.supported_linters
        assert "typescript" in linter_service.supported_linters

        assert LinterType.PYLINT in linter_service.supported_linters["python"]
        assert LinterType.MYPY in linter_service.supported_linters["python"]
        assert LinterType.ESLINT in linter_service.supported_linters["javascript"]

    @pytest.mark.asyncio
    async def test_create_temp_file(self, linter_service: LinterService) -> None:
        """Test temporary file creation."""
        import os

        code = "print('hello')"
        temp_file = await linter_service._create_temp_file(code, "python", "test.py")

        try:
            assert os.path.exists(temp_file)
            assert temp_file.endswith(".py")

            with open(temp_file, 'r') as f:
                content = f.read()
            assert content == code
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_map_pylint_severity(self, linter_service: LinterService) -> None:
        """Test pylint severity mapping."""
        assert linter_service._map_pylint_severity("error") == IssueSeverity.ERROR
        assert linter_service._map_pylint_severity("warning") == IssueSeverity.WARNING
        assert linter_service._map_pylint_severity("convention") == IssueSeverity.CONVENTION
        assert linter_service._map_pylint_severity("refactor") == IssueSeverity.REFACTOR
        assert linter_service._map_pylint_severity("info") == IssueSeverity.INFO

    def test_map_eslint_severity(self, linter_service: LinterService) -> None:
        """Test eslint severity mapping."""
        assert linter_service._map_eslint_severity(2) == IssueSeverity.ERROR
        assert linter_service._map_eslint_severity(1) == IssueSeverity.WARNING
        assert linter_service._map_eslint_severity(0) == IssueSeverity.INFO

    def test_aggregate_results(self, linter_service: LinterService) -> None:
        """Test result aggregation."""
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

        aggregated = linter_service._aggregate_results(
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
    async def test_run_pylint_not_installed(self, linter_service: LinterService) -> None:
        """Test pylint when not installed."""
        with patch("asyncio.create_subprocess_exec", side_effect=FileNotFoundError()):
            result = await linter_service._run_pylint("/tmp/test.py")

            assert result.linter == LinterType.PYLINT
            assert not result.success
            assert "not installed" in result.error_message

    @pytest.mark.asyncio
    async def test_run_mypy_not_installed(self, linter_service: LinterService) -> None:
        """Test mypy when not installed."""
        with patch("asyncio.create_subprocess_exec", side_effect=FileNotFoundError()):
            result = await linter_service._run_mypy("/tmp/test.py")

            assert result.linter == LinterType.MYPY
            assert not result.success
            assert "not installed" in result.error_message

    @pytest.mark.asyncio
    async def test_run_eslint_not_installed(self, linter_service: LinterService) -> None:
        """Test eslint when not installed."""
        with patch("asyncio.create_subprocess_exec", side_effect=FileNotFoundError()):
            result = await linter_service._run_eslint("/tmp/test.js")

            assert result.linter == LinterType.ESLINT
            assert not result.success
            assert "not installed" in result.error_message

    @pytest.mark.asyncio
    async def test_run_pylint_success(self, linter_service: LinterService) -> None:
        """Test successful pylint execution."""
        mock_output = b'[{"type": "error", "message": "Test error", "line": 1, "column": 0, "message-id": "E0001"}]'

        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=(mock_output, b""))
        mock_process.returncode = 0

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await linter_service._run_pylint("/tmp/test.py")

            assert result.linter == LinterType.PYLINT
            assert result.success
            assert len(result.issues) == 1
            assert result.issues[0].severity == IssueSeverity.ERROR
            assert result.issues[0].message == "Test error"

    @pytest.mark.asyncio
    async def test_run_mypy_success(self, linter_service: LinterService) -> None:
        """Test successful mypy execution."""
        mock_output = b"/tmp/test.py:10:5: error: Test type error"

        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=(mock_output, b""))
        mock_process.returncode = 1

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await linter_service._run_mypy("/tmp/test.py")

            assert result.linter == LinterType.MYPY
            assert result.success
            assert len(result.issues) == 1
            assert result.issues[0].line == 10
            assert result.issues[0].column == 5

    @pytest.mark.asyncio
    async def test_check_code_python(self, linter_service: LinterService) -> None:
        """Test code checking for Python."""
        code = "def foo():\n    pass"

        # Mock both linters to return empty results
        mock_pylint = LintResult(LinterType.PYLINT, True, [], execution_time=0.1)
        mock_mypy = LintResult(LinterType.MYPY, True, [], execution_time=0.1)

        with patch.object(linter_service, "_run_pylint", return_value=mock_pylint), \
             patch.object(linter_service, "_run_mypy", return_value=mock_mypy), \
             patch.object(linter_service, "_create_temp_file", return_value="/tmp/test.py"):

            result = await linter_service.check_code(code, "python")

            assert result.language == "python"
            assert result.total_issues == 0
            assert result.overall_score == 100.0
            assert len(result.linter_results) == 2

    @pytest.mark.asyncio
    async def test_check_code_javascript(self, linter_service: LinterService) -> None:
        """Test code checking for JavaScript."""
        code = "const x = 1;"

        mock_eslint = LintResult(LinterType.ESLINT, True, [], execution_time=0.1)

        with patch.object(linter_service, "_run_eslint", return_value=mock_eslint), \
             patch.object(linter_service, "_create_temp_file", return_value="/tmp/test.js"):

            result = await linter_service.check_code(code, "javascript")

            assert result.language == "javascript"
            assert result.total_issues == 0
            assert len(result.linter_results) == 1

    @pytest.mark.asyncio
    async def test_check_code_with_specific_linters(self, linter_service: LinterService) -> None:
        """Test code checking with specific linters."""
        code = "def foo():\n    pass"

        mock_pylint = LintResult(LinterType.PYLINT, True, [], execution_time=0.1)

        with patch.object(linter_service, "_run_pylint", return_value=mock_pylint), \
             patch.object(linter_service, "_create_temp_file", return_value="/tmp/test.py"):

            result = await linter_service.check_code(
                code, "python", linters=[LinterType.PYLINT]
            )

            assert len(result.linter_results) == 1
            assert result.linter_results[0].linter == LinterType.PYLINT

    @pytest.mark.asyncio
    async def test_check_code_score_calculation(self, linter_service: LinterService) -> None:
        """Test quality score calculation."""
        issues = [
            LintIssue(IssueSeverity.ERROR, "Error", 1),
            LintIssue(IssueSeverity.WARNING, "Warning", 2),
            LintIssue(IssueSeverity.INFO, "Info", 3),
        ]

        mock_result = LintResult(LinterType.PYLINT, True, issues, execution_time=0.1)

        with patch.object(linter_service, "_run_pylint", return_value=mock_result), \
             patch.object(linter_service, "_run_mypy", return_value=LintResult(LinterType.MYPY, True, [])), \
             patch.object(linter_service, "_create_temp_file", return_value="/tmp/test.py"):

            result = await linter_service.check_code("code", "python")

            # Score should be reduced: 100 - (1*10 + 1*2 + 1*0.5) = 87.5
            assert result.overall_score == 87.5
            assert result.errors == 1
            assert result.warnings == 1
            assert result.info == 1
