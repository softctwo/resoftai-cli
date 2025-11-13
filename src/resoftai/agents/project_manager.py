"""
Project Manager Agent - Coordinates the entire software development project.
"""

from typing import List
import logging

from resoftai.core.agent import Agent, AgentRole, AgentCapability
from resoftai.core.message_bus import Message, MessageType
from resoftai.core.state import WorkflowStage, TaskStatus

logger = logging.getLogger(__name__)


class ProjectManagerAgent(Agent):
    """
    Project Manager Agent responsible for:
    - Overall project coordination
    - Client communication
    - Progress tracking
    - Resource allocation
    - Risk management
    """

    @property
    def name(self) -> str:
        return "Project Manager"

    @property
    def system_prompt(self) -> str:
        return """You are an expert Project Manager specializing in software development projects.

Your responsibilities include:
- Coordinating all aspects of software development projects
- Managing client relationships and expectations
- Tracking project progress and ensuring timely delivery
- Facilitating communication between team members
- Identifying and mitigating project risks
- Making strategic decisions about project direction

Your communication style is:
- Professional and clear
- Client-focused and empathetic
- Strategic and organized
- Proactive in identifying issues

When responding:
1. Always consider the big picture and project goals
2. Communicate clearly with both technical and non-technical stakeholders
3. Identify potential risks and propose mitigation strategies
4. Ensure all deliverables meet quality standards
5. Keep the project on track and within scope"""

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="project_planning",
                description="Create and manage project plans",
                input_schema={"requirements": "string"},
                output_schema={"plan": "object"},
            ),
            AgentCapability(
                name="client_communication",
                description="Handle client communications and feedback",
                input_schema={"message": "string"},
                output_schema={"response": "string"},
            ),
            AgentCapability(
                name="progress_tracking",
                description="Track and report project progress",
                input_schema={},
                output_schema={"progress_report": "object"},
            ),
        ]

    @property
    def responsible_stages(self) -> List[WorkflowStage]:
        return [
            WorkflowStage.REQUIREMENTS_GATHERING,
            WorkflowStage.CLIENT_REVIEW,
            WorkflowStage.DEVELOPMENT_PLANNING,
            WorkflowStage.DOCUMENTATION,
            WorkflowStage.DEPLOYMENT,
        ]

    async def process_request(self, message: Message) -> None:
        """Process requests from other agents or the system."""
        request_type = message.content.get("request_type")

        if request_type == "create_project_plan":
            await self._create_project_plan(message)
        elif request_type == "client_communication":
            await self._handle_client_communication(message)
        elif request_type == "progress_report":
            await self._generate_progress_report(message)
        else:
            logger.warning(f"Unknown request type: {request_type}")

    async def handle_task_assignment(self, message: Message) -> None:
        """Handle task assignments."""
        task_id = message.content.get("task_id")
        task = message.content.get("task")

        logger.info(f"{self.name} received task: {task['title']}")

        # Update task status
        self.project_state.update_task(task_id, status=TaskStatus.IN_PROGRESS)

        # Process the task based on current stage
        stage = WorkflowStage(task["stage"])

        if stage == WorkflowStage.REQUIREMENTS_GATHERING:
            await self._gather_requirements()
        elif stage == WorkflowStage.CLIENT_REVIEW:
            await self._coordinate_client_review()
        elif stage == WorkflowStage.DEVELOPMENT_PLANNING:
            await self._create_development_plan()
        elif stage == WorkflowStage.DOCUMENTATION:
            await self._coordinate_documentation()
        elif stage == WorkflowStage.DEPLOYMENT:
            await self._coordinate_deployment()

        # Mark task as completed
        self.project_state.update_task(task_id, status=TaskStatus.COMPLETED)

        await self.send_message(
            MessageType.TASK_COMPLETE,
            "workflow",
            {"task_id": task_id, "status": "completed"}
        )

    async def _gather_requirements(self) -> None:
        """Gather and organize initial requirements."""
        context = self.get_context_from_state()
        user_input = self.project_state.requirements.get("initial_input", "")

        prompt = f"""Based on the following user input, help organize and clarify the software requirements:

User Input:
{user_input}

Current Context:
{context}

Please:
1. Identify the key features and functionalities requested
2. Ask any clarifying questions if needed
3. Organize requirements into categories (functional, non-functional, etc.)
4. Identify any potential challenges or considerations

Provide a structured response."""

        response = await self.call_claude(prompt)

        # Store organized requirements
        self.project_state.requirements["organized_requirements"] = response

        logger.info(f"{self.name} completed requirements gathering")

    async def _coordinate_client_review(self) -> None:
        """Coordinate client review process."""
        # Prepare materials for client review
        review_package = {
            "requirements": self.project_state.requirements,
            "architecture": self.project_state.architecture,
            "design": self.project_state.design,
            "prototype_notes": self.project_state.metadata.get("prototype", {}),
        }

        prompt = f"""Prepare a client review presentation based on the following project materials:

{review_package}

Create:
1. Executive summary of the project
2. Key features and capabilities
3. Architecture overview (in simple terms)
4. Design highlights
5. Questions for the client
6. Next steps

Make it client-friendly and professional."""

        review_presentation = await self.call_claude(prompt)

        self.project_state.metadata["client_review_presentation"] = review_presentation

        logger.info(f"{self.name} prepared client review materials")

    async def _create_development_plan(self) -> None:
        """Create detailed development plan."""
        context = self.get_context_from_state()

        prompt = f"""Create a detailed development plan based on:

{context}

Include:
1. Development phases and milestones
2. Task breakdown and estimates
3. Resource allocation
4. Timeline and schedule
5. Risk assessment
6. Quality assurance checkpoints

Provide a comprehensive plan in a structured format."""

        plan = await self.call_claude(prompt)

        self.project_state.implementation_plan["development_plan"] = plan

        logger.info(f"{self.name} created development plan")

    async def _coordinate_documentation(self) -> None:
        """Coordinate the documentation process."""
        # This will trigger document generation
        await self.send_message(
            MessageType.AGENT_REQUEST,
            None,  # Broadcast to all
            {
                "request_type": "generate_all_documents",
                "project_state": self.project_state.to_dict(),
            }
        )

        logger.info(f"{self.name} initiated documentation generation")

    async def _coordinate_deployment(self) -> None:
        """Coordinate deployment process."""
        prompt = """Create a deployment checklist and guide including:

1. Pre-deployment checklist
2. Deployment steps
3. Post-deployment verification
4. Rollback procedures
5. Monitoring and support plan

Provide detailed, actionable steps."""

        deployment_guide = await self.call_claude(prompt)

        self.project_state.metadata["deployment_guide"] = deployment_guide

        logger.info(f"{self.name} prepared deployment materials")

    async def _create_project_plan(self, message: Message) -> None:
        """Create initial project plan."""
        # Implementation for project planning
        pass

    async def _handle_client_communication(self, message: Message) -> None:
        """Handle client communication."""
        # Implementation for client communication
        pass

    async def _generate_progress_report(self, message: Message) -> None:
        """Generate progress report."""
        # Implementation for progress reporting
        pass
