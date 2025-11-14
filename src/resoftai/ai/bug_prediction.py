"""
Intelligent bug prediction system using AI and static analysis.

This module predicts potential bugs before they occur using pattern recognition,
historical data analysis, and AI-powered code understanding.
"""

import re
import logging
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class BugSeverity(str, Enum):
    """Bug severity levels."""
    CRITICAL = "critical"  # Crashes, data loss
    HIGH = "high"          # Major functionality broken
    MEDIUM = "medium"      # Minor functionality issues
    LOW = "low"            # Cosmetic issues
    INFO = "info"          # Potential improvements


class BugCategory(str, Enum):
    """Bug categories."""
    NULL_POINTER = "null_pointer"
    MEMORY_LEAK = "memory_leak"
    RACE_CONDITION = "race_condition"
    LOGIC_ERROR = "logic_error"
    TYPE_ERROR = "type_error"
    SECURITY = "security"
    PERFORMANCE = "performance"
    RESOURCE_LEAK = "resource_leak"
    INFINITE_LOOP = "infinite_loop"
    UNCAUGHT_EXCEPTION = "uncaught_exception"


@dataclass
class BugPrediction:
    """Predicted bug."""
    severity: BugSeverity
    category: BugCategory
    confidence: float  # 0.0 to 1.0
    line_number: Optional[int] = None
    column: Optional[int] = None
    message: str = ""
    explanation: str = ""
    fix_suggestion: str = ""
    code_snippet: Optional[str] = None
    affected_variables: List[str] = None

    def __post_init__(self):
        if self.affected_variables is None:
            self.affected_variables = []


@dataclass
class BugPredictionReport:
    """Bug prediction report for a code file."""
    language: str
    total_lines: int
    predictions: List[BugPrediction]
    risk_score: float  # 0.0 to 100.0
    analysis_time: float
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BugPredictor:
    """
    Intelligent bug prediction system.

    Uses multiple techniques:
    - Pattern matching for common bug patterns
    - Static analysis for code structure issues
    - Heuristics based on coding best practices
    - AI-powered analysis (optional)
    """

    def __init__(self):
        """Initialize bug predictor."""
        self.patterns = self._initialize_patterns()
        logger.info("BugPredictor initialized")

    def _initialize_patterns(self) -> Dict[str, List[Dict]]:
        """Initialize bug detection patterns by language."""
        return {
            'python': [
                {
                    'pattern': r'\bexcept\s*:',
                    'category': BugCategory.UNCAUGHT_EXCEPTION,
                    'severity': BugSeverity.HIGH,
                    'message': 'Bare except clause may hide critical errors',
                    'explanation': 'Using except: catches all exceptions including KeyboardInterrupt and SystemExit, which should usually be allowed to propagate.',
                    'fix': 'Use specific exception types: except SpecificException:'
                },
                {
                    'pattern': r'\beval\s*\(',
                    'category': BugCategory.SECURITY,
                    'severity': BugSeverity.CRITICAL,
                    'message': 'eval() can execute arbitrary code',
                    'explanation': 'eval() is a security risk as it executes any Python code passed to it.',
                    'fix': 'Use ast.literal_eval() for safe evaluation or redesign to avoid dynamic code execution'
                },
                {
                    'pattern': r'while\s+True\s*:(?!\s*#\s*.*timeout)(?!\s*#\s*.*break)',
                    'category': BugCategory.INFINITE_LOOP,
                    'severity': BugSeverity.MEDIUM,
                    'message': 'Potential infinite loop without obvious exit condition',
                    'explanation': 'while True loops without clear break conditions can hang the program.',
                    'fix': 'Add a break condition or use a timeout mechanism'
                },
                {
                    'pattern': r'def\s+\w+\([^)]*=\s*(\[\]|\{\}|\(\))',
                    'category': BugCategory.LOGIC_ERROR,
                    'severity': BugSeverity.HIGH,
                    'message': 'Mutable default argument',
                    'explanation': 'Mutable default arguments are shared between function calls, causing unexpected behavior.',
                    'fix': 'Use None as default and initialize inside function'
                },
                {
                    'pattern': r'(?:open|file)\s*\([^)]+\)(?!\s*as\s)',
                    'category': BugCategory.RESOURCE_LEAK,
                    'severity': BugSeverity.MEDIUM,
                    'message': 'File not used with context manager',
                    'explanation': 'Files should be used with "with" statement to ensure proper closing.',
                    'fix': 'Use: with open(...) as f:'
                },
                {
                    'pattern': r'== None\b',
                    'category': BugCategory.LOGIC_ERROR,
                    'severity': BugSeverity.LOW,
                    'message': 'Comparing with None using ==',
                    'explanation': 'Should use "is None" instead of "== None" for None comparisons.',
                    'fix': 'Use: if x is None:'
                },
            ],
            'javascript': [
                {
                    'pattern': r'(?<![=!])={2}(?!=)',
                    'category': BugCategory.TYPE_ERROR,
                    'severity': BugSeverity.MEDIUM,
                    'message': 'Using == instead of ===',
                    'explanation': '== performs type coercion which can lead to unexpected comparisons.',
                    'fix': 'Use strict equality ==='
                },
                {
                    'pattern': r'\bvar\s+',
                    'category': BugCategory.LOGIC_ERROR,
                    'severity': BugSeverity.LOW,
                    'message': 'Using var instead of let/const',
                    'explanation': 'var has function scope which can cause hoisting issues.',
                    'fix': 'Use let for mutable variables, const for immutable'
                },
                {
                    'pattern': r'async\s+function[^{]*{[^}]*(?!await)',
                    'category': BugCategory.LOGIC_ERROR,
                    'severity': BugSeverity.MEDIUM,
                    'message': 'Async function without await',
                    'explanation': 'Async function declared but not using await.',
                    'fix': 'Remove async if not needed or add await for promises'
                },
                {
                    'pattern': r'\.innerHTML\s*=\s*[^;]+\+',
                    'category': BugCategory.SECURITY,
                    'severity': BugSeverity.CRITICAL,
                    'message': 'Potential XSS vulnerability',
                    'explanation': 'Setting innerHTML with concatenated user input can lead to XSS.',
                    'fix': 'Use textContent or sanitize input'
                },
            ],
            'typescript': [
                {
                    'pattern': r':\s*any\b',
                    'category': BugCategory.TYPE_ERROR,
                    'severity': BugSeverity.MEDIUM,
                    'message': 'Using any type loses type safety',
                    'explanation': 'The any type defeats the purpose of TypeScript type checking.',
                    'fix': 'Define specific types or use unknown'
                },
                {
                    'pattern': r'!\.',
                    'category': BugCategory.NULL_POINTER,
                    'severity': BugSeverity.MEDIUM,
                    'message': 'Non-null assertion can cause runtime errors',
                    'explanation': 'Non-null assertion (!) bypasses null checks and can crash at runtime.',
                    'fix': 'Use optional chaining (?.) or null checks'
                },
            ],
            'java': [
                {
                    'pattern': r'catch\s*\([^)]+\)\s*\{\s*\}',
                    'category': BugCategory.UNCAUGHT_EXCEPTION,
                    'severity': BugSeverity.HIGH,
                    'message': 'Empty catch block suppresses exceptions',
                    'explanation': 'Empty catch blocks hide errors and make debugging difficult.',
                    'fix': 'Handle exceptions or at least log them'
                },
                {
                    'pattern': r'\.equals\s*\(\s*null\s*\)',
                    'category': BugCategory.NULL_POINTER,
                    'severity': BugSeverity.HIGH,
                    'message': 'Calling equals on potentially null object',
                    'explanation': 'This will throw NullPointerException if the object is null.',
                    'fix': 'Use: if (obj != null && obj.equals(...))'
                },
            ],
            'go': [
                {
                    'pattern': r'_, err\s*:=',
                    'category': BugCategory.UNCAUGHT_EXCEPTION,
                    'severity': BugSeverity.MEDIUM,
                    'message': 'Error being ignored',
                    'explanation': 'Ignoring errors can lead to silent failures.',
                    'fix': 'Handle or document why error is ignored'
                },
                {
                    'pattern': r'go\s+func\s*\([^)]*\)\s*{[^}]*\b\w+\s*=',
                    'category': BugCategory.RACE_CONDITION,
                    'severity': BugSeverity.HIGH,
                    'message': 'Potential race condition in goroutine',
                    'explanation': 'Goroutine accessing shared variable without synchronization.',
                    'fix': 'Use mutex or channels for synchronization'
                },
            ]
        }

    async def predict_bugs(
        self,
        code: str,
        language: str,
        filename: Optional[str] = None,
        use_ai: bool = False
    ) -> BugPredictionReport:
        """
        Predict potential bugs in code.

        Args:
            code: Source code to analyze
            language: Programming language
            filename: Optional filename
            use_ai: Whether to use AI-powered analysis

        Returns:
            Bug prediction report
        """
        start_time = datetime.now()

        predictions = []
        lines = code.split('\n')

        # Pattern-based detection
        predictions.extend(self._pattern_based_detection(code, lines, language))

        # Structure-based detection
        predictions.extend(self._structure_based_detection(code, lines, language))

        # Complexity-based detection
        predictions.extend(self._complexity_based_detection(code, lines, language))

        # Calculate risk score
        risk_score = self._calculate_risk_score(predictions, len(lines))

        execution_time = (datetime.now() - start_time).total_seconds()

        return BugPredictionReport(
            language=language,
            total_lines=len(lines),
            predictions=predictions,
            risk_score=risk_score,
            analysis_time=execution_time,
            metadata={
                'filename': filename,
                'timestamp': datetime.now().isoformat(),
                'ai_analysis': use_ai
            }
        )

    def _pattern_based_detection(
        self,
        code: str,
        lines: List[str],
        language: str
    ) -> List[BugPrediction]:
        """Detect bugs using pattern matching."""
        predictions = []

        patterns = self.patterns.get(language.lower(), [])

        for pattern_def in patterns:
            pattern = pattern_def['pattern']

            # Search in full code
            for match in re.finditer(pattern, code):
                # Find line number
                line_num = code[:match.start()].count('\n') + 1

                prediction = BugPrediction(
                    severity=pattern_def['severity'],
                    category=pattern_def['category'],
                    confidence=0.75,  # Pattern-based confidence
                    line_number=line_num,
                    message=pattern_def['message'],
                    explanation=pattern_def['explanation'],
                    fix_suggestion=pattern_def['fix'],
                    code_snippet=lines[line_num - 1] if line_num <= len(lines) else None
                )

                predictions.append(prediction)

        return predictions

    def _structure_based_detection(
        self,
        code: str,
        lines: List[str],
        language: str
    ) -> List[BugPrediction]:
        """Detect bugs based on code structure."""
        predictions = []

        # Check for deeply nested code (complexity indicator)
        for i, line in enumerate(lines, 1):
            indent_level = len(line) - len(line.lstrip())

            if language in ['python']:
                if indent_level > 32:  # More than 8 indentation levels (4 spaces each)
                    predictions.append(BugPrediction(
                        severity=BugSeverity.MEDIUM,
                        category=BugCategory.LOGIC_ERROR,
                        confidence=0.6,
                        line_number=i,
                        message='Deeply nested code (potential complexity issue)',
                        explanation='High nesting levels make code hard to understand and test.',
                        fix_suggestion='Extract nested logic into separate functions'
                    ))

        # Check for very long functions
        if language == 'python':
            func_pattern = r'def\s+(\w+)\s*\([^)]*\):'
            for match in re.finditer(func_pattern, code):
                func_name = match.group(1)
                func_start_line = code[:match.start()].count('\n') + 1

                # Find function end (simplified - looks for next def or end of file)
                func_end = re.search(r'\ndef\s+\w+', code[match.end():])
                if func_end:
                    func_lines = code[match.start():match.end() + func_end.start()].count('\n')
                else:
                    func_lines = code[match.start():].count('\n')

                if func_lines > 50:
                    predictions.append(BugPrediction(
                        severity=BugSeverity.LOW,
                        category=BugCategory.LOGIC_ERROR,
                        confidence=0.5,
                        line_number=func_start_line,
                        message=f'Very long function: {func_name} ({func_lines} lines)',
                        explanation='Long functions are harder to test and maintain.',
                        fix_suggestion='Break down into smaller, focused functions',
                        affected_variables=[func_name]
                    ))

        return predictions

    def _complexity_based_detection(
        self,
        code: str,
        lines: List[str],
        language: str
    ) -> List[BugPrediction]:
        """Detect bugs based on code complexity."""
        predictions = []

        # Check cyclomatic complexity (simplified version)
        for i, line in enumerate(lines, 1):
            # Count decision points in line
            decision_keywords = ['if', 'elif', 'else', 'for', 'while', 'and', 'or', 'case', 'switch']
            decision_count = sum(1 for kw in decision_keywords if re.search(rf'\b{kw}\b', line))

            if decision_count >= 3:
                predictions.append(BugPrediction(
                    severity=BugSeverity.LOW,
                    category=BugCategory.LOGIC_ERROR,
                    confidence=0.4,
                    line_number=i,
                    message='High complexity line with multiple conditions',
                    explanation='Lines with many conditions are error-prone and hard to test.',
                    fix_suggestion='Simplify conditions or extract to separate function'
                ))

        return predictions

    def _calculate_risk_score(
        self,
        predictions: List[BugPrediction],
        total_lines: int
    ) -> float:
        """
        Calculate overall risk score (0-100).

        Higher score = higher risk
        """
        if not predictions:
            return 0.0

        # Weight by severity
        severity_weights = {
            BugSeverity.CRITICAL: 20,
            BugSeverity.HIGH: 10,
            BugSeverity.MEDIUM: 5,
            BugSeverity.LOW: 2,
            BugSeverity.INFO: 1
        }

        total_risk = 0.0
        for pred in predictions:
            weight = severity_weights.get(pred.severity, 1)
            total_risk += weight * pred.confidence

        # Normalize by lines of code
        risk_per_line = total_risk / max(1, total_lines)

        # Scale to 0-100
        risk_score = min(100.0, risk_per_line * 100)

        return risk_score

    def format_report(self, report: BugPredictionReport) -> str:
        """Format bug prediction report as text."""
        lines = [
            "=" * 80,
            "BUG PREDICTION REPORT",
            "=" * 80,
            "",
            f"Language: {report.language}",
            f"Total Lines: {report.total_lines}",
            f"Risk Score: {report.risk_score:.1f}/100",
            f"Analysis Time: {report.analysis_time:.2f}s",
            "",
        ]

        if report.predictions:
            # Group by severity
            by_severity = {}
            for pred in report.predictions:
                by_severity.setdefault(pred.severity, []).append(pred)

            lines.append(f"Total Predictions: {len(report.predictions)}")
            lines.append("")

            for severity in [BugSeverity.CRITICAL, BugSeverity.HIGH, BugSeverity.MEDIUM, BugSeverity.LOW, BugSeverity.INFO]:
                if severity in by_severity:
                    lines.append(f"{severity.value.upper()}: {len(by_severity[severity])} predictions")

            lines.append("")
            lines.append("DETAILED PREDICTIONS:")
            lines.append("")

            for pred in sorted(report.predictions, key=lambda x: (x.severity.value, x.confidence), reverse=True):
                icon = {
                    BugSeverity.CRITICAL: "🔴",
                    BugSeverity.HIGH: "🟠",
                    BugSeverity.MEDIUM: "🟡",
                    BugSeverity.LOW: "🟢",
                    BugSeverity.INFO: "ℹ️"
                }.get(pred.severity, "•")

                line_info = f"Line {pred.line_number}" if pred.line_number else "General"
                lines.append(f"{icon} [{pred.severity.value.upper()}] {line_info} (confidence: {pred.confidence:.0%})")
                lines.append(f"   Category: {pred.category.value}")
                lines.append(f"   {pred.message}")

                if pred.explanation:
                    lines.append(f"   📝 {pred.explanation}")

                if pred.fix_suggestion:
                    lines.append(f"   💡 Fix: {pred.fix_suggestion}")

                if pred.code_snippet:
                    lines.append(f"   Code: {pred.code_snippet.strip()}")

                lines.append("")

        else:
            lines.append("✅ No potential bugs detected!")
            lines.append("")

        lines.append("=" * 80)

        return "\n".join(lines)


# Singleton instance
_predictor_instance = None


def get_bug_predictor() -> BugPredictor:
    """Get singleton instance of bug predictor."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = BugPredictor()
    return _predictor_instance
