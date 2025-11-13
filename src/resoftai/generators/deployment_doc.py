"""Deployment and installation guide generator."""

from resoftai.generators.base import DocumentGenerator


class DeploymentDocGenerator(DocumentGenerator):
    """Generates deployment and installation guide."""

    @property
    def document_name(self) -> str:
        return "Deployment and Installation Guide"

    @property
    def document_filename(self) -> str:
        return "deployment-guide.md"

    async def generate_content(self) -> str:
        """Generate deployment guide content."""
        content = self._get_project_summary()

        content += """## System Requirements

### Hardware Requirements
- CPU: Modern multi-core processor
- RAM: Minimum 4GB, Recommended 8GB+
- Storage: 10GB available space
- Network: Stable internet connection

### Software Requirements
- Operating System: Linux, macOS, or Windows
- Required software versions (to be specified based on tech stack)

## Installation Steps

### 1. Prerequisites

Install required dependencies as specified in the requirements documentation.

### 2. Download and Extract

Download the software package and extract to desired location.

### 3. Configuration

Configure the application settings:
- Database connection
- API keys and secrets
- Environment-specific settings

### 4. Database Setup

Initialize the database:
```bash
# Database migration commands
```

### 5. Start the Application

```bash
# Start command
```

## Deployment Options

### Option 1: Local Deployment

For development and testing purposes.

### Option 2: Cloud Deployment

Recommended for production use.

### Option 3: Container Deployment

Using Docker or similar containerization.

## Post-Deployment Verification

1. Verify all services are running
2. Check database connectivity
3. Test API endpoints
4. Verify user interface accessibility

## Troubleshooting

Common issues and solutions:

### Issue 1: Connection Errors
Solution: Check network settings and firewall rules

### Issue 2: Database Errors
Solution: Verify database credentials and connectivity

## Maintenance

### Backup Procedures
Regular backup recommendations

### Update Procedures
How to apply updates and patches

### Monitoring
Recommended monitoring practices

"""

        if "deployment_guide" in self.project_state.metadata:
            content += "\n## Additional Deployment Information\n\n"
            content += self.project_state.metadata["deployment_guide"]

        return content
