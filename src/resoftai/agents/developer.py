"""
Developer Agent - Implements the software solution with advanced code generation.
"""

from typing import List, Optional
import logging

from resoftai.core.agent import Agent, AgentRole, AgentCapability
from resoftai.core.message_bus import Message, MessageType
from resoftai.core.state import WorkflowStage, TaskStatus
from resoftai.core.code_quality import get_code_quality_checker, LanguageType
from resoftai.core.language_support import get_language_support

logger = logging.getLogger(__name__)


class DeveloperAgent(Agent):
    """
    Enhanced Developer Agent responsible for:
    - Software implementation with multi-language support
    - Code development following best practices
    - Technical problem-solving
    - Code quality and security
    - Performance optimization
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code_checker = get_code_quality_checker()
        self.language_support = get_language_support()

    @property
    def name(self) -> str:
        return "Software Developer"

    @property
    def system_prompt(self) -> str:
        return """You are an expert Software Developer with comprehensive programming knowledge across multiple languages and frameworks.

Your core responsibilities:
- Implement software features based on specifications
- Write clean, maintainable, and efficient code
- Follow industry best practices and coding standards
- Implement comprehensive error handling
- Write thorough unit tests
- Provide clear documentation
- Consider security implications
- Optimize for performance when necessary

Supported Programming Languages:
- Python (Django, Flask, FastAPI, Data Science)
- JavaScript/TypeScript (React, Vue, Node.js, Express)
- Java (Spring Boot, Enterprise Applications)
- Go (Microservices, Cloud Infrastructure)
- Rust (Systems Programming, Performance-Critical)
- C++ (High-Performance Applications)
- C# (.NET, Enterprise Solutions)
- PHP (Laravel, WordPress)
- Ruby (Rails, Scripting)

Core Programming Principles:
1. **Code Quality**
   - Write self-documenting code with clear variable/function names
   - Keep functions small and focused (single responsibility)
   - Follow DRY (Don't Repeat Yourself) principle
   - Use appropriate design patterns
   - Maintain consistent code style

2. **Best Practices**
   - Follow language-specific style guides (PEP 8, Airbnb, etc.)
   - Use type hints/annotations where available
   - Implement proper logging (not print statements)
   - Write meaningful comments for complex logic only
   - Use version control best practices

3. **Testing**
   - Write unit tests for all public functions
   - Follow AAA pattern (Arrange-Act-Assert)
   - Test edge cases and error conditions
   - Mock external dependencies
   - Aim for >80% code coverage

4. **Security**
   - Never hardcode credentials or sensitive data
   - Validate and sanitize all user input
   - Use parameterized queries (prevent SQL injection)
   - Implement proper authentication and authorization
   - Keep dependencies updated
   - Follow OWASP security guidelines

5. **Performance**
   - Choose appropriate data structures
   - Optimize algorithms for time/space complexity
   - Use caching strategically
   - Profile before optimizing
   - Consider scalability from the start

6. **Error Handling**
   - Use specific exception types
   - Provide meaningful error messages
   - Implement graceful degradation
   - Log errors with context
   - Use try-finally for cleanup

7. **Documentation**
   - Write clear docstrings/JSDoc for public APIs
   - Maintain README with setup instructions
   - Document architectural decisions
   - Keep documentation in sync with code

When implementing features:
1. Understand requirements thoroughly
2. Choose the appropriate language and framework
3. Design before coding (think about architecture)
4. Follow the project's existing patterns
5. Write tests alongside code (TDD when appropriate)
6. Review your own code before submission
7. Optimize for readability first, performance second
8. Consider future maintainability

Always:
- Ask clarifying questions if requirements are ambiguous
- Suggest better alternatives if you see them
- Flag potential security vulnerabilities
- Recommend appropriate libraries/frameworks
- Consider the full software lifecycle
- Think about the end user's experience"""

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="feature_implementation",
                description="Implement software features with best practices",
                input_schema={"specification": "object", "language": "string"},
                output_schema={"implementation": "object", "quality_report": "object"},
            ),
            AgentCapability(
                name="code_review",
                description="Review code quality and provide feedback",
                input_schema={"code": "string", "language": "string"},
                output_schema={"review": "object", "suggestions": "array"},
            ),
            AgentCapability(
                name="code_quality_check",
                description="Perform automated code quality analysis",
                input_schema={"code": "string", "filename": "string"},
                output_schema={"quality_score": "number", "issues": "array"},
            ),
        ]

    @property
    def responsible_stages(self) -> List[WorkflowStage]:
        return [
            WorkflowStage.PROTOTYPE_DEVELOPMENT,
            WorkflowStage.IMPLEMENTATION,
            WorkflowStage.TESTING,
        ]

    async def process_request(self, message: Message) -> None:
        """Process requests."""
        pass

    async def handle_task_assignment(self, message: Message) -> None:
        """Handle task assignments."""
        task_id = message.content.get("task_id")
        task = message.content.get("task")

        logger.info(f"{self.name} received task: {task['title']}")

        self.project_state.update_task(task_id, status=TaskStatus.IN_PROGRESS)

        stage = WorkflowStage(task["stage"])

        if stage == WorkflowStage.PROTOTYPE_DEVELOPMENT:
            await self._develop_prototype()
        elif stage == WorkflowStage.IMPLEMENTATION:
            await self._implement_features()

        self.project_state.update_task(task_id, status=TaskStatus.COMPLETED)

        await self.send_message(
            MessageType.TASK_COMPLETE,
            "workflow",
            {"task_id": task_id, "status": "completed"}
        )

    async def _develop_prototype(self) -> None:
        """Develop a working prototype."""
        context = self.get_context_from_state()

        prompt = f"""Create a prototype implementation plan based on:

{context}

Provide:

1. Prototype Scope
   - Core features to include
   - Technologies to use
   - Implementation approach

2. Technical Stack
   - Specific frameworks and libraries
   - Development tools

3. Implementation Guide
   - Project structure
   - Key components to implement
   - Sample code for critical parts

4. Setup Instructions
   - Environment setup
   - Dependencies
   - Configuration

5. Demo Scenario
   - How to demonstrate the prototype
   - Key features to showcase

Provide detailed implementation guidance."""

        prototype_plan = await self.call_claude(prompt)

        self.project_state.metadata["prototype"] = {
            "plan": prototype_plan,
            "status": "planned"
        }
        self.project_state.add_artifact("prototype_plan", "development/prototype-plan.md")

        logger.info(f"{self.name} created prototype plan")

    async def _implement_features(self) -> None:
        """Implement software features with language-specific best practices."""
        context = self.get_context_from_state()

        # Detect target language from project metadata or requirements
        target_language = self._detect_target_language(context)

        # Get language-specific guidance
        language_guidance = self.language_support.get_language_prompt_enhancement(target_language)

        prompt = f"""Create a comprehensive implementation guide based on:

{context}

{language_guidance}

Provide:

1. Implementation Plan
   - Development phases
   - Feature breakdown
   - Dependencies and libraries to use

2. Code Structure
   - Project organization following {target_language.value} best practices
   - Module design
   - File structure and naming conventions

3. Implementation Details for Key Features
   - Core algorithms with code examples
   - Data models (with proper types/annotations)
   - API implementations (RESTful best practices)
   - UI implementations (if applicable)
   - Database schema and migrations

4. Code Examples
   - Sample code for complex features in {target_language.value}
   - Best practice examples following style guides
   - Common design patterns to use
   - Error handling patterns

5. Testing Strategy
   - Unit testing approach with test framework
   - Integration testing plan
   - Test coverage goals (aim for >80%)
   - Sample test cases

6. Development Guidelines
   - Coding standards ({target_language.value} style guide)
   - Git workflow and branch strategy
   - Code review checklist
   - Security considerations

7. Quality Assurance
   - Code linting configuration
   - Code formatting tools
   - Static analysis tools
   - CI/CD pipeline suggestions

Provide a complete, production-ready implementation guide."""

        implementation_guide = await self.generate(prompt)

        self.project_state.implementation_plan["implementation_guide"] = implementation_guide
        self.project_state.implementation_plan["target_language"] = target_language.value
        self.project_state.add_artifact("implementation_guide", "development/implementation-guide.md")

        logger.info(f"{self.name} created implementation guide for {target_language.value}")

    def _detect_target_language(self, context: str) -> LanguageType:
        """
        Detect the target programming language from context.

        Args:
            context: Project context string

        Returns:
            Detected language type
        """
        context_lower = context.lower()

        # Language detection keywords
        language_keywords = {
            LanguageType.PYTHON: ["python", "django", "flask", "fastapi", "pandas", "numpy"],
            LanguageType.JAVASCRIPT: ["javascript", "js", "node", "react", "vue", "express"],
            LanguageType.TYPESCRIPT: ["typescript", "ts", "angular", "nest.js"],
            LanguageType.JAVA: ["java", "spring", "springboot", "maven", "gradle"],
            LanguageType.GO: ["golang", "go lang", " go "],
            LanguageType.RUST: ["rust", "cargo"],
            LanguageType.CPP: ["c++", "cpp"],
            LanguageType.CSHARP: ["c#", "csharp", ".net", "dotnet"],
        }

        # Count keyword matches for each language
        scores = {}
        for lang, keywords in language_keywords.items():
            scores[lang] = sum(1 for kw in keywords if kw in context_lower)

        # Return language with highest score, default to Python
        if scores:
            detected = max(scores, key=scores.get)
            if scores[detected] > 0:
                logger.info(f"Detected language: {detected.value} (score: {scores[detected]})")
                return detected

        # Default to Python if no clear match
        logger.info("No clear language detected, defaulting to Python")
        return LanguageType.PYTHON

    async def check_code_quality(self, code: str, filename: str) -> dict:
        """
        Perform automated code quality check.

        Args:
            code: Source code to check
            filename: Name of the file

        Returns:
            Dictionary with quality report
        """
        # Run automated quality check
        report = self.code_checker.analyze_code(code, filename=filename)

        # Format report for logging
        formatted_report = self.code_checker.format_report(report)
        logger.info(f"Code quality check for {filename}:\n{formatted_report}")

        # Return structured data
        return {
            "filename": filename,
            "language": report.language.value,
            "quality_score": report.score,
            "total_lines": report.total_lines,
            "issues_count": len(report.issues),
            "critical_issues": sum(1 for i in report.issues if i.level.value == "critical"),
            "error_issues": sum(1 for i in report.issues if i.level.value == "error"),
            "warning_issues": sum(1 for i in report.issues if i.level.value == "warning"),
            "metrics": report.metrics,
            "issues": [
                {
                    "level": i.level.value,
                    "message": i.message,
                    "line": i.line_number,
                    "rule_id": i.rule_id,
                    "suggestion": i.suggestion
                }
                for i in report.issues
            ]
        }

    async def generate_code_with_quality_check(
        self,
        prompt: str,
        filename: str,
        max_iterations: int = 3
    ) -> tuple[str, dict]:
        """
        Generate code and iteratively improve it based on quality checks.

        Args:
            prompt: Code generation prompt
            filename: Target filename
            max_iterations: Maximum improvement iterations

        Returns:
            Tuple of (final_code, quality_report)
        """
        logger.info(f"Generating code for {filename} with quality check")

        for iteration in range(max_iterations):
            # Generate code
            code = await self.generate(prompt)

            # Check quality
            quality_report = await self.check_code_quality(code, filename)

            # If quality is good enough, return
            if quality_report["quality_score"] >= 85 and quality_report["critical_issues"] == 0:
                logger.info(f"Code quality acceptable (score: {quality_report['quality_score']})")
                return code, quality_report

            # If not the last iteration, create improvement prompt
            if iteration < max_iterations - 1:
                issues_summary = "\n".join([
                    f"- Line {i['line']}: {i['message']} ({i['suggestion']})"
                    for i in quality_report["issues"][:5]  # Top 5 issues
                ])

                improvement_prompt = f"""The previous code has quality issues. Please improve it.

Original prompt: {prompt}

Quality Issues Found:
{issues_summary}

Please generate improved code that addresses these issues."""

                prompt = improvement_prompt
                logger.info(f"Iteration {iteration + 1}: Improving code (score: {quality_report['quality_score']})")

        logger.warning(f"Max iterations reached. Final quality score: {quality_report['quality_score']}")
        return code, quality_report
