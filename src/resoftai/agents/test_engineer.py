"""
Test Engineer Agent - Designs and executes software testing.
"""

from typing import List
import logging

from resoftai.core.agent import Agent, AgentRole, AgentCapability
from resoftai.core.message_bus import Message, MessageType
from resoftai.core.state import WorkflowStage, TaskStatus

logger = logging.getLogger(__name__)


class TestEngineerAgent(Agent):
    """
    Test Engineer Agent responsible for:
    - Test strategy and planning
    - Test case design
    - Test execution
    - Quality metrics tracking
    - Bug reporting
    """

    @property
    def name(self) -> str:
        return "Test Engineer"

    @property
    def system_prompt(self) -> str:
        return """You are an expert Test Engineer with comprehensive knowledge of software testing methodologies.

Your responsibilities include:
- Designing comprehensive test strategies
- Creating detailed test plans and test cases
- Performing various types of testing (unit, integration, system, etc.)
- Identifying and documenting defects
- Tracking quality metrics
- Ensuring software meets quality standards

Your testing approach:
- Comprehensive: cover all scenarios including edge cases
- Systematic: follow structured testing methodologies
- Risk-based: prioritize testing based on risk
- Automated where appropriate
- Documented: maintain clear test documentation

When testing:
1. Design test cases that cover all requirements
2. Include positive and negative test scenarios
3. Test edge cases and boundary conditions
4. Verify error handling
5. Ensure accessibility and usability
6. Document all findings clearly"""

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="test_planning",
                description="Create comprehensive test plans",
                input_schema={"requirements": "object"},
                output_schema={"test_plan": "object"},
            ),
            AgentCapability(
                name="test_case_design",
                description="Design detailed test cases",
                input_schema={"features": "object"},
                output_schema={"test_cases": "list"},
            ),
        ]

    @property
    def responsible_stages(self) -> List[WorkflowStage]:
        return [
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

        if "test plan" in task["title"].lower():
            await self._create_test_plan()
        elif "execute" in task["title"].lower():
            await self._execute_tests()

        self.project_state.update_task(task_id, status=TaskStatus.COMPLETED)

        await self.send_message(
            MessageType.TASK_COMPLETE,
            "workflow",
            {"task_id": task_id, "status": "completed"}
        )

    async def _create_test_plan(self) -> None:
        """Create comprehensive test plan."""
        context = self.get_context_from_state()

        prompt = f"""Create a comprehensive test plan based on:

{context}

Include:

1. Test Strategy
   - Testing objectives
   - Scope (in-scope and out-of-scope)
   - Testing approach
   - Test levels (unit, integration, system, acceptance)

2. Test Types
   - Functional testing
   - Non-functional testing (performance, security, usability)
   - Regression testing
   - User acceptance testing

3. Test Cases
   - Detailed test cases for all major features
   - Test case format: ID, Description, Preconditions, Steps, Expected Result
   - Priority levels
   - Test data requirements

4. Test Environment
   - Hardware requirements
   - Software requirements
   - Test data setup
   - Configuration needs

5. Test Schedule
   - Test phases
   - Timeline
   - Resource allocation

6. Test Deliverables
   - Test documentation
   - Test reports
   - Defect reports

7. Entry and Exit Criteria
   - When to start testing
   - When testing is complete

8. Risk Assessment
   - Testing risks
   - Mitigation strategies

9. Test Automation
   - Automation strategy
   - Tools and frameworks
   - Automated test coverage

Provide a detailed, actionable test plan."""

        test_plan = await self.call_claude(prompt)

        self.project_state.metadata["test_plan"] = test_plan
        self.project_state.add_artifact("test_plan", "testing/test-plan.md")

        logger.info(f"{self.name} created test plan")

    async def _execute_tests(self) -> None:
        """Execute tests and document results."""
        context = self.get_context_from_state()

        prompt = f"""Create a test execution guide and template results based on:

{context}

Provide:

1. Test Execution Guide
   - Test execution process
   - How to report defects
   - How to document results

2. Test Cases Checklist
   - All test cases organized by feature
   - Execution status template

3. Sample Test Results
   - Test execution summary template
   - Pass/fail criteria
   - Defect tracking template

4. Test Metrics
   - Test coverage metrics
   - Defect density
   - Test execution progress

5. Test Report Template
   - Executive summary
   - Test results by module
   - Defect summary
   - Quality assessment
   - Recommendations

6. Common Test Scenarios
   - Critical path testing
   - Edge case testing
   - Error handling verification
   - Performance testing scenarios

Provide comprehensive testing documentation."""

        test_execution = await self.call_claude(prompt)

        self.project_state.metadata["test_execution"] = test_execution
        self.project_state.add_artifact("test_results", "testing/test-results.md")

        logger.info(f"{self.name} documented test execution")
