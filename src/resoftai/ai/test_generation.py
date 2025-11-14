"""
Automated test generation system.

This module automatically generates unit tests for source code using AI
and template-based approaches.
"""

import re
import logging
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime

from resoftai.llm.base import LLMProvider, LLMConfig

logger = logging.getLogger(__name__)


class TestFramework(str, Enum):
    """Supported test frameworks."""
    PYTEST = "pytest"
    UNITTEST = "unittest"
    JEST = "jest"
    MOCHA = "mocha"
    JUNIT = "junit"
    GOTEST = "gotest"


@dataclass
class FunctionInfo:
    """Information about a function to test."""
    name: str
    parameters: List[str]
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    line_number: int = 0
    is_async: bool = False


@dataclass
class GeneratedTest:
    """A generated test case."""
    test_name: str
    test_code: str
    description: str
    test_type: str  # "happy_path", "edge_case", "error_handling"
    confidence: float  # 0.0 to 1.0


@dataclass
class TestGenerationReport:
    """Test generation report."""
    source_file: str
    test_file: str
    framework: TestFramework
    functions_analyzed: int
    tests_generated: int
    generated_tests: List[GeneratedTest]
    full_test_code: str
    coverage_estimate: float  # Estimated coverage percentage
    generation_time: float


class TestGenerator:
    """
    Automated test generator.

    Generates unit tests for source code using templates and AI assistance.
    """

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        """
        Initialize test generator.

        Args:
            llm_provider: Optional LLM provider for AI-assisted generation
        """
        self.llm_provider = llm_provider
        logger.info("TestGenerator initialized")

    async def generate_tests(
        self,
        code: str,
        language: str,
        framework: TestFramework,
        filename: Optional[str] = None,
        use_ai: bool = False
    ) -> TestGenerationReport:
        """
        Generate tests for source code.

        Args:
            code: Source code to generate tests for
            language: Programming language
            framework: Test framework to use
            filename: Optional source filename
            use_ai: Whether to use AI for test generation

        Returns:
            Test generation report
        """
        start_time = datetime.now()

        # Extract functions from code
        functions = self._extract_functions(code, language)

        # Generate tests for each function
        generated_tests = []

        for func in functions:
            if use_ai and self.llm_provider:
                tests = await self._generate_tests_ai(func, code, language, framework)
            else:
                tests = self._generate_tests_template(func, language, framework)

            generated_tests.extend(tests)

        # Assemble full test file
        full_test_code = self._assemble_test_file(
            generated_tests,
            filename or "source.py",
            framework,
            language
        )

        # Estimate coverage
        coverage_estimate = self._estimate_coverage(len(generated_tests), len(functions))

        execution_time = (datetime.now() - start_time).total_seconds()

        test_filename = self._get_test_filename(filename or "source", language)

        return TestGenerationReport(
            source_file=filename or "source",
            test_file=test_filename,
            framework=framework,
            functions_analyzed=len(functions),
            tests_generated=len(generated_tests),
            generated_tests=generated_tests,
            full_test_code=full_test_code,
            coverage_estimate=coverage_estimate,
            generation_time=execution_time
        )

    def _extract_functions(self, code: str, language: str) -> List[FunctionInfo]:
        """Extract functions from source code."""
        functions = []

        if language == 'python':
            # Match function definitions
            pattern = r'(async\s+)?def\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*([^:]+))?:'

            for match in re.finditer(pattern, code):
                is_async = bool(match.group(1))
                func_name = match.group(2)
                params_str = match.group(3)
                return_type = match.group(4).strip() if match.group(4) else None

                # Parse parameters
                params = []
                if params_str.strip():
                    for param in params_str.split(','):
                        param = param.strip()
                        # Extract just the parameter name (before : or =)
                        param_name = re.split(r'[=:]', param)[0].strip()
                        if param_name and param_name != 'self' and param_name != 'cls':
                            params.append(param_name)

                # Try to extract docstring
                func_start = match.end()
                docstring_match = re.search(r'"""(.*?)"""', code[func_start:func_start+500], re.DOTALL)
                docstring = docstring_match.group(1).strip() if docstring_match else None

                line_number = code[:match.start()].count('\n') + 1

                functions.append(FunctionInfo(
                    name=func_name,
                    parameters=params,
                    return_type=return_type,
                    docstring=docstring,
                    line_number=line_number,
                    is_async=is_async
                ))

        elif language in ['javascript', 'typescript']:
            # Match function declarations and arrow functions
            patterns = [
                r'function\s+(\w+)\s*\(([^)]*)\)',
                r'const\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>',
                r'(\w+)\s*\(([^)]*)\)\s*{',  # Method definitions
            ]

            for pattern in patterns:
                for match in re.finditer(pattern, code):
                    func_name = match.group(1)
                    params_str = match.group(2)

                    params = [p.strip().split(':')[0].strip() for p in params_str.split(',') if p.strip()]

                    line_number = code[:match.start()].count('\n') + 1

                    functions.append(FunctionInfo(
                        name=func_name,
                        parameters=params,
                        line_number=line_number,
                        is_async='async' in code[max(0, match.start()-20):match.start()]
                    ))

        return functions

    async def _generate_tests_ai(
        self,
        func: FunctionInfo,
        code: str,
        language: str,
        framework: TestFramework
    ) -> List[GeneratedTest]:
        """Generate tests using AI."""
        prompt = f"""Generate comprehensive unit tests for this {language} function using {framework.value}:

Function: {func.name}
Parameters: {', '.join(func.parameters)}
Return Type: {func.return_type or 'unknown'}
{f"Description: {func.docstring}" if func.docstring else ""}

Please generate tests for:
1. Happy path / normal cases
2. Edge cases
3. Error handling

Generate 3-5 test cases in {framework.value} format."""

        try:
            response = await self.llm_provider.generate(prompt)

            # Parse AI response into test cases (simplified)
            tests = []

            # Simple parsing: look for test function definitions
            if framework == TestFramework.PYTEST:
                pattern = r'def (test_\w+)\([^)]*\):'

                for match in re.finditer(pattern, response.content):
                    test_name = match.group(1)

                    # Extract test code (simplified - gets until next def or end)
                    test_start = match.start()
                    next_test = re.search(r'\ndef test_', response.content[match.end():])
                    if next_test:
                        test_end = match.end() + next_test.start()
                    else:
                        test_end = len(response.content)

                    test_code = response.content[test_start:test_end].strip()

                    tests.append(GeneratedTest(
                        test_name=test_name,
                        test_code=test_code,
                        description=f"AI-generated test for {func.name}",
                        test_type="ai_generated",
                        confidence=0.8
                    ))

            return tests if tests else self._generate_tests_template(func, language, framework)

        except Exception as e:
            logger.error(f"AI test generation failed: {e}")
            # Fallback to template-based generation
            return self._generate_tests_template(func, language, framework)

    def _generate_tests_template(
        self,
        func: FunctionInfo,
        language: str,
        framework: TestFramework
    ) -> List[GeneratedTest]:
        """Generate tests using templates."""
        tests = []

        if framework == TestFramework.PYTEST and language == 'python':
            # Happy path test
            test_name = f"test_{func.name}_happy_path"
            test_code = self._generate_pytest_template(func, "happy_path")

            tests.append(GeneratedTest(
                test_name=test_name,
                test_code=test_code,
                description=f"Test normal operation of {func.name}",
                test_type="happy_path",
                confidence=0.7
            ))

            # Edge case test
            test_name = f"test_{func.name}_edge_cases"
            test_code = self._generate_pytest_template(func, "edge_case")

            tests.append(GeneratedTest(
                test_name=test_name,
                test_code=test_code,
                description=f"Test edge cases for {func.name}",
                test_type="edge_case",
                confidence=0.6
            ))

            # Error handling test (if function might raise exceptions)
            if any(keyword in str(func.docstring).lower() if func.docstring else '' for keyword in ['raise', 'error', 'exception']):
                test_name = f"test_{func.name}_error_handling"
                test_code = self._generate_pytest_template(func, "error")

                tests.append(GeneratedTest(
                    test_name=test_name,
                    test_code=test_code,
                    description=f"Test error handling for {func.name}",
                    test_type="error_handling",
                    confidence=0.5
                ))

        return tests

    def _generate_pytest_template(self, func: FunctionInfo, test_type: str) -> str:
        """Generate pytest template code."""
        async_prefix = "async " if func.is_async else ""
        await_prefix = "await " if func.is_async else ""
        test_decorator = "@pytest.mark.asyncio\n" if func.is_async else ""

        if test_type == "happy_path":
            # Generate sample parameter values
            param_values = self._generate_sample_values(func.parameters)

            return f'''{test_decorator}{async_prefix}def test_{func.name}_happy_path():
    """Test {func.name} with normal inputs."""
    # Arrange
    {param_values}

    # Act
    result = {await_prefix}{func.name}({', '.join(func.parameters)})

    # Assert
    assert result is not None
    # TODO: Add specific assertions
'''

        elif test_type == "edge_case":
            return f'''{test_decorator}{async_prefix}def test_{func.name}_edge_cases():
    """Test {func.name} with edge case inputs."""
    # TODO: Test with edge cases like:
    # - Empty inputs
    # - Boundary values
    # - Special characters
    pass
'''

        elif test_type == "error":
            return f'''{test_decorator}{async_prefix}def test_{func.name}_error_handling():
    """Test {func.name} error handling."""
    with pytest.raises(Exception):  # TODO: Specify exception type
        {await_prefix}{func.name}({self._generate_error_values(func.parameters)})
'''

        return ""

    def _generate_sample_values(self, params: List[str]) -> str:
        """Generate sample parameter assignments."""
        assignments = []
        for param in params:
            # Simple heuristics based on parameter names
            if 'id' in param.lower():
                assignments.append(f"{param} = 1")
            elif 'name' in param.lower():
                assignments.append(f'{param} = "test_name"')
            elif 'count' in param.lower() or 'num' in param.lower():
                assignments.append(f"{param} = 10")
            elif 'flag' in param.lower() or 'is_' in param.lower():
                assignments.append(f"{param} = True")
            else:
                assignments.append(f'{param} = "test_value"')

        return '\n    '.join(assignments)

    def _generate_error_values(self, params: List[str]) -> str:
        """Generate parameter values that should cause errors."""
        # Simple: use None or invalid values
        return ', '.join(['None'] * len(params))

    def _assemble_test_file(
        self,
        tests: List[GeneratedTest],
        source_filename: str,
        framework: TestFramework,
        language: str
    ) -> str:
        """Assemble complete test file."""
        if framework == TestFramework.PYTEST and language == 'python':
            lines = [
                '"""',
                f'Automated tests for {source_filename}',
                '',
                'Generated by ResoftAI Test Generator',
                f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                '"""',
                '',
                'import pytest',
                'from unittest.mock import Mock, patch',
                '',
                f'# Import from {source_filename}',
                '# TODO: Add actual imports',
                '',
                '',
            ]

            # Add all test functions
            for test in tests:
                lines.append(test.test_code)
                lines.append('')
                lines.append('')

            return '\n'.join(lines)

        return "# TODO: Implement test file generation for this framework"

    def _get_test_filename(self, source_filename: str, language: str) -> str:
        """Generate test filename from source filename."""
        base_name = source_filename.rsplit('.', 1)[0]

        if language == 'python':
            return f"test_{base_name}.py"
        elif language in ['javascript', 'typescript']:
            return f"{base_name}.test.{source_filename.rsplit('.', 1)[1]}"
        else:
            return f"{base_name}_test.{source_filename.rsplit('.', 1)[1] if '.' in source_filename else 'txt'}"

    def _estimate_coverage(self, tests_count: int, functions_count: int) -> float:
        """Estimate test coverage based on generated tests."""
        if functions_count == 0:
            return 0.0

        # Simple heuristic: assume each test covers parts of a function
        # 3 tests per function (happy, edge, error) = ~75% coverage
        coverage = min(100.0, (tests_count / (functions_count * 3)) * 75)

        return coverage


# Singleton instance
_test_generator = None


def get_test_generator(llm_provider: Optional[LLMProvider] = None) -> TestGenerator:
    """Get singleton instance of test generator."""
    global _test_generator
    if _test_generator is None or (llm_provider and _test_generator.llm_provider != llm_provider):
        _test_generator = TestGenerator(llm_provider)
    return _test_generator
