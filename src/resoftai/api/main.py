"""FastAPI main application."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import socketio

from resoftai.config import Settings
from resoftai.db import init_db, close_db
from resoftai.api.routes import auth, projects, agent_activities, files, llm_configs, execution, templates, performance, monitoring, marketplace
from resoftai.websocket import sio

logger = logging.getLogger(__name__)
settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting ResoftAI API server...")
    await init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down ResoftAI API server...")
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI app with enhanced OpenAPI configuration
app = FastAPI(
    title="ResoftAI API",
    description="""
# ResoftAI Multi-Agent Software Development Platform API

ResoftAI is an enterprise-grade platform that leverages multiple AI agents to automate
and accelerate software development workflows.

## Features

### Core Platform
- **Multi-Agent Architecture**: 7 specialized agents (PM, Architect, Developer, QA, etc.)
- **Real-time Collaboration**: WebSocket-based live updates
- **Code Quality**: Automated linting, testing, and security scanning
- **Template System**: Pre-built project templates

### Enterprise Edition
- **Organizations & Teams**: Multi-tenant architecture with team collaboration
- **RBAC**: Fine-grained role-based access control
- **Quota Management**: Resource usage tracking and limits
- **Audit Logging**: Complete activity audit trail
- **SSO/SAML**: Enterprise authentication integration

### Plugin System
- **Extensibility**: Add custom agents, LLM providers, and tools
- **Marketplace**: Browse, install, and rate plugins
- **Community**: Share and discover plugins

## Authentication

Most endpoints require JWT authentication. Obtain a token via `/api/auth/login`:

```bash
curl -X POST http://localhost:8000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"username": "user", "password": "pass"}'
```

Include the token in subsequent requests:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \\
  http://localhost:8000/api/projects
```

## Rate Limiting

API requests are rate-limited based on your subscription tier:
- Free: 100 requests/minute
- Starter: 500 requests/minute
- Professional: 2000 requests/minute
- Enterprise: Custom limits

## Support

- Documentation: https://docs.resoftai.com
- GitHub: https://github.com/yourorg/resoftai-cli
- Discord: https://discord.gg/resoftai
""",
    version="0.2.0",
    lifespan=lifespan,
    contact={
        "name": "ResoftAI Support",
        "url": "https://resoftai.com/support",
        "email": "support@resoftai.com"
    },
    license_info={
        "name": "Enterprise License",
        "url": "https://resoftai.com/license"
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://staging.resoftai.com",
            "description": "Staging server"
        },
        {
            "url": "https://api.resoftai.com",
            "description": "Production server"
        }
    ],
    openapi_tags=[
        {
            "name": "auth",
            "description": "Authentication and user management"
        },
        {
            "name": "projects",
            "description": "Project creation and management"
        },
        {
            "name": "organizations",
            "description": "Organization management (Enterprise)"
        },
        {
            "name": "teams",
            "description": "Team collaboration (Enterprise)"
        },
        {
            "name": "plugins",
            "description": "Plugin marketplace and management"
        },
        {
            "name": "files",
            "description": "File versioning and management"
        },
        {
            "name": "execution",
            "description": "Project execution and monitoring"
        },
        {
            "name": "code_quality",
            "description": "Code quality analysis"
        },
        {
            "name": "templates",
            "description": "Project templates"
        },
        {
            "name": "monitoring",
            "description": "Performance monitoring and analytics"
        },
        {
            "name": "marketplace",
            "description": "Plugin marketplace - discover, install, and manage plugins"
        }
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(agent_activities.router, prefix="/api")
app.include_router(files.router, prefix="/api")
app.include_router(llm_configs.router, prefix="/api")
app.include_router(execution.router, prefix="/api")
app.include_router(templates.router, prefix="/api/v1")
app.include_router(performance.router, prefix="/api")
app.include_router(monitoring.router, prefix="/api")
app.include_router(marketplace.router, prefix="/api")

# Mount Socket.IO
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ResoftAI API",
        "version": "0.2.0",
        "docs": "/docs",
        "websocket": "/socket.io"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "resoftai-api"
    }


# Export the socket app as the main ASGI application
asgi_app = socket_app
