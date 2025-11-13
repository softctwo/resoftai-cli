"""
Code quality checking and analysis tools.

This module provides comprehensive code quality assessment including:
- Static code analysis
- Best practices verification
- Security vulnerability detection
- Performance optimization suggestions
- Code style and formatting checks
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional
import re
import logging

logger = logging.getLogger(__name__)


class QualityIssueLevel(str, Enum):
    """Severity levels for quality issues."""
    CRITICAL = "critical"  # Security vulnerabilities, major bugs
    ERROR = "error"        # Functionality issues, bad practices
    WARNING = "warning"    # Code smells, minor issues
    INFO = "info"          # Suggestions, optimizations


class LanguageType(str, Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    CPP = "cpp"
    CSHARP = "csharp"
    PHP = "php"
    RUBY = "ruby"
    UNKNOWN = "unknown"


@dataclass
class QualityIssue:
    """Represents a code quality issue."""
    level: QualityIssueLevel
    message: str
    line_number: Optional[int] = None
    file_path: Optional[str] = None
    rule_id: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class QualityReport:
    """Code quality assessment report."""
    language: LanguageType
    total_lines: int
    issues: List[QualityIssue]
    score: float  # 0-100
    metrics: Dict[str, Any]


class CodeQualityChecker:
    """
    Comprehensive code quality checker supporting multiple programming languages.

    Features:
    - Language-specific analysis
    - Security vulnerability detection
    - Best practices verification
    - Performance optimization hints
    - Code complexity metrics
    """

    def __init__(self):
        """Initialize the code quality checker."""
        self.language_detectors = {
            r'\.py$': LanguageType.PYTHON,
            r'\.js$': LanguageType.JAVASCRIPT,
            r'\.jsx$': LanguageType.JAVASCRIPT,
            r'\.ts$': LanguageType.TYPESCRIPT,
            r'\.tsx$': LanguageType.TYPESCRIPT,
            r'\.java$': LanguageType.JAVA,
            r'\.go$': LanguageType.GO,
            r'\.rs$': LanguageType.RUST,
            r'\.cpp$|\.cc$|\.cxx$': LanguageType.CPP,
            r'\.cs$': LanguageType.CSHARP,
            r'\.php$': LanguageType.PHP,
            r'\.rb$': LanguageType.RUBY,
        }

    def detect_language(self, filename: str) -> LanguageType:
        """
        Detect programming language from filename.

        Args:
            filename: Name of the file

        Returns:
            Detected language type
        """
        for pattern, lang in self.language_detectors.items():
            if re.search(pattern, filename, re.IGNORECASE):
                return lang
        return LanguageType.UNKNOWN

    def analyze_code(
        self,
        code: str,
        language: Optional[LanguageType] = None,
        filename: Optional[str] = None
    ) -> QualityReport:
        """
        Analyze code quality for given source code.

        Args:
            code: Source code to analyze
            language: Programming language (auto-detected if not provided)
            filename: Optional filename for language detection

        Returns:
            Quality assessment report
        """
        # Detect language if not provided
        if language is None and filename:
            language = self.detect_language(filename)
        elif language is None:
            language = LanguageType.UNKNOWN

        issues: List[QualityIssue] = []

        # Count lines
        lines = code.split('\n')
        total_lines = len(lines)

        # General checks applicable to all languages
        issues.extend(self._check_general_issues(code, lines))

        # Language-specific checks
        if language == LanguageType.PYTHON:
            issues.extend(self._check_python(code, lines))
        elif language == LanguageType.JAVASCRIPT:
            issues.extend(self._check_javascript(code, lines))
        elif language == LanguageType.TYPESCRIPT:
            issues.extend(self._check_typescript(code, lines))
        elif language == LanguageType.JAVA:
            issues.extend(self._check_java(code, lines))
        elif language == LanguageType.GO:
            issues.extend(self._check_go(code, lines))

        # Calculate quality score
        score = self._calculate_quality_score(issues, total_lines)

        # Calculate metrics
        metrics = self._calculate_metrics(code, lines, issues)

        return QualityReport(
            language=language,
            total_lines=total_lines,
            issues=issues,
            score=score,
            metrics=metrics
        )

    def _check_general_issues(self, code: str, lines: List[str]) -> List[QualityIssue]:
        """Check for general code quality issues."""
        issues = []

        # Check for extremely long lines
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append(QualityIssue(
                    level=QualityIssueLevel.WARNING,
                    message=f"Line too long ({len(line)} characters)",
                    line_number=i,
                    rule_id="line-length",
                    suggestion="Break long lines for better readability (max 120 chars)"
                ))

        # Check for hardcoded credentials
        credential_patterns = [
            (r'password\s*=\s*["\'](?!{{).+["\']', "Hardcoded password detected"),
            (r'api[_-]?key\s*=\s*["\'](?!{{).+["\']', "Hardcoded API key detected"),
            (r'secret\s*=\s*["\'](?!{{).+["\']', "Hardcoded secret detected"),
            (r'token\s*=\s*["\'](?!{{).+["\']', "Hardcoded token detected"),
        ]

        for i, line in enumerate(lines, 1):
            for pattern, message in credential_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(QualityIssue(
                        level=QualityIssueLevel.CRITICAL,
                        message=message,
                        line_number=i,
                        rule_id="security-credentials",
                        suggestion="Use environment variables or secure configuration management"
                    ))

        # Check for TODO/FIXME comments
        for i, line in enumerate(lines, 1):
            if re.search(r'#\s*(TODO|FIXME|HACK|XXX)', line, re.IGNORECASE):
                issues.append(QualityIssue(
                    level=QualityIssueLevel.INFO,
                    message="Unresolved TODO/FIXME comment",
                    line_number=i,
                    rule_id="todo-comment",
                    suggestion="Address or track these items in issue tracker"
                ))

        # Check for commented-out code (multiple consecutive comment lines)
        comment_count = 0
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('//'):
                comment_count += 1
                if comment_count > 5:
                    issues.append(QualityIssue(
                        level=QualityIssueLevel.WARNING,
                        message="Large block of commented code",
                        line_number=i - comment_count + 1,
                        rule_id="commented-code",
                        suggestion="Remove unused commented code or use version control"
                    ))
                    comment_count = 0
            else:
                comment_count = 0

        return issues

    def _check_python(self, code: str, lines: List[str]) -> List[QualityIssue]:
        """Python-specific code quality checks."""
        issues = []

        # Check for proper exception handling
        for i, line in enumerate(lines, 1):
            # Bare except clause
            if re.search(r'except\s*:', line):
                issues.append(QualityIssue(
                    level=QualityIssueLevel.ERROR,
                    message="Bare except clause catches all exceptions",
                    line_number=i,
                    rule_id="python-bare-except",
                    suggestion="Catch specific exceptions: except SpecificException:"
                ))

            # Using print() for debugging
            if re.search(r'\bprint\s*\(', line) and 'logger' not in code:
                issues.append(QualityIssue(
                    level=QualityIssueLevel.WARNING,
                    message="Using print() instead of logging",
                    line_number=i,
                    rule_id="python-print-logging",
                    suggestion="Use logging module for better control: logger.info()"
                ))

        # Check for mutable default arguments
        if re.search(r'def\s+\w+\([^)]*=\s*(\[\]|\{\})', code):
            issues.append(QualityIssue(
                level=QualityIssueLevel.ERROR,
                message="Mutable default argument detected",
                rule_id="python-mutable-default",
                suggestion="Use None as default and initialize inside function"
            ))

        # Check for SQL injection vulnerabilities
        for i, line in enumerate(lines, 1):
            if re.search(r'execute\s*\(\s*["\'].*%s', line) or re.search(r'execute\s*\(\s*f["\']', line):
                issues.append(QualityIssue(
                    level=QualityIssueLevel.CRITICAL,
                    message="Potential SQL injection vulnerability",
                    line_number=i,
                    rule_id="security-sql-injection",
                    suggestion="Use parameterized queries: execute(query, params)"
                ))

        return issues

    def _check_javascript(self, code: str, lines: List[str]) -> List[QualityIssue]:
        """JavaScript-specific code quality checks."""
        issues = []

        # Check for == instead of ===
        for i, line in enumerate(lines, 1):
            if re.search(r'(?<![=!])={2}(?!=)', line):
                issues.append(QualityIssue(
                    level=QualityIssueLevel.WARNING,
                    message="Using == instead of ===",
                    line_number=i,
                    rule_id="js-equality",
                    suggestion="Use strict equality (===) to avoid type coercion"
                ))

        # Check for var usage
        for i, line in enumerate(lines, 1):
            if re.search(r'\bvar\s+', line):
                issues.append(QualityIssue(
                    level=QualityIssueLevel.WARNING,
                    message="Using 'var' instead of 'let' or 'const'",
                    line_number=i,
                    rule_id="js-var-usage",
                    suggestion="Use 'const' for immutable, 'let' for mutable variables"
                ))

        # Check for console.log
        for i, line in enumerate(lines, 1):
            if re.search(r'console\.(log|debug|info)', line):
                issues.append(QualityIssue(
                    level=QualityIssueLevel.INFO,
                    message="console.log() statement found",
                    line_number=i,
                    rule_id="js-console-log",
                    suggestion="Remove console.log or use proper logging framework"
                ))

        return issues

    def _check_typescript(self, code: str, lines: List[str]) -> List[QualityIssue]:
        """TypeScript-specific code quality checks."""
        issues = []

        # Include JavaScript checks
        issues.extend(self._check_javascript(code, lines))

        # Check for 'any' type
        for i, line in enumerate(lines, 1):
            if re.search(r':\s*any\b', line):
                issues.append(QualityIssue(
                    level=QualityIssueLevel.WARNING,
                    message="Using 'any' type loses TypeScript benefits",
                    line_number=i,
                    rule_id="ts-any-type",
                    suggestion="Define specific types for better type safety"
                ))

        # Check for non-null assertion operator
        for i, line in enumerate(lines, 1):
            if re.search(r'!\.', line):
                issues.append(QualityIssue(
                    level=QualityIssueLevel.WARNING,
                    message="Non-null assertion (!) can hide potential errors",
                    line_number=i,
                    rule_id="ts-non-null-assertion",
                    suggestion="Use optional chaining (?.) or proper null checks"
                ))

        return issues

    def _check_java(self, code: str, lines: List[str]) -> List[QualityIssue]:
        """Java-specific code quality checks."""
        issues = []

        # Check for System.out.println
        for i, line in enumerate(lines, 1):
            if re.search(r'System\.(out|err)\.print', line):
                issues.append(QualityIssue(
                    level=QualityIssueLevel.WARNING,
                    message="Using System.out.println instead of logging",
                    line_number=i,
                    rule_id="java-system-out",
                    suggestion="Use logging framework (slf4j, log4j)"
                ))

        # Check for empty catch blocks
        if re.search(r'catch\s*\([^)]+\)\s*\{\s*\}', code):
            issues.append(QualityIssue(
                level=QualityIssueLevel.ERROR,
                message="Empty catch block suppresses exceptions",
                rule_id="java-empty-catch",
                suggestion="Handle exceptions properly or at least log them"
            ))

        return issues

    def _check_go(self, code: str, lines: List[str]) -> List[QualityIssue]:
        """Go-specific code quality checks."""
        issues = []

        # Check for unhandled errors
        for i, line in enumerate(lines, 1):
            if re.search(r'_, err\s*:=', line):
                issues.append(QualityIssue(
                    level=QualityIssueLevel.WARNING,
                    message="Error intentionally ignored",
                    line_number=i,
                    rule_id="go-ignored-error",
                    suggestion="Handle or document why error is ignored"
                ))

        return issues

    def _calculate_quality_score(self, issues: List[QualityIssue], total_lines: int) -> float:
        """
        Calculate overall quality score (0-100).

        Scoring:
        - Start at 100
        - Critical issues: -10 each
        - Error issues: -5 each
        - Warning issues: -2 each
        - Info issues: -0.5 each
        - Bonus for low issue density
        """
        score = 100.0

        for issue in issues:
            if issue.level == QualityIssueLevel.CRITICAL:
                score -= 10
            elif issue.level == QualityIssueLevel.ERROR:
                score -= 5
            elif issue.level == QualityIssueLevel.WARNING:
                score -= 2
            elif issue.level == QualityIssueLevel.INFO:
                score -= 0.5

        # Issue density bonus (fewer issues per line = better)
        if total_lines > 0:
            issue_density = len(issues) / total_lines
            if issue_density < 0.01:  # Less than 1 issue per 100 lines
                score += 5

        return max(0.0, min(100.0, score))

    def _calculate_metrics(
        self,
        code: str,
        lines: List[str],
        issues: List[QualityIssue]
    ) -> Dict[str, Any]:
        """Calculate code metrics."""
        # Count code vs comment vs blank lines
        code_lines = 0
        comment_lines = 0
        blank_lines = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
            elif stripped.startswith('#') or stripped.startswith('//'):
                comment_lines += 1
            else:
                code_lines += 1

        # Count issues by level
        issue_counts = {
            "critical": sum(1 for i in issues if i.level == QualityIssueLevel.CRITICAL),
            "error": sum(1 for i in issues if i.level == QualityIssueLevel.ERROR),
            "warning": sum(1 for i in issues if i.level == QualityIssueLevel.WARNING),
            "info": sum(1 for i in issues if i.level == QualityIssueLevel.INFO),
        }

        return {
            "total_lines": len(lines),
            "code_lines": code_lines,
            "comment_lines": comment_lines,
            "blank_lines": blank_lines,
            "comment_ratio": comment_lines / max(1, code_lines),
            "issue_counts": issue_counts,
            "total_issues": len(issues),
            "issue_density": len(issues) / max(1, len(lines)),
        }

    def format_report(self, report: QualityReport) -> str:
        """
        Format quality report as human-readable text.

        Args:
            report: Quality report to format

        Returns:
            Formatted report string
        """
        lines = [
            "=" * 80,
            "CODE QUALITY REPORT",
            "=" * 80,
            "",
            f"Language: {report.language.value.upper()}",
            f"Total Lines: {report.total_lines}",
            f"Quality Score: {report.score:.1f}/100",
            "",
            "METRICS:",
            f"  Code Lines: {report.metrics['code_lines']}",
            f"  Comment Lines: {report.metrics['comment_lines']}",
            f"  Blank Lines: {report.metrics['blank_lines']}",
            f"  Comment Ratio: {report.metrics['comment_ratio']:.2%}",
            f"  Issue Density: {report.metrics['issue_density']:.3f} issues/line",
            "",
            "ISSUES BY SEVERITY:",
            f"  Critical: {report.metrics['issue_counts']['critical']}",
            f"  Error: {report.metrics['issue_counts']['error']}",
            f"  Warning: {report.metrics['issue_counts']['warning']}",
            f"  Info: {report.metrics['issue_counts']['info']}",
            "",
        ]

        if report.issues:
            lines.append("DETAILED ISSUES:")
            lines.append("")
            for issue in sorted(report.issues, key=lambda x: (x.level.value, x.line_number or 0)):
                level_icon = {
                    QualityIssueLevel.CRITICAL: "🔴",
                    QualityIssueLevel.ERROR: "❌",
                    QualityIssueLevel.WARNING: "⚠️",
                    QualityIssueLevel.INFO: "ℹ️",
                }
                icon = level_icon.get(issue.level, "•")
                line_info = f"Line {issue.line_number}" if issue.line_number else "General"
                lines.append(f"{icon} [{issue.level.value.upper()}] {line_info}: {issue.message}")
                if issue.suggestion:
                    lines.append(f"   💡 {issue.suggestion}")
                lines.append("")
        else:
            lines.append("✅ No issues found!")
            lines.append("")

        lines.append("=" * 80)

        return "\n".join(lines)


# Singleton instance
_checker_instance = None


def get_code_quality_checker() -> CodeQualityChecker:
    """Get singleton instance of code quality checker."""
    global _checker_instance
    if _checker_instance is None:
        _checker_instance = CodeQualityChecker()
    return _checker_instance
