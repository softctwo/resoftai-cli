"""
Technical debt analysis system.

This module identifies and quantifies technical debt in codebases,
helping teams prioritize refactoring and maintenance efforts.
"""

import re
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DebtType(str, Enum):
    """Types of technical debt."""
    CODE_DUPLICATION = "code_duplication"
    COMPLEX_CODE = "complex_code"
    OUTDATED_DEPENDENCIES = "outdated_dependencies"
    MISSING_TESTS = "missing_tests"
    POOR_DOCUMENTATION = "poor_documentation"
    DEPRECATED_API = "deprecated_api"
    SECURITY_VULNERABILITIES = "security_vulnerabilities"
    PERFORMANCE_ISSUES = "performance_issues"
    INCONSISTENT_STYLE = "inconsistent_style"
    TODO_COMMENTS = "todo_comments"


class DebtSeverity(str, Enum):
    """Severity levels for technical debt."""
    CRITICAL = "critical"  # Urgent, blocks progress
    HIGH = "high"          # Important, plan to fix soon
    MEDIUM = "medium"      # Moderate impact
    LOW = "low"            # Minor inconvenience
    TRIVIAL = "trivial"    # Nice to fix but not essential


@dataclass
class TechnicalDebtItem:
    """A single technical debt item."""
    debt_type: DebtType
    severity: DebtSeverity
    title: str
    description: str
    location: Optional[str] = None  # File:line
    estimated_effort_hours: float = 0.0  # Hours to fix
    interest_rate: float = 0.0  # Cost per month if not fixed
    impact_score: float = 0.0  # Impact if fixed (0-10)
    created_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TechnicalDebtReport:
    """Technical debt analysis report."""
    total_items: int
    total_estimated_hours: float
    total_debt_score: float  # 0-100
    items: List[TechnicalDebtItem]
    breakdown_by_type: Dict[DebtType, int]
    breakdown_by_severity: Dict[DebtSeverity, int]
    priority_list: List[TechnicalDebtItem]  # Sorted by priority
    analysis_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class TechnicalDebtAnalyzer:
    """
    Analyze technical debt in code.

    Identifies various forms of technical debt and provides quantified
    assessments to help prioritize refactoring efforts.
    """

    def __init__(self):
        """Initialize technical debt analyzer."""
        self.patterns = self._initialize_patterns()
        logger.info("TechnicalDebtAnalyzer initialized")

    def _initialize_patterns(self) -> Dict[str, List[Dict]]:
        """Initialize debt detection patterns."""
        return {
            'all': [
                {
                    'pattern': r'(?:TODO|FIXME|HACK|XXX|REFACTOR)\s*:?\s*(.+)',
                    'type': DebtType.TODO_COMMENTS,
                    'severity': DebtSeverity.LOW,
                    'title': 'TODO comment found',
                    'effort_hours': 0.5
                },
                {
                    'pattern': r'(?:deprecated|DEPRECATED)',
                    'type': DebtType.DEPRECATED_API,
                    'severity': DebtSeverity.MEDIUM,
                    'title': 'Deprecated API usage',
                    'effort_hours': 2.0
                },
                {
                    'pattern': r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/|#.*|//.*',
                    'type': DebtType.POOR_DOCUMENTATION,
                    'severity': DebtSeverity.LOW,
                    'title': 'Minimal documentation',
                    'effort_hours': 1.0
                },
            ],
            'python': [
                {
                    'pattern': r'pass\s*$',
                    'type': DebtType.MISSING_TESTS,
                    'severity': DebtSeverity.MEDIUM,
                    'title': 'Empty implementation',
                    'effort_hours': 2.0
                },
                {
                    'pattern': r'print\s*\(',
                    'type': DebtType.POOR_DOCUMENTATION,
                    'severity': DebtSeverity.LOW,
                    'title': 'Debug print statements',
                    'effort_hours': 0.25
                },
            ],
            'javascript': [
                {
                    'pattern': r'console\.(log|debug|warn)',
                    'type': DebtType.POOR_DOCUMENTATION,
                    'severity': DebtSeverity.LOW,
                    'title': 'Console debug statements',
                    'effort_hours': 0.25
                },
                {
                    'pattern': r'\bvar\s+',
                    'type': DebtType.INCONSISTENT_STYLE,
                    'severity': DebtSeverity.LOW,
                    'title': 'Using var instead of let/const',
                    'effort_hours': 0.5
                },
            ]
        }

    async def analyze(
        self,
        code: str,
        language: str,
        filename: Optional[str] = None,
        file_history: Optional[Dict] = None
    ) -> TechnicalDebtReport:
        """
        Analyze technical debt in code.

        Args:
            code: Source code to analyze
            language: Programming language
            filename: Optional filename
            file_history: Optional git history information

        Returns:
            Technical debt report
        """
        start_time = datetime.now()

        debt_items = []
        lines = code.split('\n')

        # Pattern-based detection
        debt_items.extend(self._detect_by_patterns(code, lines, language, filename))

        # Duplication detection
        debt_items.extend(self._detect_duplication(lines, filename))

        # Complexity detection
        debt_items.extend(self._detect_complexity(code, lines, language, filename))

        # Test coverage analysis
        debt_items.extend(self._analyze_test_coverage(code, language, filename))

        # Documentation analysis
        debt_items.extend(self._analyze_documentation(code, lines, language, filename))

        # Calculate metrics
        total_hours = sum(item.estimated_effort_hours for item in debt_items)
        debt_score = self._calculate_debt_score(debt_items, len(lines))

        # Breakdown by type and severity
        by_type = {}
        by_severity = {}

        for item in debt_items:
            by_type[item.debt_type] = by_type.get(item.debt_type, 0) + 1
            by_severity[item.severity] = by_severity.get(item.severity, 0) + 1

        # Priority list (sorted by impact and severity)
        priority_list = sorted(
            debt_items,
            key=lambda x: (
                self._severity_priority(x.severity),
                -x.impact_score,
                -x.estimated_effort_hours
            )
        )

        execution_time = (datetime.now() - start_time).total_seconds()

        return TechnicalDebtReport(
            total_items=len(debt_items),
            total_estimated_hours=total_hours,
            total_debt_score=debt_score,
            items=debt_items,
            breakdown_by_type=by_type,
            breakdown_by_severity=by_severity,
            priority_list=priority_list[:20],  # Top 20
            analysis_time=execution_time,
            metadata={
                'filename': filename,
                'language': language,
                'total_lines': len(lines),
                'timestamp': datetime.now().isoformat()
            }
        )

    def _detect_by_patterns(
        self,
        code: str,
        lines: List[str],
        language: str,
        filename: Optional[str]
    ) -> List[TechnicalDebtItem]:
        """Detect debt using pattern matching."""
        items = []

        # Get patterns for language and generic patterns
        patterns = self.patterns.get('all', []) + self.patterns.get(language.lower(), [])

        for pattern_def in patterns:
            pattern = pattern_def['pattern']

            for match in re.finditer(pattern, code):
                line_num = code[:match.start()].count('\n') + 1

                location = f"{filename}:{line_num}" if filename else f"Line {line_num}"

                # Extract context from match if available
                context = match.group(1) if match.groups() else match.group(0)

                item = TechnicalDebtItem(
                    debt_type=pattern_def['type'],
                    severity=pattern_def['severity'],
                    title=pattern_def['title'],
                    description=f"{pattern_def['title']}: {context[:100]}",
                    location=location,
                    estimated_effort_hours=pattern_def.get('effort_hours', 1.0),
                    impact_score=self._calculate_impact(pattern_def['type']),
                    interest_rate=self._calculate_interest_rate(pattern_def['type']),
                    created_date=datetime.now()
                )

                items.append(item)

        return items

    def _detect_duplication(
        self,
        lines: List[str],
        filename: Optional[str]
    ) -> List[TechnicalDebtItem]:
        """Detect code duplication."""
        items = []

        # Simple duplication detection: look for repeated line sequences
        min_duplicate_lines = 5
        line_sequences = {}

        for i in range(len(lines) - min_duplicate_lines + 1):
            # Get sequence of lines
            sequence = tuple(line.strip() for line in lines[i:i+min_duplicate_lines] if line.strip())

            if len(sequence) == min_duplicate_lines:
                if sequence in line_sequences:
                    # Found duplicate
                    original_line = line_sequences[sequence]

                    location = f"{filename}:{i+1}" if filename else f"Line {i+1}"

                    items.append(TechnicalDebtItem(
                        debt_type=DebtType.CODE_DUPLICATION,
                        severity=DebtSeverity.MEDIUM,
                        title="Duplicated code block",
                        description=f"Code duplicated from line {original_line}",
                        location=location,
                        estimated_effort_hours=3.0,
                        impact_score=6.0,
                        interest_rate=0.5,
                        metadata={'duplicate_of': original_line, 'lines': min_duplicate_lines}
                    ))
                else:
                    line_sequences[sequence] = i + 1

        return items

    def _detect_complexity(
        self,
        code: str,
        lines: List[str],
        language: str,
        filename: Optional[str]
    ) -> List[TechnicalDebtItem]:
        """Detect complex code that needs refactoring."""
        items = []

        # Detect long functions
        if language == 'python':
            func_pattern = r'def\s+(\w+)\s*\([^)]*\):'

            for match in re.finditer(func_pattern, code):
                func_name = match.group(1)
                func_start = match.start()
                line_num = code[:func_start].count('\n') + 1

                # Find function end
                func_end = re.search(r'\ndef\s+\w+', code[match.end():])
                if func_end:
                    func_code = code[func_start:match.end() + func_end.start()]
                else:
                    func_code = code[func_start:]

                func_lines = func_code.count('\n')

                # Check if function is too long
                if func_lines > 50:
                    location = f"{filename}:{line_num}" if filename else f"Line {line_num}"

                    items.append(TechnicalDebtItem(
                        debt_type=DebtType.COMPLEX_CODE,
                        severity=DebtSeverity.MEDIUM if func_lines < 100 else DebtSeverity.HIGH,
                        title=f"Long function: {func_name}",
                        description=f"Function has {func_lines} lines (recommended: <50)",
                        location=location,
                        estimated_effort_hours=4.0,
                        impact_score=7.0,
                        interest_rate=0.75,
                        metadata={'function_name': func_name, 'lines': func_lines}
                    ))

                # Check cyclomatic complexity
                complexity = self._calculate_cyclomatic_complexity(func_code)
                if complexity > 10:
                    location = f"{filename}:{line_num}" if filename else f"Line {line_num}"

                    items.append(TechnicalDebtItem(
                        debt_type=DebtType.COMPLEX_CODE,
                        severity=DebtSeverity.HIGH if complexity > 20 else DebtSeverity.MEDIUM,
                        title=f"High complexity: {func_name}",
                        description=f"Cyclomatic complexity: {complexity} (recommended: <10)",
                        location=location,
                        estimated_effort_hours=5.0,
                        impact_score=8.0,
                        interest_rate=1.0,
                        metadata={'function_name': func_name, 'complexity': complexity}
                    ))

        return items

    def _analyze_test_coverage(
        self,
        code: str,
        language: str,
        filename: Optional[str]
    ) -> List[TechnicalDebtItem]:
        """Analyze test coverage and identify missing tests."""
        items = []

        # Check if this is a test file
        if filename and ('test_' in filename or '_test' in filename or 'spec' in filename):
            return items

        # Look for functions without tests
        if language == 'python':
            # Find all functions
            func_pattern = r'def\s+(\w+)\s*\([^)]*\):'
            functions = re.findall(func_pattern, code)

            # Heuristic: if file has no corresponding test file, likely has missing tests
            if len(functions) > 0:
                items.append(TechnicalDebtItem(
                    debt_type=DebtType.MISSING_TESTS,
                    severity=DebtSeverity.HIGH,
                    title="Missing test coverage",
                    description=f"File has {len(functions)} functions that may lack tests",
                    location=filename or "Unknown file",
                    estimated_effort_hours=len(functions) * 1.5,
                    impact_score=9.0,
                    interest_rate=1.5,
                    metadata={'function_count': len(functions)}
                ))

        return items

    def _analyze_documentation(
        self,
        code: str,
        lines: List[str],
        language: str,
        filename: Optional[str]
    ) -> List[TechnicalDebtItem]:
        """Analyze documentation quality."""
        items = []

        if language == 'python':
            # Find functions without docstrings
            func_pattern = r'def\s+(\w+)\s*\([^)]*\):\s*\n\s*(?!"""|\'\'\')(?!\s*pass)'

            for match in re.finditer(func_pattern, code):
                func_name = match.group(1)
                line_num = code[:match.start()].count('\n') + 1

                # Skip private functions (starting with _)
                if not func_name.startswith('_'):
                    location = f"{filename}:{line_num}" if filename else f"Line {line_num}"

                    items.append(TechnicalDebtItem(
                        debt_type=DebtType.POOR_DOCUMENTATION,
                        severity=DebtSeverity.LOW,
                        title=f"Missing docstring: {func_name}",
                        description=f"Public function {func_name} lacks documentation",
                        location=location,
                        estimated_effort_hours=0.5,
                        impact_score=4.0,
                        interest_rate=0.25,
                        metadata={'function_name': func_name}
                    ))

        return items

    def _calculate_cyclomatic_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity (simplified)."""
        # Count decision points
        decision_keywords = [
            'if', 'elif', 'else', 'for', 'while',
            'and', 'or', 'try', 'except', 'with'
        ]

        complexity = 1  # Base complexity

        for keyword in decision_keywords:
            # Count occurrences as whole words only
            pattern = r'\b' + keyword + r'\b'
            complexity += len(re.findall(pattern, code))

        return complexity

    def _calculate_impact(self, debt_type: DebtType) -> float:
        """Calculate impact score for debt type (0-10)."""
        impact_scores = {
            DebtType.SECURITY_VULNERABILITIES: 10.0,
            DebtType.MISSING_TESTS: 9.0,
            DebtType.COMPLEX_CODE: 8.0,
            DebtType.CODE_DUPLICATION: 7.0,
            DebtType.PERFORMANCE_ISSUES: 7.0,
            DebtType.DEPRECATED_API: 6.0,
            DebtType.OUTDATED_DEPENDENCIES: 6.0,
            DebtType.POOR_DOCUMENTATION: 4.0,
            DebtType.INCONSISTENT_STYLE: 3.0,
            DebtType.TODO_COMMENTS: 2.0
        }

        return impact_scores.get(debt_type, 5.0)

    def _calculate_interest_rate(self, debt_type: DebtType) -> float:
        """Calculate interest rate (cost per month if unfixed)."""
        interest_rates = {
            DebtType.SECURITY_VULNERABILITIES: 2.0,
            DebtType.PERFORMANCE_ISSUES: 1.5,
            DebtType.COMPLEX_CODE: 1.0,
            DebtType.MISSING_TESTS: 1.0,
            DebtType.CODE_DUPLICATION: 0.75,
            DebtType.DEPRECATED_API: 0.5,
            DebtType.POOR_DOCUMENTATION: 0.25,
            DebtType.TODO_COMMENTS: 0.1
        }

        return interest_rates.get(debt_type, 0.5)

    def _severity_priority(self, severity: DebtSeverity) -> int:
        """Convert severity to priority number (lower = higher priority)."""
        priorities = {
            DebtSeverity.CRITICAL: 1,
            DebtSeverity.HIGH: 2,
            DebtSeverity.MEDIUM: 3,
            DebtSeverity.LOW: 4,
            DebtSeverity.TRIVIAL: 5
        }

        return priorities.get(severity, 3)

    def _calculate_debt_score(
        self,
        items: List[TechnicalDebtItem],
        total_lines: int
    ) -> float:
        """Calculate overall technical debt score (0-100)."""
        if not items:
            return 0.0

        # Weight by severity and impact
        severity_weights = {
            DebtSeverity.CRITICAL: 10,
            DebtSeverity.HIGH: 7,
            DebtSeverity.MEDIUM: 4,
            DebtSeverity.LOW: 2,
            DebtSeverity.TRIVIAL: 1
        }

        total_debt = 0.0
        for item in items:
            weight = severity_weights.get(item.severity, 1)
            total_debt += weight * item.impact_score

        # Normalize by lines of code
        debt_per_line = total_debt / max(1, total_lines)

        # Scale to 0-100
        debt_score = min(100.0, debt_per_line * 10)

        return debt_score

    def format_report(self, report: TechnicalDebtReport) -> str:
        """Format technical debt report as text."""
        lines = [
            "=" * 80,
            "TECHNICAL DEBT ANALYSIS REPORT",
            "=" * 80,
            "",
            f"Total Debt Items: {report.total_items}",
            f"Estimated Effort: {report.total_estimated_hours:.1f} hours",
            f"Debt Score: {report.total_debt_score:.1f}/100",
            "",
            "BREAKDOWN BY TYPE:",
        ]

        for debt_type, count in sorted(report.breakdown_by_type.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  {debt_type.value}: {count}")

        lines.append("")
        lines.append("BREAKDOWN BY SEVERITY:")

        for severity in [DebtSeverity.CRITICAL, DebtSeverity.HIGH, DebtSeverity.MEDIUM, DebtSeverity.LOW, DebtSeverity.TRIVIAL]:
            count = report.breakdown_by_severity.get(severity, 0)
            if count > 0:
                lines.append(f"  {severity.value.upper()}: {count}")

        if report.priority_list:
            lines.append("")
            lines.append("TOP PRIORITIES:")
            lines.append("")

            for i, item in enumerate(report.priority_list[:10], 1):
                icon = {
                    DebtSeverity.CRITICAL: "🔴",
                    DebtSeverity.HIGH: "🟠",
                    DebtSeverity.MEDIUM: "🟡",
                    DebtSeverity.LOW: "🟢",
                    DebtSeverity.TRIVIAL: "⚪"
                }.get(item.severity, "•")

                lines.append(f"{i}. {icon} [{item.severity.value.upper()}] {item.title}")
                lines.append(f"   Location: {item.location}")
                lines.append(f"   Effort: {item.estimated_effort_hours:.1f}h | Impact: {item.impact_score:.1f}/10")
                lines.append(f"   {item.description}")
                lines.append("")

        lines.append("=" * 80)

        return "\n".join(lines)


# Singleton instance
_analyzer_instance = None


def get_technical_debt_analyzer() -> TechnicalDebtAnalyzer:
    """Get singleton instance of technical debt analyzer."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = TechnicalDebtAnalyzer()
    return _analyzer_instance
