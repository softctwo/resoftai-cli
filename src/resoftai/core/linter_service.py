"""
Code quality linter service integrating pylint, mypy, and eslint.

This module provides real-time code quality checking using industry-standard
linting tools for Python and JavaScript/TypeScript.
"""

import asyncio
import json
import logging
import os
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import subprocess

logger = logging.getLogger(__name__)


class LinterType(str, Enum):
    """Supported linter types."""
    PYLINT = "pylint"
    MYPY = "mypy"
    ESLINT = "eslint"


class IssueSeverity(str, Enum):
    """Issue severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    CONVENTION = "convention"
    REFACTOR = "refactor"


@dataclass
class LintIssue:
    """Represents a single linting issue."""
    severity: IssueSeverity
    message: str
    line: int
    column: int = 0
    rule_id: Optional[str] = None
    source: Optional[str] = None  # pylint, mypy, eslint


@dataclass
class LintResult:
    """Result from running a linter."""
    linter: LinterType
    success: bool
    issues: List[LintIssue] = field(default_factory=list)
    error_message: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeQualityResult:
    """Aggregated code quality result from all linters."""
    file_path: str
    language: str
    total_issues: int
    errors: int
    warnings: int
    info: int
    linter_results: List[LintResult] = field(default_factory=list)
    overall_score: float = 100.0  # 0-100


class LinterService:
    """
    Service for running code quality linters.

    Supports:
    - Python: pylint, mypy
    - JavaScript/TypeScript: eslint
    """

    def __init__(self) -> None:
        """Initialize linter service."""
        self.supported_linters = {
            "python": [LinterType.PYLINT, LinterType.MYPY],
            "javascript": [LinterType.ESLINT],
            "typescript": [LinterType.ESLINT],
        }

    async def check_code(
        self,
        code: str,
        language: str,
        filename: Optional[str] = None,
        linters: Optional[List[LinterType]] = None,
    ) -> CodeQualityResult:
        """
        Check code quality using appropriate linters.

        Args:
            code: Source code to check
            language: Programming language (python, javascript, typescript)
            filename: Optional filename for better context
            linters: Specific linters to use (defaults to all for language)

        Returns:
            Aggregated code quality result
        """
        language = language.lower()

        # Determine which linters to use
        if linters is None:
            linters = self.supported_linters.get(language, [])

        # Create temporary file for code
        temp_file = await self._create_temp_file(code, language, filename)

        try:
            # Run linters concurrently
            tasks = []
            for linter in linters:
                if linter == LinterType.PYLINT:
                    tasks.append(self._run_pylint(temp_file))
                elif linter == LinterType.MYPY:
                    tasks.append(self._run_mypy(temp_file))
                elif linter == LinterType.ESLINT:
                    tasks.append(self._run_eslint(temp_file))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            linter_results = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Linter error: {result}")
                    continue
                if isinstance(result, LintResult):
                    linter_results.append(result)

            # Calculate aggregated metrics
            return self._aggregate_results(
                file_path=filename or "inline_code",
                language=language,
                linter_results=linter_results
            )

        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_file}: {e}")

    async def _create_temp_file(
        self,
        code: str,
        language: str,
        filename: Optional[str] = None
    ) -> str:
        """Create temporary file with appropriate extension."""
        # Determine file extension
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "typescript": ".ts",
        }
        ext = extensions.get(language, ".txt")

        # Use provided filename or generate one
        if filename:
            base_name = Path(filename).stem
        else:
            base_name = "temp_code"

        # Create temp file
        fd, path = tempfile.mkstemp(suffix=ext, prefix=f"{base_name}_")
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(code)
        except Exception:
            os.close(fd)
            raise

        return path

    async def _run_pylint(self, file_path: str) -> LintResult:
        """
        Run pylint on Python code.

        Args:
            file_path: Path to file to check

        Returns:
            Lint result
        """
        import time
        start_time = time.time()

        try:
            # Run pylint with JSON output
            process = await asyncio.create_subprocess_exec(
                "pylint",
                file_path,
                "--output-format=json",
                "--score=no",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()
            execution_time = time.time() - start_time

            # Parse JSON output
            issues = []
            try:
                if stdout:
                    pylint_output = json.loads(stdout.decode())
                    for item in pylint_output:
                        severity = self._map_pylint_severity(item.get("type", ""))
                        issues.append(LintIssue(
                            severity=severity,
                            message=item.get("message", ""),
                            line=item.get("line", 0),
                            column=item.get("column", 0),
                            rule_id=item.get("message-id", ""),
                            source="pylint"
                        ))
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse pylint output: {e}")

            return LintResult(
                linter=LinterType.PYLINT,
                success=True,
                issues=issues,
                execution_time=execution_time,
                metadata={"return_code": process.returncode}
            )

        except FileNotFoundError:
            return LintResult(
                linter=LinterType.PYLINT,
                success=False,
                error_message="pylint not installed",
                execution_time=time.time() - start_time
            )
        except Exception as e:
            logger.error(f"Error running pylint: {e}")
            return LintResult(
                linter=LinterType.PYLINT,
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time
            )

    async def _run_mypy(self, file_path: str) -> LintResult:
        """
        Run mypy on Python code.

        Args:
            file_path: Path to file to check

        Returns:
            Lint result
        """
        import time
        start_time = time.time()

        try:
            # Run mypy with JSON output
            process = await asyncio.create_subprocess_exec(
                "mypy",
                file_path,
                "--no-error-summary",
                "--show-column-numbers",
                "--no-color-output",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()
            execution_time = time.time() - start_time

            # Parse mypy output (line format: file:line:col: severity: message)
            issues = []
            if stdout:
                for line in stdout.decode().strip().split('\n'):
                    if not line or ':' not in line:
                        continue

                    parts = line.split(':', 4)
                    if len(parts) >= 4:
                        try:
                            line_num = int(parts[1])
                            col_num = int(parts[2]) if parts[2].strip().isdigit() else 0
                            message = parts[-1].strip()

                            issues.append(LintIssue(
                                severity=IssueSeverity.ERROR,
                                message=message,
                                line=line_num,
                                column=col_num,
                                rule_id="type-check",
                                source="mypy"
                            ))
                        except (ValueError, IndexError):
                            continue

            return LintResult(
                linter=LinterType.MYPY,
                success=True,
                issues=issues,
                execution_time=execution_time,
                metadata={"return_code": process.returncode}
            )

        except FileNotFoundError:
            return LintResult(
                linter=LinterType.MYPY,
                success=False,
                error_message="mypy not installed",
                execution_time=time.time() - start_time
            )
        except Exception as e:
            logger.error(f"Error running mypy: {e}")
            return LintResult(
                linter=LinterType.MYPY,
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time
            )

    async def _run_eslint(self, file_path: str) -> LintResult:
        """
        Run eslint on JavaScript/TypeScript code.

        Args:
            file_path: Path to file to check

        Returns:
            Lint result
        """
        import time
        start_time = time.time()

        try:
            # Run eslint with JSON output
            process = await asyncio.create_subprocess_exec(
                "eslint",
                file_path,
                "--format=json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()
            execution_time = time.time() - start_time

            # Parse JSON output
            issues = []
            try:
                if stdout:
                    eslint_output = json.loads(stdout.decode())
                    for file_result in eslint_output:
                        for message in file_result.get("messages", []):
                            severity = self._map_eslint_severity(message.get("severity", 1))
                            issues.append(LintIssue(
                                severity=severity,
                                message=message.get("message", ""),
                                line=message.get("line", 0),
                                column=message.get("column", 0),
                                rule_id=message.get("ruleId", ""),
                                source="eslint"
                            ))
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse eslint output: {e}")

            return LintResult(
                linter=LinterType.ESLINT,
                success=True,
                issues=issues,
                execution_time=execution_time,
                metadata={"return_code": process.returncode}
            )

        except FileNotFoundError:
            return LintResult(
                linter=LinterType.ESLINT,
                success=False,
                error_message="eslint not installed",
                execution_time=time.time() - start_time
            )
        except Exception as e:
            logger.error(f"Error running eslint: {e}")
            return LintResult(
                linter=LinterType.ESLINT,
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time
            )

    def _map_pylint_severity(self, pylint_type: str) -> IssueSeverity:
        """Map pylint message type to severity."""
        mapping = {
            "error": IssueSeverity.ERROR,
            "fatal": IssueSeverity.ERROR,
            "warning": IssueSeverity.WARNING,
            "convention": IssueSeverity.CONVENTION,
            "refactor": IssueSeverity.REFACTOR,
            "info": IssueSeverity.INFO,
        }
        return mapping.get(pylint_type.lower(), IssueSeverity.WARNING)

    def _map_eslint_severity(self, severity_code: int) -> IssueSeverity:
        """Map eslint severity code to severity."""
        if severity_code == 2:
            return IssueSeverity.ERROR
        elif severity_code == 1:
            return IssueSeverity.WARNING
        else:
            return IssueSeverity.INFO

    def _aggregate_results(
        self,
        file_path: str,
        language: str,
        linter_results: List[LintResult]
    ) -> CodeQualityResult:
        """Aggregate results from multiple linters."""
        all_issues = []
        for result in linter_results:
            all_issues.extend(result.issues)

        # Count by severity
        errors = sum(1 for i in all_issues if i.severity == IssueSeverity.ERROR)
        warnings = sum(1 for i in all_issues
                      if i.severity in (IssueSeverity.WARNING, IssueSeverity.CONVENTION, IssueSeverity.REFACTOR))
        info = sum(1 for i in all_issues if i.severity == IssueSeverity.INFO)

        # Calculate score
        score = 100.0
        score -= errors * 10
        score -= warnings * 2
        score -= info * 0.5
        score = max(0.0, min(100.0, score))

        return CodeQualityResult(
            file_path=file_path,
            language=language,
            total_issues=len(all_issues),
            errors=errors,
            warnings=warnings,
            info=info,
            linter_results=linter_results,
            overall_score=score
        )


# Singleton instance
_linter_service: Optional[LinterService] = None


def get_linter_service() -> LinterService:
    """Get singleton linter service instance."""
    global _linter_service
    if _linter_service is None:
        _linter_service = LinterService()
    return _linter_service
