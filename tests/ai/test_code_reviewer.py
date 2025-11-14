"""Tests for intelligent code reviewer."""
import pytest
from unittest.mock import Mock, AsyncMock

from resoftai.ai.code_reviewer import (
    IntelligentCodeReviewer,
    IssueSeverity,
    IssueCategory
)
from resoftai.ai.multi_model_coordinator import MultiModelCoordinator


class TestIntelligentCodeReviewer:
    """Test suite for IntelligentCodeReviewer."""

    @pytest.fixture
    def coordinator(self):
        """Create a mock coordinator."""
        return Mock(spec=MultiModelCoordinator)

    @pytest.fixture
    def reviewer(self, coordinator):
        """Create a code reviewer instance."""
        return IntelligentCodeReviewer(coordinator)

    def test_static_analysis_security_issues(self, reviewer):
        """Test static analysis for security issues."""
        code = """
def unsafe_function():
    password = "hardcoded123"
    eval(user_input)
        """

        issues = reviewer._static_analysis(code, "python", "test.py")

        # Should find hardcoded password and eval usage
        assert len(issues) >= 2
        security_issues = [i for i in issues if i.category == IssueCategory.SECURITY]
        assert len(security_issues) >= 2

    def test_python_ast_analysis(self, reviewer):
        """Test Python AST analysis."""
        code = """
def complex_function(a, b, c, d, e, f, g):
    if True:
        if True:
            if True:
                if True:
                    pass

    try:
        something()
    except:
        pass
        """

        issues = reviewer._python_ast_analysis(code, "test.py")

        # Should find too many parameters and bare except
        assert len(issues) >= 2

        # Check for bare except
        bare_except = [i for i in issues if "except" in i.title.lower()]
        assert len(bare_except) >= 1

    def test_nesting_depth_calculation(self, reviewer):
        """Test nesting depth calculation."""
        import ast

        code = """
if True:
    if True:
        if True:
            pass
        """

        tree = ast.parse(code)
        if_node = next(node for node in ast.walk(tree) if isinstance(node, ast.If))

        depth = reviewer._get_nesting_depth(if_node)
        assert depth >= 2

    @pytest.mark.asyncio
    async def test_review_code_basic(self, reviewer, coordinator):
        """Test basic code review."""
        code = "print('Hello, world!')"

        # Mock AI response
        coordinator.execute = AsyncMock()

        report = await reviewer.review_code(code, language="python", file_path="test.py")

        assert report is not None
        assert report.total_lines > 0
        assert 0 <= report.quality_score <= 100
        assert 0 <= report.security_score <= 100

    def test_calculate_quality_score(self, reviewer):
        """Test quality score calculation."""
        # No issues - perfect score
        score = reviewer._calculate_quality_score([], "print('hello')")
        assert score == 100.0

        # With critical issues
        from resoftai.ai.code_reviewer import CodeIssue
        issues = [
            CodeIssue(
                id="1",
                severity=IssueSeverity.CRITICAL,
                category=IssueCategory.SECURITY,
                title="Security issue",
                description="desc",
                file_path="test.py",
                line_start=1,
                line_end=1,
                code_snippet="",
                suggestion="fix",
                auto_fixable=False
            )
        ]
        score = reviewer._calculate_quality_score(issues, "code")
        assert score < 100.0

    def test_calculate_security_score(self, reviewer):
        """Test security score calculation."""
        # No security issues
        score = reviewer._calculate_security_score([])
        assert score == 100.0

        # With security issues
        from resoftai.ai.code_reviewer import CodeIssue
        issues = [
            CodeIssue(
                id="1",
                severity=IssueSeverity.CRITICAL,
                category=IssueCategory.SECURITY,
                title="SQL Injection",
                description="desc",
                file_path="test.py",
                line_start=1,
                line_end=1,
                code_snippet="",
                suggestion="fix",
                auto_fixable=False
            )
        ]
        score = reviewer._calculate_security_score(issues)
        assert score < 100.0

    def test_generate_recommendations(self, reviewer):
        """Test recommendations generation."""
        from resoftai.ai.code_reviewer import CodeIssue

        issues = [
            CodeIssue(
                id="1",
                severity=IssueSeverity.CRITICAL,
                category=IssueCategory.SECURITY,
                title="Security issue",
                description="desc",
                file_path="test.py",
                line_start=1,
                line_end=1,
                code_snippet="",
                suggestion="fix",
                auto_fixable=True
            ),
            CodeIssue(
                id="2",
                severity=IssueSeverity.MEDIUM,
                category=IssueCategory.PERFORMANCE,
                title="Performance issue",
                description="desc",
                file_path="test.py",
                line_start=2,
                line_end=2,
                code_snippet="",
                suggestion="optimize",
                auto_fixable=False
            )
        ]

        recommendations = reviewer._generate_recommendations(issues)

        assert len(recommendations) > 0
        assert any("security" in r.lower() for r in recommendations)
