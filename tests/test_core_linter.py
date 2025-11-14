"""Tests for core linter service."""
import pytest
from resoftai.core.linter_service import (
    LinterType,
    IssueSeverity,
    LintIssue,
    LintResult,
    CodeQualityResult,
    LinterService
)


class TestLinterType:
    """Test LinterType enum."""

    def test_linter_types(self):
        """Test all linter types are available."""
        assert LinterType.PYLINT == "pylint"
        assert LinterType.MYPY == "mypy"
        assert LinterType.ESLINT == "eslint"

    def test_linter_type_is_string(self):
        """Test that linter types are strings."""
        assert isinstance(LinterType.PYLINT, str)
        assert isinstance(LinterType.MYPY.value, str)


class TestIssueSeverity:
    """Test IssueSeverity enum."""

    def test_severity_levels(self):
        """Test all severity levels are available."""
        assert IssueSeverity.ERROR == "error"
        assert IssueSeverity.WARNING == "warning"
        assert IssueSeverity.INFO == "info"
        assert IssueSeverity.CONVENTION == "convention"
        assert IssueSeverity.REFACTOR == "refactor"

    def test_severity_is_string(self):
        """Test that severity levels are strings."""
        assert isinstance(IssueSeverity.ERROR, str)
        assert isinstance(IssueSeverity.WARNING.value, str)


class TestLintIssue:
    """Test LintIssue dataclass."""

    def test_create_issue(self):
        """Test creating a lint issue."""
        issue = LintIssue(
            severity=IssueSeverity.ERROR,
            message="Missing semicolon",
            line=10,
            column=5,
            rule_id="E0001",
            source="pylint"
        )
        assert issue.severity == IssueSeverity.ERROR
        assert issue.message == "Missing semicolon"
        assert issue.line == 10
        assert issue.column == 5
        assert issue.rule_id == "E0001"
        assert issue.source == "pylint"

    def test_create_issue_with_defaults(self):
        """Test creating issue with default values."""
        issue = LintIssue(
            severity=IssueSeverity.WARNING,
            message="Unused variable",
            line=5
        )
        assert issue.severity == IssueSeverity.WARNING
        assert issue.message == "Unused variable"
        assert issue.line == 5
        assert issue.column == 0  # default
        assert issue.rule_id is None  # default
        assert issue.source is None  # default

    def test_issue_with_different_severities(self):
        """Test issues with different severity levels."""
        severities = [
            IssueSeverity.ERROR,
            IssueSeverity.WARNING,
            IssueSeverity.INFO,
            IssueSeverity.CONVENTION,
            IssueSeverity.REFACTOR
        ]

        for severity in severities:
            issue = LintIssue(
                severity=severity,
                message="Test message",
                line=1
            )
            assert issue.severity == severity


class TestLintResult:
    """Test LintResult dataclass."""

    def test_create_successful_result(self):
        """Test creating a successful lint result."""
        result = LintResult(
            linter=LinterType.PYLINT,
            success=True,
            issues=[
                LintIssue(
                    severity=IssueSeverity.WARNING,
                    message="Line too long",
                    line=1
                )
            ],
            execution_time=0.5,
            metadata={"score": 9.5}
        )
        assert result.linter == LinterType.PYLINT
        assert result.success is True
        assert len(result.issues) == 1
        assert result.execution_time == 0.5
        assert result.metadata["score"] == 9.5
        assert result.error_message is None

    def test_create_failed_result(self):
        """Test creating a failed lint result."""
        result = LintResult(
            linter=LinterType.MYPY,
            success=False,
            error_message="Linter not installed",
            execution_time=0.0
        )
        assert result.linter == LinterType.MYPY
        assert result.success is False
        assert result.error_message == "Linter not installed"
        assert len(result.issues) == 0  # default empty list

    def test_result_with_no_issues(self):
        """Test result with no issues (clean code)."""
        result = LintResult(
            linter=LinterType.ESLINT,
            success=True,
            issues=[],
            execution_time=0.3
        )
        assert result.success is True
        assert len(result.issues) == 0
        assert result.error_message is None

    def test_result_with_multiple_issues(self):
        """Test result with multiple issues."""
        issues = [
            LintIssue(IssueSeverity.ERROR, "Error 1", 1),
            LintIssue(IssueSeverity.WARNING, "Warning 1", 2),
            LintIssue(IssueSeverity.INFO, "Info 1", 3)
        ]
        result = LintResult(
            linter=LinterType.PYLINT,
            success=True,
            issues=issues
        )
        assert len(result.issues) == 3
        assert result.issues[0].severity == IssueSeverity.ERROR
        assert result.issues[1].severity == IssueSeverity.WARNING
        assert result.issues[2].severity == IssueSeverity.INFO


class TestCodeQualityResult:
    """Test CodeQualityResult dataclass."""

    def test_create_quality_result(self):
        """Test creating a code quality result."""
        result = CodeQualityResult(
            file_path="/path/to/file.py",
            language="python",
            total_issues=5,
            errors=2,
            warnings=2,
            info=1,
            overall_score=85.0
        )
        assert result.file_path == "/path/to/file.py"
        assert result.language == "python"
        assert result.total_issues == 5
        assert result.errors == 2
        assert result.warnings == 2
        assert result.info == 1
        assert result.overall_score == 85.0
        assert len(result.linter_results) == 0  # default

    def test_quality_result_with_linter_results(self):
        """Test quality result with linter results."""
        lint_result1 = LintResult(
            linter=LinterType.PYLINT,
            success=True,
            issues=[LintIssue(IssueSeverity.WARNING, "Test", 1)]
        )
        lint_result2 = LintResult(
            linter=LinterType.MYPY,
            success=True,
            issues=[LintIssue(IssueSeverity.ERROR, "Test", 2)]
        )

        quality_result = CodeQualityResult(
            file_path="test.py",
            language="python",
            total_issues=2,
            errors=1,
            warnings=1,
            info=0,
            linter_results=[lint_result1, lint_result2]
        )

        assert len(quality_result.linter_results) == 2
        assert quality_result.linter_results[0].linter == LinterType.PYLINT
        assert quality_result.linter_results[1].linter == LinterType.MYPY

    def test_perfect_score(self):
        """Test quality result with perfect score."""
        result = CodeQualityResult(
            file_path="perfect.py",
            language="python",
            total_issues=0,
            errors=0,
            warnings=0,
            info=0,
            overall_score=100.0
        )
        assert result.total_issues == 0
        assert result.overall_score == 100.0

    def test_low_score(self):
        """Test quality result with low score."""
        result = CodeQualityResult(
            file_path="bad.py",
            language="python",
            total_issues=50,
            errors=30,
            warnings=15,
            info=5,
            overall_score=25.5
        )
        assert result.total_issues == 50
        assert result.errors == 30
        assert result.overall_score == 25.5


class TestLinterService:
    """Test LinterService class."""

    def test_initialization(self):
        """Test linter service initialization."""
        service = LinterService()
        assert isinstance(service.supported_linters, dict)
        assert "python" in service.supported_linters
        assert "javascript" in service.supported_linters
        assert "typescript" in service.supported_linters

    def test_supported_linters_python(self):
        """Test Python linters are configured."""
        service = LinterService()
        python_linters = service.supported_linters["python"]
        assert LinterType.PYLINT in python_linters
        assert LinterType.MYPY in python_linters
        assert len(python_linters) == 2

    def test_supported_linters_javascript(self):
        """Test JavaScript linters are configured."""
        service = LinterService()
        js_linters = service.supported_linters["javascript"]
        assert LinterType.ESLINT in js_linters
        assert len(js_linters) == 1

    def test_supported_linters_typescript(self):
        """Test TypeScript linters are configured."""
        service = LinterService()
        ts_linters = service.supported_linters["typescript"]
        assert LinterType.ESLINT in ts_linters
        assert len(ts_linters) == 1

    def test_get_linters_for_language(self):
        """Test getting linters for a specific language."""
        service = LinterService()

        # Test each language
        assert "python" in service.supported_linters
        assert "javascript" in service.supported_linters
        assert "typescript" in service.supported_linters

        # Python should have 2 linters
        assert len(service.supported_linters["python"]) == 2

        # JS/TS should have 1 linter each
        assert len(service.supported_linters["javascript"]) == 1
        assert len(service.supported_linters["typescript"]) == 1


class TestLintIssueIntegration:
    """Integration tests for lint issues."""

    def test_multiple_issues_from_different_sources(self):
        """Test handling multiple issues from different linters."""
        pylint_issue = LintIssue(
            severity=IssueSeverity.ERROR,
            message="Missing docstring",
            line=1,
            rule_id="C0111",
            source="pylint"
        )

        mypy_issue = LintIssue(
            severity=IssueSeverity.ERROR,
            message="Type mismatch",
            line=5,
            column=10,
            rule_id="type-error",
            source="mypy"
        )

        eslint_issue = LintIssue(
            severity=IssueSeverity.WARNING,
            message="Missing semicolon",
            line=3,
            column=20,
            rule_id="semi",
            source="eslint"
        )

        issues = [pylint_issue, mypy_issue, eslint_issue]

        # Group by severity
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        warnings = [i for i in issues if i.severity == IssueSeverity.WARNING]

        assert len(errors) == 2
        assert len(warnings) == 1

        # Group by source
        pylint_issues = [i for i in issues if i.source == "pylint"]
        mypy_issues = [i for i in issues if i.source == "mypy"]
        eslint_issues = [i for i in issues if i.source == "eslint"]

        assert len(pylint_issues) == 1
        assert len(mypy_issues) == 1
        assert len(eslint_issues) == 1

    def test_lint_result_aggregation(self):
        """Test aggregating lint results."""
        # Create multiple lint results
        pylint_result = LintResult(
            linter=LinterType.PYLINT,
            success=True,
            issues=[
                LintIssue(IssueSeverity.ERROR, "Error 1", 1),
                LintIssue(IssueSeverity.WARNING, "Warning 1", 2)
            ]
        )

        mypy_result = LintResult(
            linter=LinterType.MYPY,
            success=True,
            issues=[
                LintIssue(IssueSeverity.ERROR, "Error 2", 3)
            ]
        )

        # Aggregate all issues
        all_issues = pylint_result.issues + mypy_result.issues
        total_issues = len(all_issues)
        errors = sum(1 for i in all_issues if i.severity == IssueSeverity.ERROR)
        warnings = sum(1 for i in all_issues if i.severity == IssueSeverity.WARNING)

        assert total_issues == 3
        assert errors == 2
        assert warnings == 1

        # Create quality result
        quality_result = CodeQualityResult(
            file_path="test.py",
            language="python",
            total_issues=total_issues,
            errors=errors,
            warnings=warnings,
            info=0,
            linter_results=[pylint_result, mypy_result]
        )

        assert quality_result.total_issues == 3
        assert quality_result.errors == 2
        assert quality_result.warnings == 1
        assert len(quality_result.linter_results) == 2
