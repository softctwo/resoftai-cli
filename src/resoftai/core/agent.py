"""
Base Agent class for all AI agents in the platform.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional
import logging
from anthropic import Anthropic

from resoftai.core.message_bus import Message, MessageBus, MessageType
from resoftai.core.state import ProjectState, WorkflowStage
from resoftai.config.settings import get_settings

logger = logging.getLogger(__name__)


class AgentRole(str, Enum):
    """Roles of different agents in the system."""

    PROJECT_MANAGER = "project_manager"
    REQUIREMENTS_ANALYST = "requirements_analyst"
    ARCHITECT = "architect"
    UXUI_DESIGNER = "uxui_designer"
    DEVELOPER = "developer"
    TEST_ENGINEER = "test_engineer"
    QUALITY_EXPERT = "quality_expert"


@dataclass
class AgentCapability:
    """Represents a capability of an agent."""

    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]


class Agent(ABC):
    """
    Base class for all AI agents in the ResoftAI platform.

    Each agent has:
    - A specific role and expertise
    - Ability to process messages and respond
    - Access to the project state
    - Communication through the message bus
    """

    def __init__(
        self,
        role: AgentRole,
        message_bus: MessageBus,
        project_state: ProjectState,
    ):
        """
        Initialize an agent.

        Args:
            role: The role of this agent
            message_bus: Message bus for communication
            project_state: Shared project state
        """
        self.role = role
        self.message_bus = message_bus
        self.project_state = project_state
        self.settings = get_settings()
        self.client = Anthropic(api_key=self.settings.anthropic_api_key)

        # Subscribe to relevant messages
        self._setup_subscriptions()

        logger.info(f"Initialized {self.role.value} agent")

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the agent."""
        pass

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt that defines the agent's behavior and expertise."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[AgentCapability]:
        """List of capabilities this agent provides."""
        pass

    @property
    @abstractmethod
    def responsible_stages(self) -> List[WorkflowStage]:
        """Workflow stages this agent is primarily responsible for."""
        pass

    def _setup_subscriptions(self) -> None:
        """Setup message subscriptions for this agent."""
        # Subscribe to messages directed to this agent
        self.message_bus.subscribe(
            f"receiver:{self.role.value}",
            self._handle_message
        )

        # Subscribe to workflow stage changes
        self.message_bus.subscribe(
            f"type:{MessageType.STAGE_START.value}",
            self._handle_stage_change
        )

    async def _handle_message(self, message: Message) -> None:
        """
        Handle incoming messages.

        Args:
            message: The message to handle
        """
        logger.debug(f"{self.name} received message: {message.type.value}")

        try:
            if message.type == MessageType.AGENT_REQUEST:
                await self.process_request(message)
            elif message.type == MessageType.TASK_ASSIGNED:
                await self.handle_task_assignment(message)
            elif message.type == MessageType.USER_FEEDBACK:
                await self.handle_user_feedback(message)
        except Exception as e:
            logger.error(f"Error handling message in {self.name}: {e}", exc_info=True)
            await self._send_error_response(message, str(e))

    async def _handle_stage_change(self, message: Message) -> None:
        """
        Handle workflow stage changes.

        Args:
            message: Stage change message
        """
        stage = WorkflowStage(message.content.get("stage"))
        if stage in self.responsible_stages:
            logger.info(f"{self.name} activated for stage: {stage.value}")
            await self.on_stage_start(stage)

    @abstractmethod
    async def process_request(self, message: Message) -> None:
        """
        Process a request message and generate a response.

        Args:
            message: The request message
        """
        pass

    @abstractmethod
    async def handle_task_assignment(self, message: Message) -> None:
        """
        Handle a task assignment.

        Args:
            message: Task assignment message
        """
        pass

    async def handle_user_feedback(self, message: Message) -> None:
        """
        Handle user feedback. Default implementation logs it.

        Args:
            message: User feedback message
        """
        feedback = message.content.get("feedback", "")
        self.project_state.add_client_feedback(
            feedback=feedback,
            stage=self.project_state.current_stage
        )
        logger.info(f"{self.name} recorded user feedback")

    async def on_stage_start(self, stage: WorkflowStage) -> None:
        """
        Called when a workflow stage that this agent is responsible for starts.

        Args:
            stage: The workflow stage that is starting
        """
        logger.info(f"{self.name} starting work on stage: {stage.value}")

    async def call_claude(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Call Claude API to get AI response.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt (uses agent's default if not provided)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            The AI response text
        """
        try:
            response = self.client.messages.create(
                model=self.settings.claude_model,
                max_tokens=max_tokens or self.settings.claude_max_tokens,
                temperature=temperature or self.settings.claude_temperature,
                system=system_prompt or self.system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract text from response
            text_content = ""
            for block in response.content:
                if block.type == "text":
                    text_content += block.text

            return text_content

        except Exception as e:
            logger.error(f"Error calling Claude API: {e}", exc_info=True)
            raise

    async def send_message(
        self,
        message_type: MessageType,
        receiver: Optional[str],
        content: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Send a message via the message bus.

        Args:
            message_type: Type of message
            receiver: Receiver agent role (None for broadcast)
            content: Message content
            correlation_id: Optional correlation ID for tracking related messages
        """
        message = Message(
            type=message_type,
            sender=self.role.value,
            receiver=receiver,
            content=content,
            correlation_id=correlation_id,
        )
        await self.message_bus.publish(message)

    async def _send_error_response(self, original_message: Message, error: str) -> None:
        """Send an error response message."""
        await self.send_message(
            message_type=MessageType.AGENT_RESPONSE,
            receiver=original_message.sender,
            content={
                "status": "error",
                "error": error,
                "original_message_id": original_message.id,
            },
            correlation_id=original_message.correlation_id,
        )

    def get_context_from_state(self) -> str:
        """
        Get relevant context from project state for this agent.

        Returns:
            Formatted context string
        """
        context_parts = [
            f"Project: {self.project_state.name}",
            f"Description: {self.project_state.description}",
            f"Current Stage: {self.project_state.current_stage.value}",
        ]

        if self.project_state.requirements:
            context_parts.append(f"Requirements: {self.project_state.requirements}")

        if self.project_state.architecture:
            context_parts.append(f"Architecture: {self.project_state.architecture}")

        if self.project_state.design:
            context_parts.append(f"Design: {self.project_state.design}")

        # Add recent decisions
        if self.project_state.decisions:
            recent_decisions = self.project_state.decisions[-5:]
            context_parts.append(
                "Recent Decisions:\n" +
                "\n".join([f"- {d['decision']} (by {d['made_by']})"
                          for d in recent_decisions])
            )

        return "\n\n".join(context_parts)
