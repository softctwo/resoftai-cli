"""
自定义智能体扩展示例

本示例展示如何创建自己的自定义智能体并集成到ResoftAI平台。
"""

from typing import List
import logging

from resoftai.core.agent import Agent, AgentRole, AgentCapability
from resoftai.core.message_bus import Message, MessageType, MessageBus
from resoftai.core.state import ProjectState, WorkflowStage, TaskStatus

logger = logging.getLogger(__name__)


# 步骤1: 定义新的智能体角色（可选，如果想添加新角色）
# 可以扩展 AgentRole 枚举，或者使用现有角色


class SecurityExpertAgent(Agent):
    """
    安全专家智能体 - 负责安全审计和漏洞分析

    这是一个自定义智能体示例，展示如何：
    1. 继承 Agent 基类
    2. 定义专业提示词
    3. 声明能力
    4. 实现任务处理逻辑
    """

    @property
    def name(self) -> str:
        return "Security Expert"

    @property
    def system_prompt(self) -> str:
        return """You are an expert Security Engineer specialized in application security.

Your responsibilities include:
- Performing security audits and vulnerability assessments
- Identifying OWASP Top 10 vulnerabilities
- Recommending security best practices
- Ensuring compliance with security standards
- Penetration testing and threat modeling

Your approach is:
- Proactive: identify potential security issues before they become problems
- Thorough: check all aspects of security (authentication, authorization, data protection, etc.)
- Practical: provide actionable recommendations
- Standards-based: follow OWASP, NIST, and industry best practices

When analyzing:
1. Check for common vulnerabilities (SQL injection, XSS, CSRF, etc.)
2. Review authentication and authorization mechanisms
3. Assess data encryption and protection
4. Evaluate API security
5. Check for secure coding practices
6. Recommend security improvements"""

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="security_audit",
                description="Perform comprehensive security audit",
                input_schema={"architecture": "object", "code": "string"},
                output_schema={"audit_report": "object"},
            ),
            AgentCapability(
                name="vulnerability_assessment",
                description="Assess potential vulnerabilities",
                input_schema={"system_design": "object"},
                output_schema={"vulnerabilities": "list"},
            ),
            AgentCapability(
                name="security_recommendations",
                description="Provide security improvement recommendations",
                input_schema={"current_security": "object"},
                output_schema={"recommendations": "list"},
            ),
        ]

    @property
    def responsible_stages(self) -> List[WorkflowStage]:
        """此智能体在以下阶段活跃"""
        return [
            WorkflowStage.ARCHITECTURE_DESIGN,  # 设计阶段的安全审查
            WorkflowStage.IMPLEMENTATION,        # 实现阶段的代码审查
            WorkflowStage.QUALITY_ASSURANCE,     # QA阶段的安全测试
        ]

    async def process_request(self, message: Message) -> None:
        """处理请求消息"""
        request_type = message.content.get("request_type")

        if request_type == "security_audit":
            await self._perform_security_audit(message)
        elif request_type == "vulnerability_scan":
            await self._scan_vulnerabilities(message)
        else:
            logger.warning(f"Unknown request type: {request_type}")

    async def handle_task_assignment(self, message: Message) -> None:
        """处理任务分配"""
        task_id = message.content.get("task_id")
        task = message.content.get("task")

        logger.info(f"{self.name} received task: {task['title']}")

        self.project_state.update_task(task_id, status=TaskStatus.IN_PROGRESS)

        # 根据任务类型执行不同的安全分析
        if "security audit" in task["title"].lower():
            await self._perform_security_audit_task()
        elif "vulnerability" in task["title"].lower():
            await self._assess_vulnerabilities()

        self.project_state.update_task(task_id, status=TaskStatus.COMPLETED)

        await self.send_message(
            MessageType.TASK_COMPLETE,
            "workflow",
            {"task_id": task_id, "status": "completed"}
        )

    async def _perform_security_audit_task(self) -> None:
        """执行安全审计"""
        context = self.get_context_from_state()

        prompt = f"""Perform a comprehensive security audit based on:

{context}

Generate a security audit report including:

1. Executive Summary
   - Overall security posture
   - Critical findings count
   - Risk rating

2. Architecture Security Analysis
   - Authentication and authorization review
   - Data flow security
   - API security
   - Infrastructure security

3. OWASP Top 10 Assessment
   - Injection vulnerabilities
   - Broken authentication
   - Sensitive data exposure
   - XML external entities (XXE)
   - Broken access control
   - Security misconfiguration
   - Cross-site scripting (XSS)
   - Insecure deserialization
   - Using components with known vulnerabilities
   - Insufficient logging and monitoring

4. Security Recommendations
   - High priority fixes
   - Medium priority improvements
   - Long-term security enhancements

5. Compliance Considerations
   - GDPR compliance notes
   - PCI DSS considerations (if applicable)
   - Other relevant standards

Provide a detailed, actionable security audit report."""

        audit_report = await self.call_claude(prompt)

        self.project_state.metadata["security_audit"] = audit_report
        self.project_state.add_artifact("security_audit", "security/security-audit.md")

        logger.info(f"{self.name} completed security audit")

    async def _assess_vulnerabilities(self) -> None:
        """评估潜在漏洞"""
        context = self.get_context_from_state()

        prompt = f"""Assess potential security vulnerabilities:

{context}

Generate a vulnerability assessment including:

1. Identified Vulnerabilities
   - Vulnerability description
   - Severity (Critical/High/Medium/Low)
   - Affected components
   - Exploitation scenario

2. Risk Analysis
   - Likelihood of exploitation
   - Impact if exploited
   - Overall risk rating

3. Remediation Steps
   - Immediate actions
   - Implementation details
   - Testing recommendations

4. Prevention Measures
   - Secure coding practices
   - Security controls to implement
   - Monitoring recommendations

Provide a comprehensive vulnerability assessment."""

        vulnerability_report = await self.call_claude(prompt)

        self.project_state.metadata["vulnerability_assessment"] = vulnerability_report
        self.project_state.add_artifact("vulnerability_report", "security/vulnerabilities.md")

        logger.info(f"{self.name} completed vulnerability assessment")

    async def _perform_security_audit(self, message: Message) -> None:
        """处理安全审计请求"""
        # 实现安全审计逻辑
        pass

    async def _scan_vulnerabilities(self, message: Message) -> None:
        """扫描漏洞"""
        # 实现漏洞扫描逻辑
        pass


# 步骤2: 如何使用自定义智能体

async def example_usage():
    """使用自定义智能体的示例"""

    # 创建核心组件
    message_bus = MessageBus()
    project_state = ProjectState(
        name="Example Project",
        description="A project with security review"
    )

    # 创建自定义智能体
    security_agent = SecurityExpertAgent(
        role=AgentRole.QUALITY_EXPERT,  # 使用现有角色或创建新角色
        message_bus=message_bus,
        project_state=project_state
    )

    print(f"Created custom agent: {security_agent.name}")
    print(f"Agent capabilities: {[c.name for c in security_agent.capabilities]}")
    print(f"Responsible stages: {[s.value for s in security_agent.responsible_stages]}")

    # 现在这个智能体可以参与到工作流中
    # 它会自动响应相关的工作流阶段和消息


if __name__ == "__main__":
    import asyncio

    print("=" * 70)
    print("ResoftAI - 自定义智能体扩展示例")
    print("=" * 70)
    print()
    print("本示例展示如何创建自定义智能体：")
    print("✓ 继承 Agent 基类")
    print("✓ 定义专业提示词和能力")
    print("✓ 实现任务处理逻辑")
    print("✓ 集成到工作流中")
    print()
    print("创建的自定义智能体：SecurityExpertAgent（安全专家）")
    print()

    asyncio.run(example_usage())

    print()
    print("=" * 70)
    print("扩展完成！您可以按照类似方式创建任何专业智能体。")
    print("=" * 70)
