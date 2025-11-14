"""API routes for code analysis (pylint, mypy, eslint)."""
import asyncio
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from resoftai.db import get_db
from resoftai.auth.dependencies import get_current_active_user
from resoftai.models.user import User

router = APIRouter(prefix="/code-analysis", tags=["code-analysis"])


# Request/Response Models
class CodeAnalysisRequest(BaseModel):
    """Request for code analysis."""
    code: str = Field(..., description="Code content to analyze")
    language: str = Field(..., description="Programming language (python, javascript, typescript)")
    filename: str = Field(default="temp", description="Filename for context")
    tools: List[str] = Field(default=["all"], description="Analysis tools to run (pylint, mypy, eslint, or all)")


class AnalysisIssue(BaseModel):
    """Single analysis issue."""
    line: Optional[int] = None
    column: Optional[int] = None
    severity: str  # error, warning, info
    message: str
    rule: Optional[str] = None
    tool: str


class CodeAnalysisResponse(BaseModel):
    """Response from code analysis."""
    success: bool
    language: str
    issues: List[AnalysisIssue]
    summary: Dict[str, int]  # {error: count, warning: count, info: count}
    score: Optional[float] = None  # For pylint
    execution_time: float  # seconds


async def run_pylint(code: str, filename: str) -> Dict:
    """Run pylint analysis on Python code."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_file = Path(tmpdir) / f"{filename}.py"
        temp_file.write_text(code, encoding='utf-8')

        try:
            # Run pylint with JSON output
            result = await asyncio.create_subprocess_exec(
                'pylint',
                str(temp_file),
                '--output-format=json',
                '--rcfile=.pylintrc',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await result.communicate()

            issues = []
            score = None

            if stdout:
                try:
                    pylint_output = json.loads(stdout.decode())
                    for issue in pylint_output:
                        issues.append(AnalysisIssue(
                            line=issue.get('line'),
                            column=issue.get('column'),
                            severity='error' if issue.get('type') == 'error' else 'warning',
                            message=issue.get('message', ''),
                            rule=issue.get('message-id'),
                            tool='pylint'
                        ))
                except json.JSONDecodeError:
                    pass

            # Extract score from stderr (if present)
            if stderr:
                stderr_text = stderr.decode()
                if 'rated at' in stderr_text:
                    try:
                        score_line = [line for line in stderr_text.split('\n') if 'rated at' in line][0]
                        score = float(score_line.split('rated at ')[1].split('/')[0])
                    except (IndexError, ValueError):
                        pass

            return {
                'success': True,
                'issues': issues,
                'score': score
            }

        except FileNotFoundError:
            raise HTTPException(status_code=500, detail="pylint not installed")
        except Exception as e:
            return {
                'success': False,
                'issues': [AnalysisIssue(
                    line=None,
                    column=None,
                    severity='error',
                    message=f"Pylint execution error: {str(e)}",
                    rule=None,
                    tool='pylint'
                )],
                'score': None
            }


async def run_mypy(code: str, filename: str) -> Dict:
    """Run mypy type checking on Python code."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_file = Path(tmpdir) / f"{filename}.py"
        temp_file.write_text(code, encoding='utf-8')

        try:
            # Run mypy with JSON output
            result = await asyncio.create_subprocess_exec(
                'mypy',
                str(temp_file),
                '--config-file=mypy.ini',
                '--show-column-numbers',
                '--show-error-codes',
                '--no-error-summary',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await result.communicate()

            issues = []

            if stdout:
                output_text = stdout.decode()
                for line in output_text.strip().split('\n'):
                    if line and ':' in line:
                        try:
                            # Parse mypy output: filename:line:col: severity: message [error-code]
                            parts = line.split(':', 4)
                            if len(parts) >= 4:
                                line_num = int(parts[1]) if parts[1].isdigit() else None
                                col_num = int(parts[2]) if parts[2].isdigit() else None
                                rest = parts[3] if len(parts) == 4 else parts[4]

                                severity = 'error'
                                if 'note:' in rest.lower():
                                    severity = 'info'
                                elif 'warning:' in rest.lower():
                                    severity = 'warning'

                                # Extract error code if present
                                rule = None
                                if '[' in rest and ']' in rest:
                                    rule = rest[rest.rfind('[') + 1:rest.rfind(']')]

                                message = rest.strip()

                                issues.append(AnalysisIssue(
                                    line=line_num,
                                    column=col_num,
                                    severity=severity,
                                    message=message,
                                    rule=rule,
                                    tool='mypy'
                                ))
                        except (ValueError, IndexError):
                            continue

            return {
                'success': True,
                'issues': issues
            }

        except FileNotFoundError:
            raise HTTPException(status_code=500, detail="mypy not installed")
        except Exception as e:
            return {
                'success': False,
                'issues': [AnalysisIssue(
                    line=None,
                    column=None,
                    severity='error',
                    message=f"Mypy execution error: {str(e)}",
                    rule=None,
                    tool='mypy'
                )]
            }


async def run_eslint(code: str, filename: str) -> Dict:
    """Run eslint analysis on JavaScript/TypeScript code."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ext = '.js'
        if 'typescript' in filename.lower() or filename.endswith('.ts'):
            ext = '.ts'
        elif filename.endswith('.vue'):
            ext = '.vue'

        temp_file = Path(tmpdir) / f"{filename}{ext}"
        temp_file.write_text(code, encoding='utf-8')

        try:
            # Run eslint with JSON output
            result = await asyncio.create_subprocess_exec(
                'npx',
                'eslint',
                str(temp_file),
                '--format=json',
                '--config=frontend/.eslintrc.cjs',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd='/home/user/resoftai-cli'
            )

            stdout, stderr = await result.communicate()

            issues = []

            if stdout:
                try:
                    eslint_output = json.loads(stdout.decode())
                    if eslint_output and len(eslint_output) > 0:
                        for message in eslint_output[0].get('messages', []):
                            severity_map = {
                                2: 'error',
                                1: 'warning',
                                0: 'info'
                            }
                            issues.append(AnalysisIssue(
                                line=message.get('line'),
                                column=message.get('column'),
                                severity=severity_map.get(message.get('severity', 1), 'warning'),
                                message=message.get('message', ''),
                                rule=message.get('ruleId'),
                                tool='eslint'
                            ))
                except json.JSONDecodeError:
                    pass

            return {
                'success': True,
                'issues': issues
            }

        except FileNotFoundError:
            raise HTTPException(status_code=500, detail="eslint not installed")
        except Exception as e:
            return {
                'success': False,
                'issues': [AnalysisIssue(
                    line=None,
                    column=None,
                    severity='error',
                    message=f"ESLint execution error: {str(e)}",
                    rule=None,
                    tool='eslint'
                )]
            }


@router.post("/analyze", response_model=CodeAnalysisResponse)
async def analyze_code(
    request: CodeAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze code using static analysis tools.

    Supports:
    - Python: pylint, mypy
    - JavaScript/TypeScript: eslint
    """
    import time
    start_time = time.time()

    all_issues = []
    score = None

    # Determine which tools to run
    tools = request.tools
    if "all" in tools:
        if request.language.lower() == "python":
            tools = ["pylint", "mypy"]
        elif request.language.lower() in ["javascript", "typescript"]:
            tools = ["eslint"]
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language: {request.language}"
            )

    # Run Python analysis
    if request.language.lower() == "python":
        if "pylint" in tools:
            result = await run_pylint(request.code, request.filename)
            all_issues.extend(result['issues'])
            if result.get('score') is not None:
                score = result['score']

        if "mypy" in tools:
            result = await run_mypy(request.code, request.filename)
            all_issues.extend(result['issues'])

    # Run JavaScript/TypeScript analysis
    elif request.language.lower() in ["javascript", "typescript"]:
        if "eslint" in tools:
            result = await run_eslint(request.code, request.filename)
            all_issues.extend(result['issues'])

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language: {request.language}"
        )

    # Calculate summary
    summary = {
        'error': sum(1 for issue in all_issues if issue.severity == 'error'),
        'warning': sum(1 for issue in all_issues if issue.severity == 'warning'),
        'info': sum(1 for issue in all_issues if issue.severity == 'info')
    }

    execution_time = time.time() - start_time

    return CodeAnalysisResponse(
        success=True,
        language=request.language,
        issues=all_issues,
        summary=summary,
        score=score,
        execution_time=execution_time
    )


@router.get("/tools")
async def get_available_tools(
    current_user: User = Depends(get_current_active_user)
):
    """Get list of available analysis tools."""
    tools = {
        "python": [],
        "javascript": [],
        "typescript": []
    }

    # Check if pylint is available
    try:
        result = subprocess.run(['pylint', '--version'], capture_output=True, timeout=5)
        if result.returncode == 0:
            tools["python"].append({
                "name": "pylint",
                "version": result.stdout.decode().split('\n')[0]
            })
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Check if mypy is available
    try:
        result = subprocess.run(['mypy', '--version'], capture_output=True, timeout=5)
        if result.returncode == 0:
            tools["python"].append({
                "name": "mypy",
                "version": result.stdout.decode().strip()
            })
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Check if eslint is available
    try:
        result = subprocess.run(['npx', 'eslint', '--version'], capture_output=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.decode().strip()
            tools["javascript"].append({"name": "eslint", "version": version})
            tools["typescript"].append({"name": "eslint", "version": version})
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return {
        "available_tools": tools,
        "supported_languages": ["python", "javascript", "typescript"]
    }
