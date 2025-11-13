"""
Requirements Analyst Agent - Analyzes and documents software requirements.
"""

from typing import List
import logging

from resoftai.core.agent import Agent, AgentRole, AgentCapability
from resoftai.core.message_bus import Message, MessageType
from resoftai.core.state import WorkflowStage, TaskStatus

logger = logging.getLogger(__name__)


class RequirementsAnalystAgent(Agent):
    """
    Requirements Analyst Agent responsible for:
    - Gathering detailed requirements
    - Analyzing user needs
    - Creating requirements specifications
    - Requirements validation and refinement
    """

    @property
    def name(self) -> str:
        return "Requirements Analyst"

    @property
    def system_prompt(self) -> str:
        return """You are an expert Requirements Analyst with deep expertise in software requirements engineering.

Your responsibilities include:
- Eliciting detailed requirements from stakeholders
- Analyzing and documenting functional and non-functional requirements
- Creating clear, testable requirements specifications
- Identifying requirements conflicts and dependencies
- Validating requirements completeness and feasibility

Your approach is:
- Systematic and thorough
- Detail-oriented and precise
- Question-driven to uncover hidden requirements
- Focused on clarity and testability

When analyzing requirements:
1. Use structured techniques (use cases, user stories, etc.)
2. Identify both functional and non-functional requirements
3. Consider edge cases and error scenarios
4. Ensure requirements are specific, measurable, and testable
5. Document assumptions and constraints"""

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="requirements_elicitation",
                description="Gather detailed requirements from users",
                input_schema={"user_input": "string"},
                output_schema={"requirements": "object"},
            ),
            AgentCapability(
                name="requirements_analysis",
                description="Analyze and structure requirements",
                input_schema={"raw_requirements": "string"},
                output_schema={"analyzed_requirements": "object"},
            ),
        ]

    @property
    def responsible_stages(self) -> List[WorkflowStage]:
        return [
            WorkflowStage.REQUIREMENTS_GATHERING,
            WorkflowStage.REQUIREMENTS_ANALYSIS,
            WorkflowStage.REQUIREMENTS_REFINEMENT,
        ]

    async def process_request(self, message: Message) -> None:
        """Process requests."""
        request_type = message.content.get("request_type")

        if request_type == "analyze_requirements":
            await self._analyze_requirements(message)

    async def handle_task_assignment(self, message: Message) -> None:
        """Handle task assignments."""
        task_id = message.content.get("task_id")
        task = message.content.get("task")

        logger.info(f"{self.name} received task: {task['title']}")

        self.project_state.update_task(task_id, status=TaskStatus.IN_PROGRESS)

        stage = WorkflowStage(task["stage"])

        if stage == WorkflowStage.REQUIREMENTS_GATHERING:
            await self._document_user_needs()
        elif stage == WorkflowStage.REQUIREMENTS_ANALYSIS:
            await self._create_requirements_specification()
        elif stage == WorkflowStage.REQUIREMENTS_REFINEMENT:
            await self._refine_requirements()

        self.project_state.update_task(task_id, status=TaskStatus.COMPLETED)

        await self.send_message(
            MessageType.TASK_COMPLETE,
            "workflow",
            {"task_id": task_id, "status": "completed"}
        )

    async def _document_user_needs(self) -> None:
        """Document detailed user needs."""
        context = self.get_context_from_state()

        prompt = f"""Analyze the user requirements and create a comprehensive requirements document:

{context}

Create:
1. Functional Requirements (with priorities)
2. Non-Functional Requirements (performance, security, usability, etc.)
3. User Stories
4. Use Cases
5. System Constraints
6. Assumptions and Dependencies

Format each requirement clearly and ensure they are testable."""

        requirements_doc = await self.call_claude(prompt)

        self.project_state.requirements["detailed_requirements"] = requirements_doc

        logger.info(f"{self.name} documented user needs")

    async def _create_requirements_specification(self) -> None:
        """Create formal requirements specification."""
        context = self.get_context_from_state()

        prompt = f"""Create a formal Software Requirements Specification (SRS) document:

{context}

Structure:
1. Introduction
   - Purpose
   - Scope
   - Definitions and Acronyms
2. Overall Description
   - Product Perspective
   - Product Features
   - User Classes
3. Functional Requirements
   - Detailed feature specifications
4. Non-Functional Requirements
   - Performance requirements
   - Security requirements
   - Quality attributes
5. Interface Requirements
6. Data Requirements
7. Acceptance Criteria

Ensure professional formatting and completeness."""

        srs_document = await self.call_claude(prompt)

        self.project_state.requirements["srs_document"] = srs_document
        self.project_state.add_artifact("requirements_specification", "requirements/SRS.md")

        logger.info(f"{self.name} created requirements specification")

    async def _refine_requirements(self) -> None:
        """Refine requirements based on feedback."""
        context = self.get_context_from_state()
        feedback = self.project_state.client_feedback

        prompt = f"""Refine the requirements based on client feedback:

Current Requirements:
{context}

Client Feedback:
{feedback}

Update the requirements to:
1. Address all client feedback
2. Resolve any ambiguities
3. Add missing requirements
4. Update priorities if needed
5. Ensure consistency across all requirements

Provide the refined requirements document."""

        refined_requirements = await self.call_claude(prompt)

        self.project_state.requirements["refined_requirements"] = refined_requirements

        logger.info(f"{self.name} refined requirements")

    async def _analyze_requirements(self, message: Message) -> None:
        """Analyze requirements for completeness and consistency."""
        # Implementation for requirements analysis
        pass
