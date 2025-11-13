"""
Developer Agent - Implements the software solution.
"""

from typing import List
import logging

from resoftai.core.agent import Agent, AgentRole, AgentCapability
from resoftai.core.message_bus import Message, MessageType
from resoftai.core.state import WorkflowStage, TaskStatus

logger = logging.getLogger(__name__)


class DeveloperAgent(Agent):
    """
    Developer Agent responsible for:
    - Software implementation
    - Code development
    - Technical problem-solving
    - Code quality and best practices
    """

    @property
    def name(self) -> str:
        return "Software Developer"

    @property
    def system_prompt(self) -> str:
        return """You are an expert Software Developer with comprehensive programming knowledge and best practices expertise.

Your responsibilities include:
- Implementing software features based on specifications
- Writing clean, maintainable, and efficient code
- Following coding standards and best practices
- Implementing proper error handling and logging
- Writing unit tests
- Documenting code

Your coding principles:
- Code quality: write clean, readable code
- Best practices: follow industry standards
- Testing: ensure code is well-tested
- Performance: optimize when necessary
- Security: implement secure coding practices
- Documentation: document complex logic

When implementing:
1. Follow the architecture and design specifications
2. Use appropriate design patterns
3. Implement comprehensive error handling
4. Write meaningful comments for complex logic
5. Ensure code is modular and reusable
6. Consider performance and scalability"""

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="feature_implementation",
                description="Implement software features",
                input_schema={"specification": "object"},
                output_schema={"implementation": "object"},
            ),
            AgentCapability(
                name="code_review",
                description="Review code quality",
                input_schema={"code": "string"},
                output_schema={"review": "object"},
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
        """Implement software features."""
        context = self.get_context_from_state()

        prompt = f"""Create a comprehensive implementation guide based on:

{context}

Provide:

1. Implementation Plan
   - Development phases
   - Feature breakdown
   - Dependencies

2. Code Structure
   - Project organization
   - Module design
   - File structure

3. Implementation Details for Key Features
   - Core algorithms
   - Data models
   - API implementations
   - UI implementations

4. Code Examples
   - Sample code for complex features
   - Best practice examples
   - Common patterns to use

5. Testing Strategy
   - Unit testing approach
   - Integration testing
   - Test coverage goals

6. Development Guidelines
   - Coding standards
   - Git workflow
   - Code review process

Provide a complete implementation guide."""

        implementation_guide = await self.call_claude(prompt)

        self.project_state.implementation_plan["implementation_guide"] = implementation_guide
        self.project_state.add_artifact("implementation_guide", "development/implementation-guide.md")

        logger.info(f"{self.name} created implementation guide")
