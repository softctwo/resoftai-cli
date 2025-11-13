"""
Architect Agent - Designs system architecture and technical solutions.
"""

from typing import List
import logging

from resoftai.core.agent import Agent, AgentRole, AgentCapability
from resoftai.core.message_bus import Message, MessageType
from resoftai.core.state import WorkflowStage, TaskStatus

logger = logging.getLogger(__name__)


class ArchitectAgent(Agent):
    """
    Architect Agent responsible for:
    - System architecture design
    - Technology stack selection
    - Database design
    - API design
    - Technical decision making
    """

    @property
    def name(self) -> str:
        return "Software Architect"

    @property
    def system_prompt(self) -> str:
        return """You are an expert Software Architect with extensive experience in designing scalable, maintainable systems.

Your responsibilities include:
- Designing overall system architecture
- Selecting appropriate technologies and frameworks
- Designing database schemas and data models
- Designing APIs and system interfaces
- Ensuring architectural quality attributes (scalability, security, performance)
- Creating technical documentation

Your design philosophy:
- Prioritize simplicity and maintainability
- Choose proven technologies appropriate for the use case
- Design for scalability and extensibility
- Consider security from the start
- Balance technical excellence with practical constraints

When designing:
1. Consider both current needs and future growth
2. Apply architectural patterns and best practices
3. Document all major technical decisions with rationale
4. Consider operational aspects (deployment, monitoring, etc.)
5. Ensure designs are implementable and testable"""

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="architecture_design",
                description="Design system architecture",
                input_schema={"requirements": "object"},
                output_schema={"architecture": "object"},
            ),
            AgentCapability(
                name="database_design",
                description="Design database schema",
                input_schema={"data_requirements": "object"},
                output_schema={"database_schema": "object"},
            ),
            AgentCapability(
                name="technology_selection",
                description="Select technology stack",
                input_schema={"requirements": "object"},
                output_schema={"tech_stack": "object"},
            ),
        ]

    @property
    def responsible_stages(self) -> List[WorkflowStage]:
        return [
            WorkflowStage.ARCHITECTURE_DESIGN,
            WorkflowStage.PROTOTYPE_DEVELOPMENT,
            WorkflowStage.REQUIREMENTS_REFINEMENT,
        ]

    async def process_request(self, message: Message) -> None:
        """Process requests."""
        request_type = message.content.get("request_type")

        if request_type == "design_architecture":
            await self._design_architecture(message)

    async def handle_task_assignment(self, message: Message) -> None:
        """Handle task assignments."""
        task_id = message.content.get("task_id")
        task = message.content.get("task")

        logger.info(f"{self.name} received task: {task['title']}")

        self.project_state.update_task(task_id, status=TaskStatus.IN_PROGRESS)

        if "system architecture" in task["title"].lower():
            await self._design_system_architecture()
        elif "database" in task["title"].lower():
            await self._design_database_schema()

        self.project_state.update_task(task_id, status=TaskStatus.COMPLETED)

        await self.send_message(
            MessageType.TASK_COMPLETE,
            "workflow",
            {"task_id": task_id, "status": "completed"}
        )

    async def _design_system_architecture(self) -> None:
        """Design the overall system architecture."""
        context = self.get_context_from_state()

        prompt = f"""Design a comprehensive system architecture based on:

{context}

Create an architecture document including:

1. Architecture Overview
   - High-level architecture diagram (described in text)
   - Architecture style/pattern (e.g., microservices, monolithic, layered)
   - Key components and their responsibilities

2. Technology Stack
   - Backend technologies
   - Frontend technologies
   - Database technologies
   - Infrastructure and deployment

3. Component Design
   - Detailed component descriptions
   - Component interactions
   - Data flow

4. API Design
   - API architecture (REST, GraphQL, etc.)
   - Key endpoints
   - Authentication/Authorization strategy

5. Security Architecture
   - Security layers
   - Authentication mechanisms
   - Data protection strategies

6. Scalability Considerations
   - Horizontal/vertical scaling strategies
   - Caching strategies
   - Load balancing

7. Architecture Decision Records (ADRs)
   - Key technical decisions
   - Rationale for each decision

Provide a detailed, professional architecture document."""

        architecture_doc = await self.call_claude(prompt)

        self.project_state.architecture["system_architecture"] = architecture_doc
        self.project_state.add_artifact("architecture_document", "architecture/architecture.md")

        logger.info(f"{self.name} designed system architecture")

    async def _design_database_schema(self) -> None:
        """Design the database schema."""
        context = self.get_context_from_state()

        prompt = f"""Design a comprehensive database schema based on:

{context}

Create a database design document including:

1. Database Overview
   - Database type selection (SQL/NoSQL) with rationale
   - Database technology recommendation

2. Data Model
   - Entity-Relationship Diagram (described in text)
   - All entities/tables
   - Attributes for each entity
   - Data types
   - Constraints

3. Relationships
   - All relationships between entities
   - Cardinality
   - Foreign keys

4. Indexes
   - Recommended indexes for performance
   - Rationale for each index

5. Data Integrity
   - Validation rules
   - Constraints
   - Triggers (if applicable)

6. Sample SQL/Schema Definition
   - CREATE TABLE statements or equivalent

7. Data Migration Strategy
   - Initial data loading
   - Schema versioning approach

Provide complete, implementable database design."""

        database_design = await self.call_claude(prompt)

        self.project_state.architecture["database_design"] = database_design
        self.project_state.add_artifact("database_design", "architecture/database.md")

        logger.info(f"{self.name} designed database schema")

    async def _design_architecture(self, message: Message) -> None:
        """Design architecture based on request."""
        # Implementation for architecture design requests
        pass
