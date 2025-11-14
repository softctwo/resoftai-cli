"""
DevOps Engineer Agent - CI/CD, Infrastructure, and Deployment expertise.
"""

from typing import List, Optional
import logging

from resoftai.core.agent import Agent, AgentRole, AgentCapability
from resoftai.core.message_bus import Message, MessageType
from resoftai.core.state import WorkflowStage, TaskStatus

logger = logging.getLogger(__name__)


class DevOpsEngineerAgent(Agent):
    """
    DevOps Engineer Agent responsible for:
    - CI/CD pipeline design and optimization
    - Infrastructure as Code (IaC)
    - Container orchestration
    - Deployment strategies
    - Monitoring and observability
    - Cloud infrastructure management
    """

    @property
    def name(self) -> str:
        return "DevOps Engineer"

    @property
    def system_prompt(self) -> str:
        return """You are an expert DevOps Engineer with deep knowledge of modern infrastructure, deployment, and operational practices.

Your core responsibilities:
- Design and implement CI/CD pipelines
- Manage infrastructure as code
- Configure container orchestration
- Implement deployment strategies
- Set up monitoring and logging
- Optimize cloud infrastructure
- Ensure system reliability and scalability

Expertise Areas:

1. **CI/CD Pipelines**
   - GitHub Actions, GitLab CI, Jenkins, CircleCI
   - Build automation and artifact management
   - Test automation integration
   - Deployment automation
   - Blue-green and canary deployments
   - Rollback strategies

2. **Infrastructure as Code**
   - Terraform for multi-cloud provisioning
   - CloudFormation for AWS
   - Ansible for configuration management
   - Pulumi for modern IaC
   - Version control for infrastructure

3. **Containerization & Orchestration**
   - Docker containerization best practices
   - Kubernetes cluster management
   - Helm charts for application deployment
   - Service mesh (Istio, Linkerd)
   - Container registry management

4. **Cloud Platforms**
   - AWS (EC2, ECS, EKS, Lambda, S3, RDS)
   - Azure (VMs, AKS, Functions, Blob Storage)
   - GCP (Compute Engine, GKE, Cloud Functions)
   - Multi-cloud strategies

5. **Monitoring & Observability**
   - Prometheus and Grafana for metrics
   - ELK Stack (Elasticsearch, Logstash, Kibana)
   - Datadog, New Relic for APM
   - Distributed tracing (Jaeger, Zipkin)
   - Alert management and on-call procedures

6. **Security & Compliance**
   - Secret management (Vault, AWS Secrets Manager)
   - Network security (VPC, Security Groups, Firewalls)
   - SSL/TLS certificate management
   - Compliance scanning (CIS benchmarks)
   - Vulnerability scanning

7. **Deployment Strategies**
   - Zero-downtime deployments
   - Blue-green deployment
   - Canary releases
   - Feature flags
   - Database migration strategies

8. **Performance Optimization**
   - Auto-scaling configuration
   - Load balancing
   - CDN setup and optimization
   - Database performance tuning
   - Caching strategies (Redis, Memcached)

Best Practices:
- Everything as Code (Infrastructure, Configuration, Policy)
- Immutable infrastructure
- Continuous deployment with safety checks
- Comprehensive monitoring and alerting
- Cost optimization
- Disaster recovery and business continuity
- Documentation for runbooks and procedures

When designing CI/CD pipelines:
1. Automated testing at every stage
2. Security scanning (SAST, DAST, dependency scanning)
3. Artifact versioning and tagging
4. Environment parity (dev, staging, production)
5. Automated rollback on failure
6. Deployment approvals for production
7. Post-deployment verification

When setting up infrastructure:
1. Use IaC for all resources
2. Implement least privilege access
3. Enable logging and monitoring from day one
4. Plan for scalability
5. Implement backup and recovery
6. Cost tagging and optimization
7. Security hardening

Provide detailed, actionable recommendations with specific tools, configurations, and best practices."""

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="design_cicd_pipeline",
                description="Design CI/CD pipeline for application deployment",
                input_schema={"project_type": "str", "tech_stack": "list", "deployment_target": "str"},
                output_schema={"pipeline_config": "str", "stages": "list", "tools": "list"}
            ),
            AgentCapability(
                name="infrastructure_as_code",
                description="Generate infrastructure as code templates",
                input_schema={"cloud_provider": "str", "resources": "list", "environment": "str"},
                output_schema={"iac_templates": "dict", "variables": "dict"}
            ),
            AgentCapability(
                name="containerization_strategy",
                description="Design containerization and orchestration strategy",
                input_schema={"application": "str", "services": "list", "scale_requirements": "dict"},
                output_schema={"dockerfiles": "dict", "k8s_manifests": "dict", "helm_charts": "dict"}
            ),
            AgentCapability(
                name="monitoring_setup",
                description="Configure monitoring and observability",
                input_schema={"application": "str", "metrics": "list", "sla_requirements": "dict"},
                output_schema={"monitoring_config": "dict", "dashboards": "list", "alerts": "list"}
            ),
        ]

    @property
    def responsible_stages(self) -> List[WorkflowStage]:
        """Stages this agent is responsible for."""
        return [
            WorkflowStage.DEPLOYMENT,
            WorkflowStage.TESTING,  # CI/CD integration testing
        ]

    async def process_request(self, message: Message) -> None:
        """Process incoming requests."""
        # Delegate to the process method for compatibility
        await self.process(message)

    async def handle_task_assignment(self, message: Message) -> None:
        """Handle task assignments."""
        task_id = message.content.get("task_id")
        task = message.content.get("task")
        logger.info(f"{self.name} received task assignment: {task_id} - {task}")

    async def process(self, message: Message) -> Optional[Message]:
        """Process incoming messages related to DevOps concerns."""
        if message.type == MessageType.AGENT_REQUEST:
            if "cicd" in message.content.lower() or "deployment" in message.content.lower():
                return await self._handle_cicd_request(message)
            elif "infrastructure" in message.content.lower():
                return await self._handle_infrastructure_request(message)
            elif "monitoring" in message.content.lower():
                return await self._handle_monitoring_request(message)

        return None

    async def _handle_cicd_request(self, message: Message) -> Message:
        """Handle CI/CD pipeline design requests."""
        prompt = f"""Design a comprehensive CI/CD pipeline for the following requirements:

{message.content}

Provide:
1. Pipeline stages (build, test, security scan, deploy)
2. Recommended tools and technologies
3. Configuration examples (GitHub Actions, GitLab CI, etc.)
4. Deployment strategy (blue-green, canary, etc.)
5. Rollback procedures
6. Environment-specific configurations

Be specific and provide actual YAML/configuration examples."""

        response = await self.generate(
            prompt=prompt,
            system_prompt=self.system_prompt
        )

        return Message(
            type=MessageType.AGENT_RESPONSE,
            sender=self.role,
            content=response,
            metadata={"capability": "cicd_pipeline_design"}
        )

    async def _handle_infrastructure_request(self, message: Message) -> Message:
        """Handle infrastructure as code requests."""
        prompt = f"""Generate Infrastructure as Code for:

{message.content}

Provide:
1. Terraform/CloudFormation templates
2. Resource definitions
3. Network configuration
4. Security groups and IAM policies
5. Scaling and availability setup
6. Cost optimization recommendations

Include complete, production-ready configurations."""

        response = await self.generate(
            prompt=prompt,
            system_prompt=self.system_prompt
        )

        return Message(
            type=MessageType.AGENT_RESPONSE,
            sender=self.role,
            content=response,
            metadata={"capability": "infrastructure_as_code"}
        )

    async def _handle_monitoring_request(self, message: Message) -> Message:
        """Handle monitoring and observability requests."""
        prompt = f"""Configure monitoring and observability for:

{message.content}

Provide:
1. Metrics to track (application, infrastructure, business)
2. Logging configuration
3. Alerting rules and thresholds
4. Dashboard configurations
5. Distributed tracing setup
6. On-call procedures

Include specific configurations for Prometheus, Grafana, ELK, etc."""

        response = await self.generate(
            prompt=prompt,
            system_prompt=self.system_prompt
        )

        return Message(
            type=MessageType.AGENT_RESPONSE,
            sender=self.role,
            content=response,
            metadata={"capability": "monitoring_setup"}
        )
