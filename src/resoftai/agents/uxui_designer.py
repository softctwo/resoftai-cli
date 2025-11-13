"""
UX/UI Designer Agent - Designs user experience and interface.
"""

from typing import List
import logging

from resoftai.core.agent import Agent, AgentRole, AgentCapability
from resoftai.core.message_bus import Message, MessageType
from resoftai.core.state import WorkflowStage, TaskStatus

logger = logging.getLogger(__name__)


class UXUIDesignerAgent(Agent):
    """
    UX/UI Designer Agent responsible for:
    - User experience design
    - User interface design
    - Interaction design
    - Design system creation
    - Usability considerations
    """

    @property
    def name(self) -> str:
        return "UX/UI Designer"

    @property
    def system_prompt(self) -> str:
        return """You are an expert UX/UI Designer with deep knowledge of user-centered design principles.

Your responsibilities include:
- Designing intuitive user experiences
- Creating beautiful, functional user interfaces
- Designing interaction patterns
- Creating design systems and style guides
- Ensuring accessibility and usability

Your design principles:
- User-centered: always prioritize user needs
- Simplicity: remove unnecessary complexity
- Consistency: maintain design consistency
- Accessibility: design for all users
- Visual hierarchy: guide users naturally

When designing:
1. Consider user personas and user journeys
2. Apply UX best practices and patterns
3. Ensure responsive design for all devices
4. Follow accessibility guidelines (WCAG)
5. Create clear, actionable designs
6. Balance aesthetics with functionality"""

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="ux_design",
                description="Design user experience flows",
                input_schema={"requirements": "object"},
                output_schema={"ux_design": "object"},
            ),
            AgentCapability(
                name="ui_design",
                description="Design user interface",
                input_schema={"ux_flow": "object"},
                output_schema={"ui_design": "object"},
            ),
        ]

    @property
    def responsible_stages(self) -> List[WorkflowStage]:
        return [
            WorkflowStage.UI_UX_DESIGN,
            WorkflowStage.PROTOTYPE_DEVELOPMENT,
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

        if "interface" in task["title"].lower():
            await self._design_user_interface()
        elif "experience" in task["title"].lower():
            await self._design_user_experience()

        self.project_state.update_task(task_id, status=TaskStatus.COMPLETED)

        await self.send_message(
            MessageType.TASK_COMPLETE,
            "workflow",
            {"task_id": task_id, "status": "completed"}
        )

    async def _design_user_interface(self) -> None:
        """Design the user interface."""
        context = self.get_context_from_state()

        prompt = f"""Design a comprehensive user interface based on:

{context}

Create a UI design document including:

1. Design System
   - Color palette
   - Typography (fonts, sizes, hierarchy)
   - Spacing and layout grid
   - Component library

2. Screen Designs
   - Main screens/pages with detailed descriptions
   - Layout structure for each screen
   - Component placement
   - Navigation structure

3. UI Components
   - Buttons and controls
   - Forms and inputs
   - Cards and containers
   - Navigation elements
   - Modals and overlays

4. Responsive Design
   - Mobile layout considerations
   - Tablet layout
   - Desktop layout
   - Breakpoints

5. Accessibility
   - Color contrast requirements
   - Keyboard navigation
   - Screen reader considerations
   - ARIA labels

6. Visual Design Guidelines
   - Icon style
   - Image treatment
   - Animation principles

Provide detailed, implementable UI specifications."""

        ui_design = await self.call_claude(prompt)

        self.project_state.design["ui_design"] = ui_design
        self.project_state.add_artifact("ui_design", "design/ui-design.md")

        logger.info(f"{self.name} designed user interface")

    async def _design_user_experience(self) -> None:
        """Design the user experience flow."""
        context = self.get_context_from_state()

        prompt = f"""Design the user experience based on:

{context}

Create a UX design document including:

1. User Research
   - User personas
   - User needs and pain points
   - Usage scenarios

2. User Journeys
   - Main user flows
   - Step-by-step journey maps
   - Touchpoints and interactions

3. Information Architecture
   - Site/app structure
   - Navigation hierarchy
   - Content organization

4. Wireframes
   - Low-fidelity wireframes (described in text)
   - Key screens and flows
   - Interaction patterns

5. Interaction Design
   - User actions and system responses
   - Feedback mechanisms
   - Error handling
   - Microinteractions

6. Usability Considerations
   - Ease of use
   - Learnability
   - Efficiency
   - Error prevention

Provide a comprehensive UX design."""

        ux_design = await self.call_claude(prompt)

        self.project_state.design["ux_design"] = ux_design
        self.project_state.add_artifact("ux_design", "design/ux-design.md")

        logger.info(f"{self.name} designed user experience")
