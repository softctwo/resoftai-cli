"""
Quality Expert Agent - Ensures overall software quality.
"""

from typing import List
import logging

from resoftai.core.agent import Agent, AgentRole, AgentCapability
from resoftai.core.message_bus import Message, MessageType
from resoftai.core.state import WorkflowStage, TaskStatus

logger = logging.getLogger(__name__)


class QualityExpertAgent(Agent):
    """
    Quality Expert Agent responsible for:
    - Quality assurance strategy
    - Quality metrics and standards
    - Code quality review
    - Process improvement
    - Final quality validation
    """

    @property
    def name(self) -> str:
        return "Quality Expert"

    @property
    def system_prompt(self) -> str:
        return """You are an expert Quality Assurance professional with deep knowledge of software quality principles.

Your responsibilities include:
- Defining quality standards and metrics
- Ensuring compliance with quality requirements
- Reviewing all deliverables for quality
- Identifying quality risks and issues
- Recommending quality improvements
- Final quality sign-off

Your quality philosophy:
- Prevention over detection
- Continuous improvement
- Evidence-based decisions
- Holistic quality view (code, documentation, process)
- User-centric quality

When assessing quality:
1. Review against established standards
2. Check for completeness and consistency
3. Verify requirements traceability
4. Assess maintainability and sustainability
5. Evaluate user experience quality
6. Consider operational quality (performance, security, etc.)"""

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="quality_review",
                description="Perform comprehensive quality review",
                input_schema={"deliverables": "object"},
                output_schema={"quality_report": "object"},
            ),
            AgentCapability(
                name="quality_metrics",
                description="Define and track quality metrics",
                input_schema={},
                output_schema={"metrics": "object"},
            ),
        ]

    @property
    def responsible_stages(self) -> List[WorkflowStage]:
        return [
            WorkflowStage.QUALITY_ASSURANCE,
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

        await self._perform_quality_review()

        self.project_state.update_task(task_id, status=TaskStatus.COMPLETED)

        await self.send_message(
            MessageType.TASK_COMPLETE,
            "workflow",
            {"task_id": task_id, "status": "completed"}
        )

    async def _perform_quality_review(self) -> None:
        """Perform comprehensive quality review."""
        context = self.get_context_from_state()

        prompt = f"""Perform a comprehensive quality assessment based on:

{context}

Create a quality assessment report including:

1. Quality Standards
   - Coding standards compliance
   - Documentation standards
   - Testing standards
   - Security standards

2. Quality Metrics
   - Code quality metrics
   - Test coverage
   - Defect density
   - Performance metrics
   - Security metrics

3. Requirements Traceability
   - Verify all requirements are addressed
   - Check for requirement coverage
   - Identify any gaps

4. Code Quality Review
   - Code structure and organization
   - Design patterns usage
   - Error handling
   - Security best practices
   - Performance considerations
   - Maintainability assessment

5. Documentation Quality
   - Completeness
   - Accuracy
   - Clarity
   - Consistency

6. Test Quality
   - Test coverage adequacy
   - Test case quality
   - Test results analysis

7. User Experience Quality
   - Usability assessment
   - Accessibility compliance
   - User interface consistency

8. Operational Quality
   - Deployment readiness
   - Monitoring and logging
   - Error handling and recovery
   - Performance characteristics

9. Quality Issues and Risks
   - Identified quality issues
   - Risk assessment
   - Recommendations

10. Quality Sign-off
    - Overall quality rating
    - Readiness for deployment
    - Conditions for sign-off

Provide a thorough, professional quality assessment."""

        quality_report = await self.call_claude(prompt)

        self.project_state.metadata["quality_report"] = quality_report
        self.project_state.add_artifact("quality_report", "quality/quality-assessment.md")

        # Record quality decision
        self.project_state.add_decision(
            decision="Quality assessment completed",
            made_by=self.role.value,
            rationale="Comprehensive quality review performed across all dimensions"
        )

        logger.info(f"{self.name} completed quality review")
