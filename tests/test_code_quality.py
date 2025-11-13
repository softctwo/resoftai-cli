"""Tests for code quality checking functionality."""
import pytest
from resoftai.core.code_quality import (
    CodeQualityChecker,
    LanguageType,
    QualityIssueLevel
)


class TestCodeQualityChecker:
    """Test suite for CodeQualityChecker."""

    @pytest.fixture
    def checker(self):
        """Get code quality checker instance."""
        return CodeQualityChecker()

    def test_detect_python_language(self, checker):
        """Test Python language detection."""
        assert checker.detect_language("main.py") == LanguageType.PYTHON
        assert checker.detect_language("script.PY") == LanguageType.PYTHON

    def test_detect_javascript_language(self, checker):
        """Test JavaScript language detection."""
        assert checker.detect_language("app.js") == LanguageType.JAVASCRIPT
        assert checker.detect_language("component.jsx") == LanguageType.JAVASCRIPT

    def test_detect_typescript_language(self, checker):
        """Test TypeScript language detection."""
        assert checker.detect_language("app.ts") == LanguageType.TYPESCRIPT
        assert checker.detect_language("component.tsx") == LanguageType.TYPESCRIPT

    def test_detect_java_language(self, checker):
        """Test Java language detection."""
        assert checker.detect_language("Main.java") == LanguageType.JAVA

    def test_detect_go_language(self, checker):
        """Test Go language detection."""
        assert checker.detect_language("main.go") == LanguageType.GO

    def test_detect_rust_language(self, checker):
        """Test Rust language detection."""
        assert checker.detect_language("main.rs") == LanguageType.RUST

    def test_analyze_clean_python_code(self, checker):
        """Test analysis of clean Python code."""
        code = '''
def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two numbers."""
    return a + b
'''
        report = checker.analyze_code(code, language=LanguageType.PYTHON)

        assert report.language == LanguageType.PYTHON
        assert report.score >= 95  # Should have a high score
        assert len(report.issues) == 0  # Should have no issues

    def test_detect_hardcoded_credentials(self, checker):
        """Test detection of hardcoded credentials."""
        code = '''
password = "secret123"
api_key = "abc123xyz"
'''
        report = checker.analyze_code(code, language=LanguageType.PYTHON)

        # Should detect critical security issues
        critical_issues = [i for i in report.issues if i.level == QualityIssueLevel.CRITICAL]
        assert len(critical_issues) >= 2  # password and api_key

    def test_detect_bare_except(self, checker):
        """Test detection of bare except clause in Python."""
        code = '''
try:
    risky_operation()
except:
    pass
'''
        report = checker.analyze_code(code, language=LanguageType.PYTHON)

        # Should detect bare except
        error_issues = [i for i in report.issues if i.level == QualityIssueLevel.ERROR]
        assert len(error_issues) > 0
        assert any("except" in i.message.lower() for i in error_issues)

    def test_detect_long_lines(self, checker):
        """Test detection of overly long lines."""
        code = 'x = "' + 'a' * 150 + '"'  # Line longer than 120 chars

        report = checker.analyze_code(code, language=LanguageType.PYTHON)

        # Should detect long line warning
        warning_issues = [i for i in report.issues if i.level == QualityIssueLevel.WARNING]
        assert len(warning_issues) > 0
        assert any("long" in i.message.lower() for i in warning_issues)

    def test_detect_javascript_equality(self, checker):
        """Test detection of == in JavaScript."""
        code = '''
if (x == y) {
    console.log("equal");
}
'''
        report = checker.analyze_code(code, language=LanguageType.JAVASCRIPT)

        # Should detect == usage
        issues = [i for i in report.issues if "==" in i.message]
        assert len(issues) > 0

    def test_detect_javascript_var(self, checker):
        """Test detection of var keyword in JavaScript."""
        code = 'var x = 5;'

        report = checker.analyze_code(code, language=LanguageType.JAVASCRIPT)

        # Should detect var usage
        issues = [i for i in report.issues if "var" in i.message.lower()]
        assert len(issues) > 0

    def test_calculate_metrics(self, checker):
        """Test metrics calculation."""
        code = '''
# This is a comment
def function():
    # Another comment
    return 42

# Final comment
'''
        report = checker.analyze_code(code, language=LanguageType.PYTHON)

        assert report.metrics["comment_lines"] >= 3
        assert report.metrics["code_lines"] >= 2
        assert report.metrics["comment_ratio"] > 0

    def test_quality_score_calculation(self, checker):
        """Test quality score calculation."""
        # Clean code should have high score
        clean_code = '''
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
'''
        clean_report = checker.analyze_code(clean_code, language=LanguageType.PYTHON)
        assert clean_report.score >= 95

        # Problematic code should have lower score
        bad_code = '''
password = "hardcoded"
try:
    x()
except:
    pass
'''
        bad_report = checker.analyze_code(bad_code, language=LanguageType.PYTHON)
        assert bad_report.score < clean_report.score

    def test_format_report(self, checker):
        """Test report formatting."""
        code = 'password = "test123"'
        report = checker.analyze_code(code, language=LanguageType.PYTHON)

        formatted = checker.format_report(report)

        assert "CODE QUALITY REPORT" in formatted
        assert "Language:" in formatted
        assert "Quality Score:" in formatted
        assert "METRICS:" in formatted

    def test_typescript_any_type_detection(self, checker):
        """Test detection of 'any' type in TypeScript."""
        code = 'function test(param: any): void {}'

        report = checker.analyze_code(code, language=LanguageType.TYPESCRIPT)

        # Should detect 'any' usage
        issues = [i for i in report.issues if "any" in i.message.lower()]
        assert len(issues) > 0

    def test_java_system_out_detection(self, checker):
        """Test detection of System.out.println in Java."""
        code = 'System.out.println("Debug message");'

        report = checker.analyze_code(code, language=LanguageType.JAVA)

        # Should detect System.out usage
        issues = [i for i in report.issues if "system" in i.message.lower()]
        assert len(issues) > 0
