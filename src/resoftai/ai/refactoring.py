"""
Automatic refactoring suggestions system.

This module analyzes code and provides actionable refactoring suggestions
to improve code quality, maintainability, and performance.
"""

import re
import logging
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class RefactoringType(str, Enum):
    """Types of refactoring suggestions."""
    EXTRACT_METHOD = "extract_method"
    RENAME = "rename"
    MOVE_METHOD = "move_method"
    REMOVE_DUPLICATION = "remove_duplication"
    SIMPLIFY_CONDITIONAL = "simplify_conditional"
    REPLACE_MAGIC_NUMBER = "replace_magic_number"
    INTRODUCE_PARAMETER = "introduce_parameter"
    REMOVE_DEAD_CODE = "remove_dead_code"
    OPTIMIZE_IMPORTS = "optimize_imports"
    MODERNIZE_CODE = "modernize_code"


@dataclass
class RefactoringSuggestion:
    """A single refactoring suggestion."""
    refactoring_type: RefactoringType
    title: str
    description: str
    location: str  # File:line or range
    current_code: str
    suggested_code: str
    rationale: str
    effort: str  # "trivial", "easy", "medium", "hard"
    benefits: List[str]
    risks: List[str] = None

    def __post_init__(self):
        if self.risks is None:
            self.risks = []


@dataclass
class RefactoringReport:
    """Refactoring analysis report."""
    total_suggestions: int
    suggestions: List[RefactoringSuggestion]
    by_type: Dict[RefactoringType, int]
    high_priority: List[RefactoringSuggestion]
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class RefactoringAnalyzer:
    """Analyze code and suggest refactorings."""

    def __init__(self):
        """Initialize refactoring analyzer."""
        logger.info("RefactoringAnalyzer initialized")

    async def analyze(
        self,
        code: str,
        language: str,
        filename: Optional[str] = None
    ) -> RefactoringReport:
        """
        Analyze code and generate refactoring suggestions.

        Args:
            code: Source code to analyze
            language: Programming language
            filename: Optional filename

        Returns:
            Refactoring report
        """
        suggestions = []

        # Detect various refactoring opportunities
        suggestions.extend(self._detect_extract_method(code, language))
        suggestions.extend(self._detect_magic_numbers(code, language))
        suggestions.extend(self._detect_complex_conditionals(code, language))
        suggestions.extend(self._detect_code_duplication(code, language))
        suggestions.extend(self._detect_modernization_opportunities(code, language))

        # Calculate breakdown
        by_type = {}
        for suggestion in suggestions:
            by_type[suggestion.refactoring_type] = by_type.get(suggestion.refactoring_type, 0) + 1

        # Identify high priority suggestions
        high_priority = [s for s in suggestions if s.effort in ["trivial", "easy"] and len(s.benefits) >= 2]

        return RefactoringReport(
            total_suggestions=len(suggestions),
            suggestions=suggestions,
            by_type=by_type,
            high_priority=high_priority[:10],
            metadata={'filename': filename, 'language': language}
        )

    def _detect_extract_method(self, code: str, language: str) -> List[RefactoringSuggestion]:
        """Detect opportunities to extract methods."""
        suggestions = []

        if language == 'python':
            # Look for long code blocks that could be extracted
            lines = code.split('\n')

            for i, line in enumerate(lines):
                # Look for comment blocks that indicate logical sections
                if line.strip().startswith('#') and len(line.strip()) > 10:
                    # This could be a candidate for extraction
                    suggestion = RefactoringSuggestion(
                        refactoring_type=RefactoringType.EXTRACT_METHOD,
                        title="Extract method",
                        description=f"Section starting at line {i+1} could be extracted into a separate method",
                        location=f"Line {i+1}",
                        current_code=line,
                        suggested_code=f"def {self._suggest_method_name(line)}():\n    # Implementation here",
                        rationale="Extracting this section would improve readability and reusability",
                        effort="medium",
                        benefits=["Improved readability", "Better testability", "Code reuse"]
                    )
                    suggestions.append(suggestion)

        return suggestions[:5]  # Limit to top 5

    def _detect_magic_numbers(self, code: str, language: str) -> List[RefactoringSuggestion]:
        """Detect magic numbers that should be constants."""
        suggestions = []

        # Find numeric literals (excluding 0, 1, -1 which are often fine)
        pattern = r'\b(?<![\d.])(([2-9]|\d{2,})(?:\.\d+)?)\b(?!\.)'

        for match in re.finditer(pattern, code):
            number = match.group(1)
            line_num = code[:match.start()].count('\n') + 1

            # Skip if already in a constant definition
            line_content = code.split('\n')[line_num - 1] if line_num <= len(code.split('\n')) else ""
            if 'const' in line_content.lower() or '=' in line_content and line_content.strip().isupper():
                continue

            constant_name = f"MAGIC_NUMBER_{number.replace('.', '_')}"

            suggestion = RefactoringSuggestion(
                refactoring_type=RefactoringType.REPLACE_MAGIC_NUMBER,
                title="Replace magic number with named constant",
                description=f"Magic number {number} at line {line_num}",
                location=f"Line {line_num}",
                current_code=f"... {number} ...",
                suggested_code=f"{constant_name} = {number}\n... {constant_name} ...",
                rationale="Named constants are more maintainable and self-documenting",
                effort="trivial",
                benefits=["Improved readability", "Easier maintenance", "Self-documenting code"]
            )
            suggestions.append(suggestion)

        return suggestions[:10]

    def _detect_complex_conditionals(self, code: str, language: str) -> List[RefactoringSuggestion]:
        """Detect complex conditionals that could be simplified."""
        suggestions = []

        # Look for conditions with multiple and/or operators
        if language in ['python', 'javascript', 'typescript']:
            pattern = r'if\s+(.{60,}):' if language == 'python' else r'if\s*\((.{60,})\)'

            for match in re.finditer(pattern, code):
                condition = match.group(1)
                line_num = code[:match.start()].count('\n') + 1

                # Count logical operators
                and_count = condition.count(' and ') + condition.count(' && ')
                or_count = condition.count(' or ') + condition.count(' || ')

                if and_count + or_count >= 3:
                    suggestion = RefactoringSuggestion(
                        refactoring_type=RefactoringType.SIMPLIFY_CONDITIONAL,
                        title="Simplify complex conditional",
                        description=f"Complex condition at line {line_num}",
                        location=f"Line {line_num}",
                        current_code=f"if {condition}:",
                        suggested_code="# Extract to well-named boolean variables or method",
                        rationale="Complex conditions are hard to understand and test",
                        effort="easy",
                        benefits=["Improved readability", "Easier testing", "Better maintainability"]
                    )
                    suggestions.append(suggestion)

        return suggestions[:5]

    def _detect_code_duplication(self, code: str, language: str) -> List[RefactoringSuggestion]:
        """Detect code duplication."""
        suggestions = []

        lines = code.split('\n')
        seen_sequences = {}

        # Look for repeated sequences of 3+ lines
        for i in range(len(lines) - 3):
            sequence = tuple(line.strip() for line in lines[i:i+3] if line.strip())

            if len(sequence) == 3 and sequence in seen_sequences:
                original_line = seen_sequences[sequence]

                suggestion = RefactoringSuggestion(
                    refactoring_type=RefactoringType.REMOVE_DUPLICATION,
                    title="Remove code duplication",
                    description=f"Duplicated code at lines {i+1} and {original_line}",
                    location=f"Lines {i+1}-{i+3}",
                    current_code="\n".join(lines[i:i+3]),
                    suggested_code="# Extract to shared method",
                    rationale="Duplicated code makes maintenance harder",
                    effort="medium",
                    benefits=["Reduced maintenance", "Single source of truth", "Smaller codebase"],
                    risks=["May need to handle slight variations"]
                )
                suggestions.append(suggestion)
            elif len(sequence) == 3:
                seen_sequences[sequence] = i + 1

        return suggestions[:5]

    def _detect_modernization_opportunities(self, code: str, language: str) -> List[RefactoringSuggestion]:
        """Detect opportunities to modernize code."""
        suggestions = []

        if language == 'python':
            # Check for old-style string formatting
            if '%' in code and 'format' not in code and 'f"' not in code:
                pattern = r'["\'].*%[sd].*["\']'
                if re.search(pattern, code):
                    suggestions.append(RefactoringSuggestion(
                        refactoring_type=RefactoringType.MODERNIZE_CODE,
                        title="Modernize string formatting",
                        description="Use f-strings instead of % formatting",
                        location="Multiple locations",
                        current_code='"%s %d" % (name, count)',
                        suggested_code='f"{name} {count}"',
                        rationale="F-strings are more readable and performant",
                        effort="trivial",
                        benefits=["Modern Python idiom", "Better readability", "Slightly faster"]
                    ))

        elif language in ['javascript', 'typescript']:
            # Check for var instead of let/const
            if re.search(r'\bvar\s+', code):
                suggestions.append(RefactoringSuggestion(
                    refactoring_type=RefactoringType.MODERNIZE_CODE,
                    title="Modernize variable declarations",
                    description="Use let/const instead of var",
                    location="Multiple locations",
                    current_code="var x = 10;",
                    suggested_code="const x = 10; // or let if mutable",
                    rationale="let/const have block scope and are ES6+ standard",
                    effort="trivial",
                    benefits=["Modern JavaScript", "Better scoping", "Prevents hoisting issues"]
                ))

        return suggestions

    def _suggest_method_name(self, comment: str) -> str:
        """Suggest a method name based on comment."""
        # Simple heuristic: extract words from comment
        words = re.findall(r'\w+', comment.lower())
        # Filter out common words
        filtered = [w for w in words if w not in {'a', 'an', 'the', 'is', 'are', 'and', 'or', 'to'}]
        # Take first few words
        name_parts = filtered[:3]
        return '_'.join(name_parts) if name_parts else 'extracted_method'

    def format_report(self, report: RefactoringReport) -> str:
        """Format refactoring report as text."""
        lines = [
            "=" * 80,
            "REFACTORING SUGGESTIONS REPORT",
            "=" * 80,
            "",
            f"Total Suggestions: {report.total_suggestions}",
            "",
            "BY TYPE:",
        ]

        for ref_type, count in sorted(report.by_type.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  {ref_type.value}: {count}")

        if report.high_priority:
            lines.append("")
            lines.append(f"HIGH PRIORITY (Quick wins): {len(report.high_priority)}")

        if report.suggestions:
            lines.append("")
            lines.append("DETAILED SUGGESTIONS:")
            lines.append("")

            for i, suggestion in enumerate(report.suggestions[:15], 1):
                lines.append(f"{i}. [{suggestion.refactoring_type.value}] {suggestion.title}")
                lines.append(f"   Location: {suggestion.location}")
                lines.append(f"   Effort: {suggestion.effort}")
                lines.append(f"   Rationale: {suggestion.rationale}")
                lines.append(f"   Benefits: {', '.join(suggestion.benefits)}")

                if suggestion.risks:
                    lines.append(f"   Risks: {', '.join(suggestion.risks)}")

                lines.append("")

        lines.append("=" * 80)

        return "\n".join(lines)


# Singleton instance
_refactoring_analyzer = None


def get_refactoring_analyzer() -> RefactoringAnalyzer:
    """Get singleton instance of refactoring analyzer."""
    global _refactoring_analyzer
    if _refactoring_analyzer is None:
        _refactoring_analyzer = RefactoringAnalyzer()
    return _refactoring_analyzer
