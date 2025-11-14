"""Intelligent Code Review System powered by AI."""
from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import re
import ast

from resoftai.ai.multi_model_coordinator import MultiModelCoordinator, TaskComplexity


class IssueSeverity(str, Enum):
    """Severity levels for code issues."""
    CRITICAL = "critical"  # Security vulnerabilities, critical bugs
    HIGH = "high"  # Performance issues, major bugs
    MEDIUM = "medium"  # Code smells, moderate issues
    LOW = "low"  # Style issues, minor improvements
    INFO = "info"  # Informational suggestions


class IssueCategory(str, Enum):
    """Categories of code issues."""
    SECURITY = "security"  # Security vulnerabilities
    PERFORMANCE = "performance"  # Performance problems
    BUG = "bug"  # Potential bugs
    MAINTAINABILITY = "maintainability"  # Code maintainability
    STYLE = "style"  # Code style
    BEST_PRACTICE = "best_practice"  # Best practice violations
    DOCUMENTATION = "documentation"  # Missing/poor documentation
    TESTING = "testing"  # Testing-related issues


@dataclass
class CodeIssue:
    """Represents a single code issue found during review."""
    id: str
    severity: IssueSeverity
    category: IssueCategory
    title: str
    description: str
    file_path: str
    line_start: int
    line_end: int
    code_snippet: str
    suggestion: str
    auto_fixable: bool = False
    fix_code: Optional[str] = None
    confidence: float = 1.0  # AI confidence in the issue (0-1)
    references: List[str] = field(default_factory=list)  # Links to documentation


@dataclass
class CodeReviewReport:
    """Complete code review report."""
    project_id: int
    files_reviewed: int
    total_lines: int
    issues: List[CodeIssue]
    quality_score: float  # Overall quality score (0-100)
    maintainability_index: float  # Maintainability score (0-100)
    security_score: float  # Security score (0-100)
    summary: str
    recommendations: List[str]
    reviewed_at: datetime
    review_duration: float  # seconds
    ai_models_used: List[str]


class IntelligentCodeReviewer:
    """AI-powered intelligent code review system."""

    def __init__(self, coordinator: MultiModelCoordinator):
        """Initialize code reviewer with multi-model coordinator."""
        self.coordinator = coordinator

        # Issue patterns (basic static analysis)
        self.security_patterns = {
            r'eval\s*\(': "Use of eval() is dangerous",
            r'exec\s*\(': "Use of exec() is dangerous",
            r'__import__\s*\(': "Dynamic imports can be risky",
            r'pickle\.loads?\s*\(': "Unpickling untrusted data is unsafe",
            r'sql\s*=.*\+.*': "Potential SQL injection vulnerability",
            r'password\s*=\s*["\'].*["\']': "Hardcoded password detected",
            r'api[_-]?key\s*=\s*["\'].*["\']': "Hardcoded API key detected",
        }

        self.performance_patterns = {
            r'for\s+\w+\s+in\s+range\(len\(': "Use enumerate() instead of range(len())",
            r'\.append\s*\(.*\)\s*$': "Consider list comprehension for better performance",
        }

    async def review_code(
        self,
        code: str,
        language: str = "python",
        file_path: str = "",
        context: Optional[Dict[str, Any]] = None
    ) -> CodeReviewReport:
        """
        Perform comprehensive AI-powered code review.

        Args:
            code: Source code to review
            language: Programming language
            file_path: Path to the file being reviewed
            context: Additional context (project info, requirements, etc.)

        Returns:
            CodeReviewReport with findings and recommendations
        """
        start_time = datetime.now()

        # Static analysis (pattern matching)
        static_issues = self._static_analysis(code, language, file_path)

        # AI-powered deep analysis
        ai_issues = await self._ai_analysis(code, language, file_path, context or {})

        # Combine issues
        all_issues = static_issues + ai_issues

        # Calculate scores
        quality_score = self._calculate_quality_score(all_issues, code)
        maintainability_index = self._calculate_maintainability(code, language)
        security_score = self._calculate_security_score(all_issues)

        # Generate summary and recommendations
        summary = await self._generate_summary(all_issues, code, language)
        recommendations = self._generate_recommendations(all_issues)

        duration = (datetime.now() - start_time).total_seconds()

        return CodeReviewReport(
            project_id=context.get("project_id", 0) if context else 0,
            files_reviewed=1,
            total_lines=len(code.split('\n')),
            issues=all_issues,
            quality_score=quality_score,
            maintainability_index=maintainability_index,
            security_score=security_score,
            summary=summary,
            recommendations=recommendations,
            reviewed_at=datetime.now(),
            review_duration=duration,
            ai_models_used=["multi-model-coordinator"]
        )

    def _static_analysis(
        self,
        code: str,
        language: str,
        file_path: str
    ) -> List[CodeIssue]:
        """Perform static analysis using pattern matching."""
        issues = []
        lines = code.split('\n')

        # Security pattern checks
        for line_num, line in enumerate(lines, 1):
            for pattern, message in self.security_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(CodeIssue(
                        id=f"SEC-{line_num}",
                        severity=IssueSeverity.CRITICAL,
                        category=IssueCategory.SECURITY,
                        title=message,
                        description=f"Security issue detected: {message}",
                        file_path=file_path,
                        line_start=line_num,
                        line_end=line_num,
                        code_snippet=line.strip(),
                        suggestion="Review this code for security implications",
                        auto_fixable=False,
                        confidence=0.9
                    ))

            # Performance pattern checks
            for pattern, message in self.performance_patterns.items():
                if re.search(pattern, line):
                    issues.append(CodeIssue(
                        id=f"PERF-{line_num}",
                        severity=IssueSeverity.MEDIUM,
                        category=IssueCategory.PERFORMANCE,
                        title=message,
                        description=f"Performance improvement opportunity: {message}",
                        file_path=file_path,
                        line_start=line_num,
                        line_end=line_num,
                        code_snippet=line.strip(),
                        suggestion="Consider optimizing this code",
                        auto_fixable=True,
                        confidence=0.8
                    ))

        # Python-specific AST analysis
        if language.lower() == "python":
            issues.extend(self._python_ast_analysis(code, file_path))

        return issues

    def _python_ast_analysis(self, code: str, file_path: str) -> List[CodeIssue]:
        """Analyze Python code using AST."""
        issues = []

        try:
            tree = ast.parse(code)

            # Check for common issues
            for node in ast.walk(tree):
                # Too many arguments
                if isinstance(node, ast.FunctionDef):
                    if len(node.args.args) > 5:
                        issues.append(CodeIssue(
                            id=f"MAINT-{node.lineno}",
                            severity=IssueSeverity.MEDIUM,
                            category=IssueCategory.MAINTAINABILITY,
                            title=f"Function '{node.name}' has too many parameters ({len(node.args.args)})",
                            description="Functions with many parameters are hard to maintain",
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=node.end_lineno or node.lineno,
                            code_snippet=f"def {node.name}(...)",
                            suggestion="Consider using a configuration object or reducing parameters",
                            auto_fixable=False,
                            confidence=1.0
                        ))

                # Deeply nested code
                if isinstance(node, (ast.For, ast.While, ast.If)):
                    depth = self._get_nesting_depth(node)
                    if depth > 3:
                        issues.append(CodeIssue(
                            id=f"MAINT-{node.lineno}-NEST",
                            severity=IssueSeverity.MEDIUM,
                            category=IssueCategory.MAINTAINABILITY,
                            title=f"Deeply nested code (depth: {depth})",
                            description="Deep nesting reduces readability",
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=node.end_lineno or node.lineno,
                            code_snippet="Nested control structure",
                            suggestion="Consider extracting nested logic into separate functions",
                            auto_fixable=False,
                            confidence=0.9
                        ))

                # Bare except
                if isinstance(node, ast.ExceptHandler):
                    if node.type is None:
                        issues.append(CodeIssue(
                            id=f"BEST-{node.lineno}",
                            severity=IssueSeverity.HIGH,
                            category=IssueCategory.BEST_PRACTICE,
                            title="Bare except clause",
                            description="Catching all exceptions can hide bugs",
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=node.end_lineno or node.lineno,
                            code_snippet="except:",
                            suggestion="Catch specific exceptions instead",
                            auto_fixable=True,
                            fix_code="except Exception:",
                            confidence=1.0
                        ))

        except SyntaxError as e:
            issues.append(CodeIssue(
                id="SYNTAX-ERROR",
                severity=IssueSeverity.CRITICAL,
                category=IssueCategory.BUG,
                title="Syntax error in code",
                description=str(e),
                file_path=file_path,
                line_start=e.lineno or 0,
                line_end=e.lineno or 0,
                code_snippet=e.text or "",
                suggestion="Fix the syntax error",
                auto_fixable=False,
                confidence=1.0
            ))

        return issues

    def _get_nesting_depth(self, node: ast.AST, depth: int = 0) -> int:
        """Calculate nesting depth of a node."""
        max_depth = depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While, ast.If, ast.With)):
                child_depth = self._get_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
        return max_depth

    async def _ai_analysis(
        self,
        code: str,
        language: str,
        file_path: str,
        context: Dict[str, Any]
    ) -> List[CodeIssue]:
        """Perform AI-powered deep code analysis."""
        # Prepare prompt for AI review
        prompt = f"""Perform a comprehensive code review of the following {language} code.

File: {file_path}

Code:
```{language}
{code}
```

Context:
{context}

Please analyze the code for:
1. Security vulnerabilities
2. Performance issues
3. Potential bugs
4. Code maintainability
5. Best practice violations
6. Missing or poor documentation

For each issue found, provide:
- Severity (critical/high/medium/low)
- Category (security/performance/bug/maintainability/style/best_practice/documentation)
- Title and description
- Line number(s)
- Specific suggestion for improvement
- Whether it's auto-fixable

Format your response as a structured list of issues."""

        try:
            # Use multi-model coordination for high-quality review
            response = await self.coordinator.execute(
                prompt=prompt,
                task_complexity=TaskComplexity.COMPLEX,
                max_models=3
            )

            # Parse AI response into issues
            # (Simplified parsing - in production, use structured output)
            ai_issues = self._parse_ai_response(response.final_output, file_path)
            return ai_issues

        except Exception as e:
            # Log error but don't fail the review
            print(f"AI analysis error: {e}")
            return []

    def _parse_ai_response(self, response: str, file_path: str) -> List[CodeIssue]:
        """Parse AI response into structured issues."""
        # Simplified parsing - in production, use structured output format
        issues = []

        # Example parsing (basic implementation)
        sections = response.split('\n\n')
        issue_counter = 0

        for section in sections:
            if any(keyword in section.lower() for keyword in ['issue', 'problem', 'vulnerability', 'bug']):
                issue_counter += 1

                # Extract severity
                severity = IssueSeverity.MEDIUM
                if 'critical' in section.lower():
                    severity = IssueSeverity.CRITICAL
                elif 'high' in section.lower():
                    severity = IssueSeverity.HIGH
                elif 'low' in section.lower():
                    severity = IssueSeverity.LOW

                # Extract category
                category = IssueCategory.BUG
                if 'security' in section.lower():
                    category = IssueCategory.SECURITY
                elif 'performance' in section.lower():
                    category = IssueCategory.PERFORMANCE
                elif 'maintain' in section.lower():
                    category = IssueCategory.MAINTAINABILITY

                # Create issue
                issues.append(CodeIssue(
                    id=f"AI-{issue_counter}",
                    severity=severity,
                    category=category,
                    title=section.split('\n')[0][:100],
                    description=section[:500],
                    file_path=file_path,
                    line_start=1,
                    line_end=1,
                    code_snippet="",
                    suggestion="See AI analysis",
                    auto_fixable=False,
                    confidence=0.7
                ))

        return issues

    def _calculate_quality_score(self, issues: List[CodeIssue], code: str) -> float:
        """Calculate overall code quality score (0-100)."""
        if not code.strip():
            return 0.0

        # Base score
        score = 100.0

        # Deduct points based on issues
        severity_weights = {
            IssueSeverity.CRITICAL: 20,
            IssueSeverity.HIGH: 10,
            IssueSeverity.MEDIUM: 5,
            IssueSeverity.LOW: 2,
            IssueSeverity.INFO: 0.5,
        }

        for issue in issues:
            score -= severity_weights.get(issue.severity, 1)

        return max(0.0, min(100.0, score))

    def _calculate_maintainability(self, code: str, language: str) -> float:
        """Calculate maintainability index (0-100)."""
        # Simplified maintainability calculation
        lines = code.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]

        # Factors
        loc = len(non_empty_lines)
        comment_lines = len([l for l in lines if l.strip().startswith('#')])
        comment_ratio = comment_lines / max(loc, 1)

        # Higher score for reasonable size and good comments
        size_score = max(0, 100 - (loc / 10))  # Penalize very long files
        comment_score = min(100, comment_ratio * 100 * 3)  # Reward comments

        return (size_score + comment_score) / 2

    def _calculate_security_score(self, issues: List[CodeIssue]) -> float:
        """Calculate security score (0-100)."""
        score = 100.0

        security_issues = [i for i in issues if i.category == IssueCategory.SECURITY]

        for issue in security_issues:
            if issue.severity == IssueSeverity.CRITICAL:
                score -= 30
            elif issue.severity == IssueSeverity.HIGH:
                score -= 15
            else:
                score -= 5

        return max(0.0, score)

    async def _generate_summary(
        self,
        issues: List[CodeIssue],
        code: str,
        language: str
    ) -> str:
        """Generate review summary using AI."""
        # Count issues by severity
        severity_counts = {}
        for issue in issues:
            severity_counts[issue.severity.value] = severity_counts.get(issue.severity.value, 0) + 1

        summary_parts = [
            f"Code review for {language} file",
            f"Total issues found: {len(issues)}",
        ]

        for severity, count in sorted(severity_counts.items()):
            summary_parts.append(f"- {severity}: {count}")

        return "\n".join(summary_parts)

    def _generate_recommendations(self, issues: List[CodeIssue]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Group issues by category
        category_counts = {}
        for issue in issues:
            category_counts[issue.category.value] = category_counts.get(issue.category.value, 0) + 1

        # Generate recommendations based on most common issues
        if category_counts.get(IssueCategory.SECURITY.value, 0) > 0:
            recommendations.append("Address all security vulnerabilities immediately")

        if category_counts.get(IssueCategory.PERFORMANCE.value, 0) > 2:
            recommendations.append("Consider performance optimization opportunities")

        if category_counts.get(IssueCategory.MAINTAINABILITY.value, 0) > 3:
            recommendations.append("Refactor code to improve maintainability")

        if category_counts.get(IssueCategory.DOCUMENTATION.value, 0) > 0:
            recommendations.append("Add documentation for better code understanding")

        # Auto-fixable issues
        auto_fixable = [i for i in issues if i.auto_fixable]
        if auto_fixable:
            recommendations.append(f"{len(auto_fixable)} issues can be auto-fixed")

        return recommendations if recommendations else ["Code quality is good, no major issues found"]
