"""
Security Expert Agent - Application security, vulnerability assessment, and compliance.
"""

from typing import List, Optional
import logging

from resoftai.core.agent import Agent, AgentRole, AgentCapability
from resoftai.core.message_bus import Message, MessageType
from resoftai.core.state import WorkflowStage, TaskStatus

logger = logging.getLogger(__name__)


class SecurityExpertAgent(Agent):
    """
    Security Expert Agent responsible for:
    - Security vulnerability assessment
    - Code security review
    - Penetration testing guidance
    - Compliance verification
    - Security best practices
    - Threat modeling
    """

    @property
    def name(self) -> str:
        return "Security Expert"

    @property
    def system_prompt(self) -> str:
        return """You are an elite Security Expert with comprehensive knowledge of application security, infrastructure security, and compliance frameworks.

Your core responsibilities:
- Identify and remediate security vulnerabilities
- Conduct security code reviews
- Design secure architectures
- Ensure compliance with security standards
- Implement security best practices
- Perform threat modeling
- Guide penetration testing

Expertise Areas:

1. **OWASP Top 10**
   - Injection attacks (SQL, NoSQL, LDAP, OS Command)
   - Broken authentication and session management
   - Sensitive data exposure
   - XML External Entities (XXE)
   - Broken access control
   - Security misconfiguration
   - Cross-Site Scripting (XSS)
   - Insecure deserialization
   - Using components with known vulnerabilities
   - Insufficient logging and monitoring

2. **Authentication & Authorization**
   - OAuth 2.0 and OpenID Connect
   - JWT (JSON Web Tokens) best practices
   - Multi-factor authentication (MFA)
   - Role-Based Access Control (RBAC)
   - Attribute-Based Access Control (ABAC)
   - Session management
   - Password policies and storage (bcrypt, argon2)

3. **Data Protection**
   - Encryption at rest and in transit
   - TLS/SSL configuration
   - Key management
   - PII/PHI data handling
   - Data masking and anonymization
   - Secure data deletion
   - Database encryption

4. **API Security**
   - API authentication (API keys, OAuth, JWT)
   - Rate limiting and throttling
   - Input validation and sanitization
   - CORS configuration
   - API versioning security
   - GraphQL security
   - API gateway security

5. **Infrastructure Security**
   - Network segmentation
   - Firewall rules
   - Security groups
   - VPN and VPC configuration
   - DDoS protection
   - Intrusion detection/prevention (IDS/IPS)
   - Container security

6. **Compliance & Standards**
   - GDPR (General Data Protection Regulation)
   - HIPAA (Healthcare)
   - PCI DSS (Payment Card Industry)
   - SOC 2 Type II
   - ISO 27001
   - NIST Cybersecurity Framework
   - CIS Benchmarks

7. **Security Testing**
   - Static Application Security Testing (SAST)
   - Dynamic Application Security Testing (DAST)
   - Interactive Application Security Testing (IAST)
   - Software Composition Analysis (SCA)
   - Penetration testing methodologies
   - Vulnerability scanning
   - Fuzzing

8. **Secure Development**
   - Security Development Lifecycle (SDL)
   - Threat modeling (STRIDE, DREAD)
   - Secure coding guidelines
   - Code review security checklist
   - Dependency management
   - Secrets management (Vault, AWS Secrets Manager)
   - Security headers (CSP, HSTS, X-Frame-Options)

9. **Incident Response**
   - Security incident detection
   - Incident response procedures
   - Forensics and root cause analysis
   - Breach notification requirements
   - Security monitoring and SIEM
   - Security metrics and KPIs

Common Vulnerabilities and Mitigations:

**SQL Injection**
- Use parameterized queries/prepared statements
- Input validation and sanitization
- ORM usage
- Principle of least privilege for DB users

**XSS (Cross-Site Scripting)**
- Output encoding/escaping
- Content Security Policy (CSP)
- HTTPOnly and Secure cookie flags
- Input validation

**CSRF (Cross-Site Request Forgery)**
- CSRF tokens
- SameSite cookie attribute
- Referer/Origin header validation

**Authentication Bypass**
- Strong password policies
- Account lockout mechanisms
- MFA implementation
- Secure session management

**Sensitive Data Exposure**
- Encryption in transit (TLS 1.3)
- Encryption at rest
- Secure key storage
- Data classification

**Security Misconfiguration**
- Disable default accounts
- Remove unnecessary services
- Keep systems updated
- Security hardening checklists
- Regular security audits

**Insecure Deserialization**
- Avoid deserializing untrusted data
- Implement integrity checks
- Type validation
- Restricted deserialization

**Broken Access Control**
- Implement proper authorization checks
- Deny by default
- Log access control failures
- Enforce least privilege

Security Best Practices:
1. Defense in depth (multiple layers of security)
2. Principle of least privilege
3. Fail securely (secure defaults)
4. Separation of duties
5. Keep security simple (KISS principle)
6. Fix security issues correctly
7. Assume external systems are insecure
8. Security by design, not afterthought

When reviewing code for security:
1. Check for hardcoded credentials
2. Validate input validation
3. Review authentication/authorization logic
4. Check encryption usage
5. Review error handling (no sensitive info in errors)
6. Verify logging of security events
7. Check for timing attacks
8. Review third-party dependencies

Provide specific, actionable security recommendations with code examples and configuration samples."""

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="security_code_review",
                description="Review code for security vulnerabilities",
                input_schema={"code": "str", "language": "str", "framework": "str"},
                output_schema={"vulnerabilities": "list", "severity": "str", "recommendations": "list"}
            ),
            AgentCapability(
                name="threat_modeling",
                description="Perform threat modeling for application",
                input_schema={"architecture": "str", "assets": "list", "threat_actors": "list"},
                output_schema={"threats": "list", "attack_vectors": "list", "mitigations": "list"}
            ),
            AgentCapability(
                name="compliance_check",
                description="Verify compliance with security standards",
                input_schema={"standard": "str", "system_config": "dict"},
                output_schema={"compliance_status": "str", "gaps": "list", "remediation_steps": "list"}
            ),
            AgentCapability(
                name="penetration_test_plan",
                description="Create penetration testing plan",
                input_schema={"application": "str", "scope": "list", "objectives": "list"},
                output_schema={"test_plan": "str", "methodologies": "list", "tools": "list"}
            ),
        ]

    @property
    def responsible_stages(self) -> List[WorkflowStage]:
        """Stages this agent is responsible for."""
        return [
            WorkflowStage.QUALITY_ASSURANCE,  # Security testing
            WorkflowStage.TESTING,  # Security validation
            WorkflowStage.DEPLOYMENT,  # Security hardening
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
        """Process incoming messages related to security concerns."""
        if message.type == MessageType.AGENT_REQUEST:
            content_lower = message.content.lower()
            if "security" in content_lower or "vulnerability" in content_lower:
                return await self._handle_security_review(message)
            elif "compliance" in content_lower:
                return await self._handle_compliance_check(message)
            elif "threat" in content_lower:
                return await self._handle_threat_modeling(message)

        return None

    async def _handle_security_review(self, message: Message) -> Message:
        """Handle security review requests."""
        prompt = f"""Perform a comprehensive security review for:

{message.content}

Analyze and provide:
1. **Vulnerability Assessment**
   - Identify potential security vulnerabilities
   - Classify by severity (Critical, High, Medium, Low)
   - OWASP Top 10 alignment

2. **Security Best Practices**
   - Authentication and authorization
   - Data protection
   - Input validation
   - Error handling
   - Logging and monitoring

3. **Code-Level Security**
   - Hardcoded credentials
   - SQL injection risks
   - XSS vulnerabilities
   - CSRF protection
   - Insecure dependencies

4. **Remediation Recommendations**
   - Specific fixes with code examples
   - Priority and effort estimates
   - Testing procedures

5. **Security Checklist**
   - Implementation checklist
   - Verification steps

Provide detailed, actionable recommendations."""

        response = await self.generate(
            prompt=prompt,
            system_prompt=self.system_prompt
        )

        return Message(
            type=MessageType.AGENT_RESPONSE,
            sender=self.role,
            content=response,
            metadata={"capability": "security_review"}
        )

    async def _handle_compliance_check(self, message: Message) -> Message:
        """Handle compliance verification requests."""
        prompt = f"""Verify compliance for:

{message.content}

Provide comprehensive compliance assessment:
1. **Standard Requirements**
   - Specific requirements for the standard (GDPR, HIPAA, PCI DSS, etc.)
   - Mandatory controls
   - Optional but recommended controls

2. **Gap Analysis**
   - Current state assessment
   - Missing controls
   - Partial implementations

3. **Remediation Plan**
   - Steps to achieve compliance
   - Priority and timeline
   - Resource requirements

4. **Documentation Requirements**
   - Policies and procedures needed
   - Evidence and audit trails
   - Training requirements

5. **Ongoing Compliance**
   - Monitoring and maintenance
   - Regular audit procedures
   - Continuous improvement

Include specific compliance checklists."""

        response = await self.generate(
            prompt=prompt,
            system_prompt=self.system_prompt
        )

        return Message(
            type=MessageType.AGENT_RESPONSE,
            sender=self.role,
            content=response,
            metadata={"capability": "compliance_check"}
        )

    async def _handle_threat_modeling(self, message: Message) -> Message:
        """Handle threat modeling requests."""
        prompt = f"""Perform threat modeling for:

{message.content}

Use STRIDE methodology (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege):

1. **Asset Identification**
   - Valuable assets
   - Data flows
   - Trust boundaries

2. **Threat Enumeration**
   - Potential threats for each asset
   - Attack vectors
   - Threat actors

3. **Risk Assessment**
   - Likelihood and impact
   - DREAD scoring (Damage, Reproducibility, Exploitability, Affected users, Discoverability)
   - Risk prioritization

4. **Mitigation Strategies**
   - Security controls
   - Design changes
   - Process improvements

5. **Attack Trees**
   - Attack paths
   - Prerequisites
   - Detection opportunities

Provide visual threat model diagrams and detailed analysis."""

        response = await self.generate(
            prompt=prompt,
            system_prompt=self.system_prompt
        )

        return Message(
            type=MessageType.AGENT_RESPONSE,
            sender=self.role,
            content=response,
            metadata={"capability": "threat_modeling"}
        )
