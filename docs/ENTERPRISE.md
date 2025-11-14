# ResoftAI Enterprise Edition

ResoftAI Enterprise Edition provides advanced features for organizations requiring enterprise-grade security, scalability, and customization.

## Table of Contents

- [Enterprise Features](#enterprise-features)
- [Private Deployment](#private-deployment)
- [Plugin System](#plugin-system)
- [Marketplace and Community](#marketplace-and-community)
- [Setup and Configuration](#setup-and-configuration)
- [Security](#security)
- [Scalability](#scalability)

---

## Enterprise Features

### 1. Organization and Team Management

#### Organizations
- **Multi-tenant architecture**: Isolate data and resources per organization
- **Subscription tiers**: Free, Starter, Professional, Enterprise
- **Customizable settings**: Per-organization configuration
- **SSO/SAML support**: Enterprise authentication integration

#### Teams
- **Hierarchical organization**: Organize users into teams
- **Role-based access**: Owner, Admin, Member, Viewer
- **Team-specific resources**: Projects, configurations, and permissions scoped to teams
- **Collaboration features**: Shared projects and real-time editing

### 2. Role-Based Access Control (RBAC)

#### Permission System
```python
# Permission format: resource.action
examples = [
    "project.create",
    "project.read",
    "project.update",
    "project.delete",
    "user.invite",
    "team.manage",
    "plugin.install",
]
```

#### Built-in Roles
- **Super Admin**: Full system access
- **Organization Admin**: Manage organization and teams
- **Team Admin**: Manage team members and resources
- **Developer**: Create and manage projects
- **Viewer**: Read-only access

#### Custom Roles
Create custom roles with fine-grained permissions:

```python
# Example: Create a custom role
await create_role(
    db=db,
    name="QA Engineer",
    code="qa_engineer",
    description="Can view projects and run tests",
    organization_id=org_id
)

# Assign permissions
await assign_permission_to_role(
    db=db,
    role_id=role.id,
    permission_id=permission.id
)
```

### 3. Quota Management

#### Resource Quotas
Track and enforce limits on:
- **Projects**: Maximum number of projects
- **API Calls**: API requests per month
- **Storage**: File storage limits
- **Team Members**: Maximum team size
- **LLM Tokens**: Token consumption limits

#### Quota Configuration

```python
# Set quotas for an organization
await create_quota(
    db=db,
    organization_id=org_id,
    resource_type=ResourceType.PROJECTS,
    limit_value=100,
    period="monthly",
    warning_threshold=0.8  # Warn at 80%
)
```

#### Usage Tracking

```python
# Record usage
await record_usage(
    db=db,
    organization_id=org_id,
    resource_type=ResourceType.LLM_TOKENS,
    amount=1500,
    user_id=user_id,
    metadata={"model": "deepseek-chat"}
)

# Check quota before operation
can_consume, error = await check_quota(
    db=db,
    organization_id=org_id,
    resource_type=ResourceType.PROJECTS,
    amount=1
)
```

### 4. Audit Logging

#### Comprehensive Logging
Track all important actions for compliance and security:

```python
await create_audit_log(
    db=db,
    action=AuditAction.CREATE,
    resource_type="project",
    resource_id=project.id,
    user_id=user.id,
    organization_id=org_id,
    description="Created new project",
    changes={"name": "New Project", "status": "pending"},
    ip_address=request.client.host,
    user_agent=request.headers.get("user-agent")
)
```

#### Audit Features
- **Immutable logs**: Cannot be modified or deleted
- **Detailed tracking**: Who, what, when, where, why
- **Change history**: Before/after states for updates
- **Compliance ready**: GDPR, SOC2, HIPAA compliance support
- **Export capabilities**: JSON, CSV export for analysis
- **Retention policies**: Configurable retention periods

---

## Private Deployment

### Deployment Options

#### 1. Docker Deployment

**Quick Start:**
```bash
# Clone repository
git clone https://github.com/yourorg/resoftai-cli.git
cd resoftai-cli

# Copy and configure environment
cp .env.enterprise.example .env
# Edit .env with your configuration

# Start services
cd deployment/docker
docker-compose -f docker-compose.production.yml up -d
```

**Services Included:**
- PostgreSQL database
- Redis cache
- ResoftAI API server
- Nginx reverse proxy
- Background worker

**Configuration:**
- Edit `docker-compose.production.yml` for service configuration
- Update `.env` for application settings
- SSL certificates in `deployment/docker/ssl/`

#### 2. Kubernetes Deployment

**Prerequisites:**
- Kubernetes cluster (1.24+)
- kubectl configured
- Helm 3 (optional)

**Deployment:**
```bash
# Apply Kubernetes manifests
kubectl apply -f deployment/kubernetes/deployment.yaml

# Or use Helm (if available)
helm install resoftai ./deployment/helm \
  --namespace resoftai \
  --create-namespace \
  --values values.production.yaml
```

**Features:**
- **High availability**: 3+ replicas with auto-scaling
- **Health checks**: Liveness and readiness probes
- **Resource limits**: CPU and memory constraints
- **Persistent storage**: PostgreSQL and Redis data persistence
- **Secrets management**: Kubernetes secrets for sensitive data
- **Ingress**: HTTPS with automatic certificate management

#### 3. Bare Metal / VM Deployment

**System Requirements:**
- Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Nginx (optional, for reverse proxy)

**Installation:**
```bash
# Install dependencies
sudo apt update
sudo apt install python3.11 python3.11-venv postgresql redis-server nginx

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install ResoftAI
pip install -e .

# Configure database
sudo -u postgres createdb resoftai
sudo -u postgres createuser resoftai -P

# Run migrations
alembic upgrade head

# Start server
gunicorn resoftai.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Network Configuration

#### Firewall Rules
```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow database (internal only)
sudo ufw allow from 10.0.0.0/8 to any port 5432
```

#### Nginx Configuration
See `deployment/docker/nginx.conf` for production-ready Nginx configuration.

### Database Management

#### Backup Strategy
```bash
# Automatic daily backups
0 2 * * * pg_dump resoftai | gzip > /backups/resoftai_$(date +\%Y\%m\%d).sql.gz

# Backup retention (keep 30 days)
find /backups -name "resoftai_*.sql.gz" -mtime +30 -delete
```

#### Database Restore
```bash
# Restore from backup
gunzip -c /backups/resoftai_20241114.sql.gz | psql resoftai
```

---

## Plugin System

### Overview
The plugin system allows extending ResoftAI with custom functionality without modifying the core codebase.

### Plugin Architecture

```
plugins/
├── plugin.json              # Plugin manifest
├── __init__.py
├── main.py                  # Plugin entry point
└── README.md
```

### Plugin Types

1. **Agent Plugins**: Add custom agents
2. **LLM Provider Plugins**: Support additional LLM providers
3. **Integration Plugins**: Connect to external services
4. **Workflow Plugins**: Custom project workflows
5. **Code Quality Plugins**: Linters and formatters
6. **Template Plugins**: Project templates

### Creating a Plugin

#### 1. Plugin Manifest (`plugin.json`)

```json
{
  "name": "Custom Security Scanner",
  "slug": "security-scanner",
  "version": "1.0.0",
  "description": "Scans code for security vulnerabilities",
  "author": "Your Name",
  "category": "code_quality",
  "tags": ["security", "scanning"],
  "min_platform_version": "0.2.0",
  "dependencies": [],
  "entry_point": "main.py:SecurityScannerPlugin",
  "license": "MIT",
  "homepage": "https://github.com/yourname/security-scanner",
  "repository": "https://github.com/yourname/security-scanner"
}
```

#### 2. Plugin Implementation (`main.py`)

```python
from resoftai.plugins.base import CodeQualityPlugin, PluginContext

class SecurityScannerPlugin(CodeQualityPlugin):
    """Security vulnerability scanner plugin"""

    def load(self, context: PluginContext) -> bool:
        """Initialize plugin"""
        self.context = context
        self.context.log_info(f"Loading {self.metadata.name}")
        return True

    def activate(self) -> bool:
        """Activate plugin and register hooks"""
        self.context.log_info(f"Activating {self.metadata.name}")

        # Register hook for code analysis
        context.hooks.register_filter(
            "code.analyze",
            self.scan_code,
            priority=5
        )
        return True

    def deactivate(self) -> bool:
        """Deactivate plugin"""
        # Unregister hooks
        return True

    def unload(self) -> bool:
        """Clean up resources"""
        return True

    def get_tool_name(self) -> str:
        return "security_scanner"

    async def analyze_code(self, code: str, language: str) -> dict:
        """Scan code for security issues"""
        issues = []

        # Example: Check for SQL injection
        if "execute(" in code and "%" in code:
            issues.append({
                "severity": "high",
                "type": "sql_injection",
                "message": "Potential SQL injection vulnerability"
            })

        return {
            "issues": issues,
            "score": 100 - len(issues) * 10
        }

    async def scan_code(self, analysis_result: dict) -> dict:
        """Filter hook for code analysis"""
        # Add security scan results
        security_results = await self.analyze_code(
            analysis_result.get("code", ""),
            analysis_result.get("language", "")
        )

        analysis_result["security"] = security_results
        return analysis_result
```

#### 3. Configuration Schema

```python
def get_config_schema(self) -> dict:
    """Return JSON Schema for plugin configuration"""
    return {
        "type": "object",
        "properties": {
            "severity_threshold": {
                "type": "string",
                "enum": ["low", "medium", "high", "critical"],
                "default": "medium"
            },
            "scan_dependencies": {
                "type": "boolean",
                "default": True
            }
        }
    }
```

### Installing Plugins

#### Via API
```bash
curl -X POST http://localhost:8000/api/plugins/install \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plugin_id": 123,
    "config": {
      "severity_threshold": "high"
    }
  }'
```

#### Via CLI
```bash
resoftai plugin install security-scanner --config severity_threshold=high
```

#### Manual Installation
```bash
# Copy plugin to plugins directory
cp -r /path/to/security-scanner /app/plugins/

# Restart ResoftAI to load plugin
systemctl restart resoftai
```

---

## Marketplace and Community

### Plugin Marketplace

#### Features
- **Discover plugins**: Browse by category, popularity, rating
- **Plugin details**: Screenshots, documentation, reviews
- **One-click install**: Install plugins directly from marketplace
- **Automatic updates**: Keep plugins up to date
- **Security scanning**: All plugins are scanned for vulnerabilities

#### Publishing Plugins

1. **Create Plugin**: Develop your plugin following the guidelines
2. **Test Locally**: Test thoroughly in development environment
3. **Submit**: Submit to marketplace for review
4. **Review Process**: Security and quality checks
5. **Approval**: Plugin becomes available in marketplace

```bash
# Submit plugin
resoftai plugin submit /path/to/plugin \
  --category code_quality \
  --tags security,scanning
```

### Community Features

#### Plugin Collections
Create and share curated plugin lists:

```bash
# Create collection
resoftai collection create "Security Tools" \
  --description "Essential security plugins" \
  --plugins security-scanner,dependency-checker,secret-detector
```

#### Reviews and Ratings
- **Rate plugins**: 1-5 star ratings
- **Write reviews**: Share your experience
- **Helpful votes**: Community-driven quality signals

#### Comments and Discussions
- **Ask questions**: Plugin-specific Q&A
- **Share tips**: Best practices and use cases
- **Report issues**: Bug reports and feature requests

---

## Setup and Configuration

### Initial Setup

#### 1. Create Super Admin

```bash
# Create first admin user
python -m resoftai.cli.admin create-user \
  --username admin \
  --email admin@yourcompany.com \
  --role admin \
  --password
```

#### 2. Create Organization

```bash
# Via CLI
python -m resoftai.cli.admin create-org \
  --name "Your Company" \
  --slug your-company \
  --tier enterprise \
  --admin-email admin@yourcompany.com
```

Or via API:
```bash
curl -X POST http://localhost:8000/api/organizations \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Your Company",
    "slug": "your-company",
    "tier": "enterprise",
    "contact_email": "admin@yourcompany.com"
  }'
```

#### 3. Configure SSO (Optional)

```bash
# SAML Configuration
python -m resoftai.cli.admin configure-sso \
  --org your-company \
  --provider saml \
  --entity-id "https://resoftai.yourdomain.com/saml" \
  --sso-url "https://idp.yourdomain.com/saml/sso" \
  --certificate /path/to/idp-cert.pem
```

#### 4. Set Up Quotas

```python
# Configure quotas for organization
from resoftai.crud.enterprise import create_quota
from resoftai.models.enterprise import ResourceType

quotas = [
    (ResourceType.PROJECTS, 1000, None),
    (ResourceType.API_CALLS, 100000, "monthly"),
    (ResourceType.STORAGE, 100_000_000_000, None),  # 100GB
    (ResourceType.LLM_TOKENS, 10_000_000, "monthly"),
]

for resource, limit, period in quotas:
    await create_quota(
        db=db,
        organization_id=org_id,
        resource_type=resource,
        limit_value=limit,
        period=period
    )
```

### Environment Variables

See `.env.enterprise.example` for all available configuration options.

**Critical Settings:**
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Strong random key for JWT signing
- `LLM_API_KEY`: Your LLM provider API key
- `ENTERPRISE_MODE`: Set to `true`
- `LICENSE_KEY`: Enterprise license key

---

## Security

### Best Practices

#### 1. Secure Secrets
- Never commit `.env` files
- Use environment variables or secrets management (Vault, AWS Secrets Manager)
- Rotate secrets regularly
- Use strong passwords (minimum 16 characters)

#### 2. Network Security
- Use HTTPS only (TLS 1.2+)
- Implement rate limiting
- Use firewall rules to restrict access
- Enable CORS only for trusted origins

#### 3. Database Security
- Use strong database passwords
- Restrict database access to application servers only
- Enable SSL for database connections
- Regular backups and disaster recovery testing

#### 4. Application Security
- Keep dependencies updated
- Enable audit logging
- Implement RBAC properly
- Validate all user inputs
- Use parameterized queries (SQLAlchemy handles this)

### Compliance

#### GDPR Compliance
- **Data minimization**: Collect only necessary data
- **Right to access**: Users can export their data
- **Right to deletion**: Users can delete their accounts
- **Audit trails**: All data access logged
- **Data encryption**: At rest and in transit

#### SOC2 Compliance
- **Access controls**: RBAC and SSO
- **Audit logging**: Comprehensive activity logs
- **Monitoring**: Real-time alerts and metrics
- **Backup and recovery**: Regular backups and tested recovery

---

## Scalability

### Performance Optimization

#### 1. Database Optimization
```python
# Connection pooling
DATABASE_URL=postgresql+asyncpg://...?pool_size=20&max_overflow=40

# Indexing (already configured in models)
# - All foreign keys indexed
# - Common query fields indexed
# - Composite indexes for frequent joins
```

#### 2. Caching
```python
# Redis caching
REDIS_ENABLED=true
CACHE_TTL=3600
CACHE_MAX_SIZE=1000
```

#### 3. Horizontal Scaling
```yaml
# Kubernetes auto-scaling
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: resoftai-api-hpa
spec:
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        averageUtilization: 70
```

#### 4. Load Balancing
- Nginx upstream configuration
- Kubernetes Service load balancing
- Health checks for automatic failover

### Monitoring

#### Metrics to Monitor
- **Application**: Request rate, response time, error rate
- **Database**: Connection pool usage, query performance, deadlocks
- **System**: CPU, memory, disk I/O, network
- **Business**: Active users, projects created, API usage

#### Tools
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **Sentry**: Error tracking
- **ELK Stack**: Log aggregation and analysis

---

## Support

### Enterprise Support
- **24/7 Support**: Phone, email, chat
- **Dedicated Account Manager**: Personalized assistance
- **SLA**: 99.9% uptime guarantee
- **Priority Bug Fixes**: Critical issues resolved within 4 hours
- **Training**: Onboarding and ongoing training for your team

### Documentation
- **API Reference**: https://docs.resoftai.com/api
- **User Guide**: https://docs.resoftai.com/guide
- **Plugin Development**: https://docs.resoftai.com/plugins
- **Video Tutorials**: https://www.youtube.com/resoftai

### Community
- **GitHub**: https://github.com/yourorg/resoftai-cli
- **Discord**: https://discord.gg/resoftai
- **Forum**: https://forum.resoftai.com
- **Stack Overflow**: Tag `resoftai`

---

## License

ResoftAI Enterprise Edition requires a valid enterprise license. Contact sales@resoftai.com for pricing and licensing information.
