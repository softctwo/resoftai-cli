"""
Multi-language support and best practices for code generation.

This module provides language-specific guidance, templates, and best practices
for the AI agents to generate high-quality code across multiple programming languages.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from resoftai.core.code_quality import LanguageType


@dataclass
class LanguageConfig:
    """Configuration and metadata for a programming language."""
    name: str
    type: LanguageType
    file_extensions: List[str]
    description: str
    paradigms: List[str]  # e.g., ["object-oriented", "functional"]
    typical_use_cases: List[str]
    popular_frameworks: List[str]
    package_manager: Optional[str] = None
    build_tool: Optional[str] = None
    testing_framework: Optional[str] = None
    linter: Optional[str] = None
    formatter: Optional[str] = None


@dataclass
class BestPractices:
    """Best practices guide for a programming language."""
    language: LanguageType
    coding_standards: List[str]
    naming_conventions: Dict[str, str]
    code_organization: List[str]
    error_handling: List[str]
    testing_guidelines: List[str]
    security_practices: List[str]
    performance_tips: List[str]
    common_pitfalls: List[str]


class LanguageSupport:
    """
    Centralized language support providing best practices and guidance
    for code generation across multiple programming languages.
    """

    def __init__(self):
        """Initialize language support with configurations."""
        self._configs = self._initialize_configs()
        self._best_practices = self._initialize_best_practices()

    def _initialize_configs(self) -> Dict[LanguageType, LanguageConfig]:
        """Initialize language configurations."""
        return {
            LanguageType.PYTHON: LanguageConfig(
                name="Python",
                type=LanguageType.PYTHON,
                file_extensions=[".py", ".pyw", ".pyx"],
                description="High-level, interpreted, general-purpose programming language",
                paradigms=["object-oriented", "functional", "procedural"],
                typical_use_cases=[
                    "Web development (Django, Flask, FastAPI)",
                    "Data science and machine learning",
                    "Automation and scripting",
                    "API development",
                    "Scientific computing"
                ],
                popular_frameworks=[
                    "Django", "Flask", "FastAPI", "Pytest", "NumPy", "Pandas",
                    "TensorFlow", "PyTorch", "Scikit-learn"
                ],
                package_manager="pip/poetry",
                build_tool="setuptools/poetry",
                testing_framework="pytest/unittest",
                linter="pylint/flake8/ruff",
                formatter="black/autopep8"
            ),

            LanguageType.JAVASCRIPT: LanguageConfig(
                name="JavaScript",
                type=LanguageType.JAVASCRIPT,
                file_extensions=[".js", ".jsx", ".mjs"],
                description="Dynamic, prototype-based scripting language for web",
                paradigms=["object-oriented", "functional", "event-driven"],
                typical_use_cases=[
                    "Frontend web development",
                    "Backend development (Node.js)",
                    "Mobile apps (React Native)",
                    "Desktop apps (Electron)",
                    "Web APIs"
                ],
                popular_frameworks=[
                    "React", "Vue", "Angular", "Express", "Next.js",
                    "Nest.js", "Jest", "Mocha"
                ],
                package_manager="npm/yarn/pnpm",
                build_tool="webpack/vite/esbuild",
                testing_framework="jest/mocha/vitest",
                linter="eslint",
                formatter="prettier"
            ),

            LanguageType.TYPESCRIPT: LanguageConfig(
                name="TypeScript",
                type=LanguageType.TYPESCRIPT,
                file_extensions=[".ts", ".tsx"],
                description="Typed superset of JavaScript",
                paradigms=["object-oriented", "functional"],
                typical_use_cases=[
                    "Large-scale web applications",
                    "Enterprise applications",
                    "Type-safe APIs",
                    "React/Angular/Vue projects"
                ],
                popular_frameworks=[
                    "React", "Angular", "Vue", "Express", "Nest.js",
                    "Next.js", "Remix"
                ],
                package_manager="npm/yarn/pnpm",
                build_tool="tsc/webpack/vite",
                testing_framework="jest/vitest",
                linter="eslint",
                formatter="prettier"
            ),

            LanguageType.JAVA: LanguageConfig(
                name="Java",
                type=LanguageType.JAVA,
                file_extensions=[".java"],
                description="Object-oriented, class-based, platform-independent language",
                paradigms=["object-oriented"],
                typical_use_cases=[
                    "Enterprise applications",
                    "Android mobile apps",
                    "Microservices",
                    "Big data processing",
                    "Server-side applications"
                ],
                popular_frameworks=[
                    "Spring Boot", "Spring Framework", "Hibernate",
                    "JUnit", "Maven", "Gradle"
                ],
                package_manager="maven/gradle",
                build_tool="maven/gradle",
                testing_framework="junit/testng",
                linter="checkstyle/pmd",
                formatter="google-java-format"
            ),

            LanguageType.GO: LanguageConfig(
                name="Go",
                type=LanguageType.GO,
                file_extensions=[".go"],
                description="Statically typed, compiled language designed for simplicity",
                paradigms=["procedural", "concurrent"],
                typical_use_cases=[
                    "Microservices",
                    "Cloud infrastructure",
                    "CLI tools",
                    "Network programming",
                    "DevOps tools"
                ],
                popular_frameworks=[
                    "Gin", "Echo", "Fiber", "Gorilla", "GORM", "Testify"
                ],
                package_manager="go modules",
                build_tool="go build",
                testing_framework="testing package",
                linter="golangci-lint",
                formatter="gofmt"
            ),

            LanguageType.RUST: LanguageConfig(
                name="Rust",
                type=LanguageType.RUST,
                file_extensions=[".rs"],
                description="Systems programming language focused on safety and performance",
                paradigms=["functional", "imperative", "concurrent"],
                typical_use_cases=[
                    "Systems programming",
                    "WebAssembly",
                    "Embedded systems",
                    "Performance-critical applications",
                    "CLI tools"
                ],
                popular_frameworks=[
                    "Tokio", "Actix", "Rocket", "Serde", "Diesel"
                ],
                package_manager="cargo",
                build_tool="cargo",
                testing_framework="cargo test",
                linter="clippy",
                formatter="rustfmt"
            ),
        }

    def _initialize_best_practices(self) -> Dict[LanguageType, BestPractices]:
        """Initialize best practices for each language."""
        return {
            LanguageType.PYTHON: BestPractices(
                language=LanguageType.PYTHON,
                coding_standards=[
                    "Follow PEP 8 style guide",
                    "Use type hints (PEP 484)",
                    "Write docstrings for all public modules, functions, classes (PEP 257)",
                    "Keep functions small and focused (single responsibility)",
                    "Use list/dict comprehensions for clarity",
                    "Prefer f-strings for string formatting"
                ],
                naming_conventions={
                    "modules": "lowercase_with_underscores",
                    "classes": "CapWords (PascalCase)",
                    "functions": "lowercase_with_underscores",
                    "variables": "lowercase_with_underscores",
                    "constants": "UPPERCASE_WITH_UNDERSCORES",
                    "private": "_leading_underscore"
                },
                code_organization=[
                    "One class per file (generally)",
                    "Group imports: stdlib, third-party, local",
                    "Use __init__.py for package structure",
                    "Separate business logic from presentation",
                    "Use virtual environments (venv/poetry)"
                ],
                error_handling=[
                    "Use specific exception types",
                    "Avoid bare except clauses",
                    "Use context managers (with statement)",
                    "Log exceptions with traceback",
                    "Raise exceptions for exceptional cases",
                    "Use finally for cleanup"
                ],
                testing_guidelines=[
                    "Use pytest for testing",
                    "Follow AAA pattern (Arrange-Act-Assert)",
                    "Test edge cases and error conditions",
                    "Use fixtures for test setup",
                    "Aim for >80% code coverage",
                    "Mock external dependencies"
                ],
                security_practices=[
                    "Never hardcode credentials",
                    "Use parameterized SQL queries",
                    "Validate all user input",
                    "Use environment variables for secrets",
                    "Keep dependencies updated",
                    "Use secrets module for sensitive data"
                ],
                performance_tips=[
                    "Use generators for large datasets",
                    "Leverage built-in functions (they're optimized)",
                    "Use set for membership testing",
                    "Profile before optimizing",
                    "Use appropriate data structures",
                    "Consider asyncio for I/O-bound operations"
                ],
                common_pitfalls=[
                    "Mutable default arguments",
                    "Late binding closures in loops",
                    "Modifying list while iterating",
                    "Catching too broad exceptions",
                    "Not using virtual environments",
                    "Ignoring __all__ in __init__.py"
                ]
            ),

            LanguageType.JAVASCRIPT: BestPractices(
                language=LanguageType.JAVASCRIPT,
                coding_standards=[
                    "Use ES6+ features (arrow functions, destructuring, etc.)",
                    "Prefer const over let, avoid var",
                    "Use async/await over callbacks",
                    "Follow Airbnb or Standard style guide",
                    "Use JSDoc for documentation",
                    "Enable strict mode"
                ],
                naming_conventions={
                    "variables": "camelCase",
                    "constants": "UPPER_SNAKE_CASE",
                    "functions": "camelCase",
                    "classes": "PascalCase",
                    "private": "#privateField (or _conventional)",
                    "files": "kebab-case or PascalCase"
                },
                code_organization=[
                    "One component per file",
                    "Use modules (import/export)",
                    "Separate concerns (MVC, components)",
                    "Use index.js for barrel exports",
                    "Group related files in directories"
                ],
                error_handling=[
                    "Use try-catch for async/await",
                    "Handle promise rejections",
                    "Use .catch() for promise chains",
                    "Provide meaningful error messages",
                    "Use error boundaries (React)",
                    "Log errors appropriately"
                ],
                testing_guidelines=[
                    "Use Jest or Vitest for testing",
                    "Write unit and integration tests",
                    "Test components in isolation",
                    "Mock external dependencies",
                    "Use testing-library for React/Vue",
                    "Aim for >80% coverage"
                ],
                security_practices=[
                    "Sanitize user input",
                    "Prevent XSS attacks",
                    "Use Content Security Policy",
                    "Validate on both client and server",
                    "Keep dependencies updated (npm audit)",
                    "Use HTTPS for production"
                ],
                performance_tips=[
                    "Minimize DOM manipulations",
                    "Use debouncing/throttling for events",
                    "Lazy load components and images",
                    "Optimize bundle size (code splitting)",
                    "Use Web Workers for heavy computations",
                    "Cache API responses appropriately"
                ],
                common_pitfalls=[
                    "Using == instead of ===",
                    "Not handling async errors",
                    "Callback hell",
                    "Memory leaks (event listeners)",
                    "Blocking the main thread",
                    "Not cleaning up side effects"
                ]
            ),

            LanguageType.TYPESCRIPT: BestPractices(
                language=LanguageType.TYPESCRIPT,
                coding_standards=[
                    "Enable strict mode in tsconfig.json",
                    "Avoid using 'any' type",
                    "Use interfaces for object shapes",
                    "Define return types explicitly",
                    "Use generics for reusable components",
                    "Leverage union and intersection types"
                ],
                naming_conventions={
                    "interfaces": "PascalCase (IPrefix or not)",
                    "types": "PascalCase",
                    "enums": "PascalCase",
                    "variables": "camelCase",
                    "constants": "UPPER_SNAKE_CASE",
                    "generic_params": "T, U, V or descriptive"
                },
                code_organization=[
                    "Use barrel exports (index.ts)",
                    "Separate types into .d.ts or types/",
                    "Group by feature, not by type",
                    "Use path aliases (@/components)",
                    "Keep related types together"
                ],
                error_handling=[
                    "Use custom error types",
                    "Type error responses",
                    "Use discriminated unions for results",
                    "Handle null/undefined explicitly",
                    "Use optional chaining (?.) and nullish coalescing (??)"
                ],
                testing_guidelines=[
                    "Type your test fixtures",
                    "Use type assertions in tests",
                    "Test type inference",
                    "Mock with proper types",
                    "Use jest with ts-jest or vitest"
                ],
                security_practices=[
                    "Type-safe API responses",
                    "Validate runtime data",
                    "Use zod or yup for schema validation",
                    "Type environment variables",
                    "Prevent type coercion vulnerabilities"
                ],
                performance_tips=[
                    "Use const assertions",
                    "Avoid excessive type computations",
                    "Use 'unknown' instead of 'any' for better type safety",
                    "Leverage tree-shaking with ES modules",
                    "Optimize build configuration"
                ],
                common_pitfalls=[
                    "Overusing 'any' type",
                    "Not enabling strictNullChecks",
                    "Forgetting to handle undefined",
                    "Circular type references",
                    "Not using utility types",
                    "Ignoring compiler errors"
                ]
            ),
        }

    def get_language_config(self, language: LanguageType) -> Optional[LanguageConfig]:
        """Get configuration for a specific language."""
        return self._configs.get(language)

    def get_best_practices(self, language: LanguageType) -> Optional[BestPractices]:
        """Get best practices for a specific language."""
        return self._best_practices.get(language)

    def get_supported_languages(self) -> List[LanguageType]:
        """Get list of all supported languages."""
        return list(self._configs.keys())

    def get_language_prompt_enhancement(self, language: LanguageType) -> str:
        """
        Get language-specific prompt enhancement for AI agents.

        This provides detailed guidance to AI agents when generating code
        in a specific language.

        Args:
            language: Target programming language

        Returns:
            Formatted prompt enhancement string
        """
        config = self.get_language_config(language)
        practices = self.get_best_practices(language)

        if not config or not practices:
            return ""

        lines = [
            f"\n## {config.name} Development Guidelines\n",
            f"**Language**: {config.description}",
            f"**Paradigms**: {', '.join(config.paradigms)}",
            "",
            "### Coding Standards:",
        ]

        for standard in practices.coding_standards:
            lines.append(f"- {standard}")

        lines.extend([
            "",
            "### Naming Conventions:",
        ])

        for item_type, convention in practices.naming_conventions.items():
            lines.append(f"- {item_type.replace('_', ' ').title()}: `{convention}`")

        lines.extend([
            "",
            "### Error Handling:",
        ])

        for guideline in practices.error_handling:
            lines.append(f"- {guideline}")

        lines.extend([
            "",
            "### Security Best Practices:",
        ])

        for practice in practices.security_practices:
            lines.append(f"- {practice}")

        lines.extend([
            "",
            "### Performance Considerations:",
        ])

        for tip in practices.performance_tips[:3]:  # Top 3 tips
            lines.append(f"- {tip}")

        lines.extend([
            "",
            "### Common Pitfalls to Avoid:",
        ])

        for pitfall in practices.common_pitfalls[:3]:  # Top 3 pitfalls
            lines.append(f"- {pitfall}")

        if config.popular_frameworks:
            lines.extend([
                "",
                f"### Recommended Frameworks/Libraries:",
                f"- {', '.join(config.popular_frameworks[:5])}"
            ])

        if config.testing_framework:
            lines.extend([
                "",
                f"### Testing:",
                f"- Use {config.testing_framework}",
            ])
            for guideline in practices.testing_guidelines[:3]:
                lines.append(f"- {guideline}")

        return "\n".join(lines)

    def get_project_template(self, language: LanguageType, project_type: str = "web_api") -> Dict[str, str]:
        """
        Get project structure template for a language.

        Args:
            language: Target programming language
            project_type: Type of project (web_api, cli, library, etc.)

        Returns:
            Dictionary mapping file paths to file templates
        """
        templates = {
            LanguageType.PYTHON: {
                "web_api": {
                    "src/main.py": "# FastAPI application entry point\nfrom fastapi import FastAPI\n\napp = FastAPI()\n",
                    "src/models.py": "# Data models\nfrom pydantic import BaseModel\n",
                    "src/routes.py": "# API routes\nfrom fastapi import APIRouter\n\nrouter = APIRouter()\n",
                    "tests/test_main.py": "# Tests\nimport pytest\n",
                    "requirements.txt": "fastapi\nuvicorn\npydantic\n",
                    "README.md": "# Project Name\n\n## Description\n",
                    ".gitignore": "__pycache__/\n*.pyc\n.env\nvenv/\n",
                }
            },
            LanguageType.JAVASCRIPT: {
                "web_api": {
                    "src/index.js": "// Express application entry point\nconst express = require('express');\n",
                    "src/routes/index.js": "// API routes\nconst express = require('express');\n",
                    "src/controllers/index.js": "// Controllers\n",
                    "tests/index.test.js": "// Tests\nconst request = require('supertest');\n",
                    "package.json": '{\n  "name": "project",\n  "version": "1.0.0"\n}\n',
                    "README.md": "# Project Name\n\n## Description\n",
                    ".gitignore": "node_modules/\n.env\ndist/\n",
                }
            },
        }

        return templates.get(language, {}).get(project_type, {})


# Singleton instance
_language_support_instance = None


def get_language_support() -> LanguageSupport:
    """Get singleton instance of language support."""
    global _language_support_instance
    if _language_support_instance is None:
        _language_support_instance = LanguageSupport()
    return _language_support_instance
