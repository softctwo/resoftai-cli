# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ResoftAI is a multi-agent software development collaboration platform with 7 specialized AI agents that automate the complete software development lifecycle from requirements to delivery. The platform includes:

- **Core Platform**: 7 AI agents (Project Manager, Requirements Analyst, Architect, Designer, Developer, Test Engineer, QA Expert)
- **Enterprise Edition**: Organizations, teams, RBAC, quota management, audit logging, SSO/SAML
- **Plugin System**: Extensible hook-based architecture with marketplace
- **Web APIs**: 60+ FastAPI endpoints with OpenAPI documentation
- **Frontend**: Vue 3 admin interface with Monaco editor integration

Current version: **0.2.2 (Beta)** | Test coverage: **90%+**

## Essential Commands

### Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database (creates tables)
python scripts/init_db.py

# Run database migrations (updates schema)
PYTHONPATH=src alembic upgrade head

# Start backend (development mode with auto-reload)
PYTHONPATH=src uvicorn resoftai.api.main:asgi_app --reload --port 8000

# Start frontend (from frontend/ directory)
cd frontend && npm install && npm run dev
```

### Testing

```bash
# Run all tests with coverage
PYTHONPATH=src pytest tests/ -v --cov=src/resoftai --cov-report=html

# Run specific test file
PYTHONPATH=src pytest tests/test_llm_factory.py -v

# Run single test function
PYTHONPATH=src pytest tests/test_workflow.py::test_workflow_initialization -v

# Enterprise and plugin tests
PYTHONPATH=src pytest tests/enterprise/ -v
PYTHONPATH=src pytest tests/plugins/ -v
PYTHONPATH=src pytest tests/api/ -v

# Performance/load testing
locust -f tests/performance/locustfile.py
```

### Code Quality

```bash
# Format code
black src/ tests/ --line-length=100
isort src/ tests/

# Lint code
flake8 src/ tests/ --max-line-length=120
ruff check src/ tests/

# Type checking
mypy src/ --ignore-missing-imports

# Security scanning
bandit -r src/ -ll
```

### Database Migrations

```bash
# Create new migration (auto-detect model changes)
PYTHONPATH=src alembic revision --autogenerate -m "description"

# Apply migrations
PYTHONPATH=src alembic upgrade head

# Rollback one migration
PYTHONPATH=src alembic downgrade -1

# Show migration history
PYTHONPATH=src alembic history
```

### Docker

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f backend

# Rebuild after code changes
docker-compose up -d --build

# Stop services
docker-compose down
```

## Architecture Overview

### Core Design Pattern: Multi-Agent Orchestration

The system uses a **workflow orchestration pattern** where agents communicate via a **message bus** and share state through a **centralized state manager**.

```
User Request → Workflow Orchestrator → Agent 1 → Agent 2 → ... → Agent 7 → Deliverables
                        ↓
                  Message Bus (pub/sub)
                        ↓
                  State Manager (persistence)
```

### Key Architectural Components

#### 1. Agent System (`src/resoftai/agents/`, `src/resoftai/core/agent.py`)

**Base Agent Pattern**: All agents inherit from `Agent` base class with:
- `execute(context)`: Main execution method
- `validate_input()`: Input validation
- `generate_output()`: Output generation
- `llm`: Access to configured LLM provider

**Agent Communication**: Via `MessageBus` (`src/resoftai/core/message_bus.py`)
- Publish/subscribe pattern
- Event-driven communication
- Async message handling

**State Management**: Via `StateManager` (`src/resoftai/core/state.py`)
- Persistent state across workflow stages
- Version control for artifacts
- Rollback capabilities

#### 2. Workflow System (`src/resoftai/orchestration/`)

**7-Stage Pipeline**:
1. Requirements Analysis → SRS document
2. Architecture Design → System design, DB schema
3. UI/UX Design → Wireframes, mockups
4. Development → Source code with quality checks
5. Testing → Test cases, test results
6. QA Review → Quality assessment
7. Completion → Final deliverables

**Workflow Orchestrator** (`workflow.py`): Manages stage transitions, agent coordination, error handling

**Project Executor** (`executor.py`): Executes workflows, tracks progress, manages resources

#### 3. LLM Abstraction Layer (`src/resoftai/llm/`)

**Factory Pattern**: `LLMFactory` creates provider instances
**Supported Providers**: DeepSeek, Anthropic, Google Gemini, Moonshot, Zhipu, MiniMax

**Key Pattern**: All LLM providers implement `BaseLLMProvider` interface:
```python
async def generate(self, messages, **kwargs) -> str
async def stream_generate(self, messages, **kwargs) -> AsyncIterator[str]
```

#### 4. Database Layer

**Technology**: SQLAlchemy 2.0 (async) with Alembic migrations

**Primary Models** (`src/resoftai/models/`):
- `User`: Authentication and user management
- `Project`: Project metadata and lifecycle
- `File`: File storage with version history
- `LLMConfig`: LLM provider configurations
- `AgentActivity`: Agent execution tracking
- **Enterprise Models** (19 tables):
  - `Organization`, `Team`, `TeamMember`
  - `Role`, `Permission` (RBAC)
  - `Quota`, `QuotaUsage`
  - `AuditLog`, `SSOProvider`
- **Plugin Models** (8 tables):
  - `Plugin`, `PluginVersion`, `PluginInstallation`
  - `PluginReview`, `PluginCollection`

**CRUD Pattern**: Database operations in `src/resoftai/crud/` follow consistent pattern:
```python
async def create_X(db: AsyncSession, **kwargs) -> Model
async def get_X(db: AsyncSession, id: int) -> Optional[Model]
async def list_X(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Model]
async def update_X(db: AsyncSession, id: int, **kwargs) -> Model
async def delete_X(db: AsyncSession, id: int) -> bool
```

#### 5. Enterprise Features (`src/resoftai/models/enterprise.py`, `src/resoftai/crud/enterprise.py`)

**Multi-tenancy**: Organization-based data isolation
**RBAC**: Fine-grained permissions with custom roles
**Quota Management**: Resource limits and usage tracking
**Audit Logging**: Complete activity trail for compliance
**SSO/SAML**: Enterprise authentication integration

**Organization Tiers**: FREE, STARTER, PROFESSIONAL, ENTERPRISE
**Team Roles**: OWNER, ADMIN, MEMBER, VIEWER

#### 6. Plugin System (`src/resoftai/plugins/`)

**Hook-Based Architecture**: Event-driven extensibility

**Core Components**:
- `base.py`: Abstract plugin base classes
- `manager.py`: Plugin lifecycle management (load → activate → deactivate → unload)
- `hooks.py`: Event hook system (actions and filters with priority)

**Plugin Types**:
- `AgentPlugin`: Extend agent capabilities
- `LLMProviderPlugin`: Add LLM providers
- `CodeQualityPlugin`: Add code analysis tools
- `IntegrationPlugin`: Third-party integrations

**Plugin Lifecycle**:
```python
plugin.load(context)     # Initialize plugin
plugin.activate()        # Start plugin
plugin.deactivate()      # Stop plugin
plugin.unload()          # Cleanup resources
```

**Hook System Pattern**:
```python
# Register action hook
hook_manager.register_action("event_name", callback, priority=10)
hook_manager.do_action("event_name", *args, **kwargs)

# Register filter hook
hook_manager.register_filter("filter_name", transform_func, priority=10)
result = hook_manager.apply_filters("filter_name", value)
```

#### 7. API Layer (`src/resoftai/api/`)

**Technology**: FastAPI with async/await

**API Organization**:
- `main.py`: App initialization, middleware, OpenAPI config
- `routes/`: Modular route definitions
  - Core: `auth.py`, `projects.py`, `files.py`, `llm_configs.py`
  - Enterprise: `organizations.py`, `teams.py`
  - Features: `plugins.py`, `templates.py`, `code_analysis.py`

**Authentication**: JWT tokens via `src/resoftai/auth/`
- Access tokens (30min expiry)
- Refresh tokens (7 day expiry)
- Argon2 password hashing

**WebSocket**: Real-time updates via `src/resoftai/websocket/`
- Project execution progress
- Agent activity streams
- Template application status

## Important Patterns and Conventions

### Environment Configuration

**Required Variables**:
```bash
DATABASE_URL=sqlite+aiosqlite:///./resoftai.db  # or postgresql+asyncpg://...
JWT_SECRET_KEY=your-secret-key
DEEPSEEK_API_KEY=sk-...  # or ANTHROPIC_API_KEY
```

**Database Switching**: Platform automatically detects SQLite vs PostgreSQL from `DATABASE_URL` and configures connection pooling accordingly.

### Code Quality System

**Developer Agent Enhancement**: Includes automatic code quality checks supporting 9 languages (Python, JavaScript, TypeScript, Java, Go, Rust, C++, C#, PHP).

**Quality Checks**:
- Security vulnerabilities (SQL injection, XSS, hardcoded secrets)
- Best practices validation
- Naming conventions
- Code complexity metrics
- Automated scoring (0-100)

### Template System

**Location**: `src/resoftai/templates/`

**Built-in Templates**:
- FastAPI REST API
- React + FastAPI Web App
- Python CLI Tool

**Template Structure**: Jinja2 templates with variable substitution, metadata, and validation schema.

### Testing Strategy

**Test Organization**:
- `tests/`: Unit tests for core components
- `tests/enterprise/`: Enterprise feature tests
- `tests/plugins/`: Plugin system tests
- `tests/api/`: API endpoint tests
- `tests/performance/`: Load tests (Locust)

**Fixtures**: Defined in `conftest.py` files (database sessions, test users, tokens)

**Coverage Target**: 90%+ for enterprise features and plugin system

## Working with This Codebase

### Adding a New Agent

1. Create agent class in `src/resoftai/agents/new_agent.py` inheriting from `Agent`
2. Implement `execute(context)` method
3. Add agent to workflow in `src/resoftai/orchestration/workflow.py`
4. Register agent in workflow stages
5. Add tests in `tests/test_agents.py`

### Adding a New API Endpoint

1. Create/update route file in `src/resoftai/api/routes/`
2. Define Pydantic models for request/response
3. Implement async route handler with proper authentication
4. Add to router in `main.py`
5. Write tests in `tests/api/test_<route_name>.py`

### Creating a Database Migration

1. Modify models in `src/resoftai/models/`
2. Run: `PYTHONPATH=src alembic revision --autogenerate -m "description"`
3. Review generated migration in `alembic/versions/`
4. Test: `PYTHONPATH=src alembic upgrade head`
5. Commit migration file

### Adding a Plugin

1. Create plugin directory in `examples/plugins/<plugin-name>/`
2. Implement plugin class inheriting from appropriate base (e.g., `CodeQualityPlugin`)
3. Define metadata (name, version, category, dependencies)
4. Implement lifecycle methods (`load`, `activate`, `deactivate`, `unload`)
5. Create `plugin.json` manifest
6. Add tests in `tests/plugins/`

### Extending Enterprise Features

**Adding a new organization-scoped resource**:
1. Create model in `src/resoftai/models/enterprise.py` with `organization_id` FK
2. Add CRUD operations in `src/resoftai/crud/enterprise.py`
3. Create API routes in `src/resoftai/api/routes/`
4. Add permission checks
5. Create audit log entries for sensitive operations
6. Write comprehensive tests

## Key Files and Their Purposes

- `src/resoftai/api/main.py`: FastAPI app entry point, 60+ endpoints
- `src/resoftai/orchestration/workflow.py`: 7-stage workflow orchestration
- `src/resoftai/core/message_bus.py`: Agent communication infrastructure
- `src/resoftai/llm/factory.py`: LLM provider abstraction
- `src/resoftai/plugins/manager.py`: Plugin lifecycle management
- `src/resoftai/crud/enterprise.py`: Enterprise feature database operations
- `alembic/versions/002_add_enterprise_features.py`: Enterprise schema migration
- `docs/ENTERPRISE.md`: Complete enterprise features documentation
- `docs/TEST_COVERAGE_IMPROVEMENTS.md`: Testing strategy and coverage details

## Common Development Workflows

### Testing Changes to an Agent

```bash
# Make changes to agent
vim src/resoftai/agents/developer.py

# Run agent-specific tests
PYTHONPATH=src pytest tests/test_agents.py::test_developer_agent -v

# Run workflow integration test
PYTHONPATH=src pytest tests/test_workflow.py -v

# Test via API
PYTHONPATH=src uvicorn resoftai.api.main:asgi_app --reload --port 8000
# Then create project and start execution via API
```

### Testing Enterprise Features

```bash
# Run enterprise tests
PYTHONPATH=src pytest tests/enterprise/ -v

# Test specific feature
PYTHONPATH=src pytest tests/enterprise/test_organizations.py -v

# Test API endpoints
PYTHONPATH=src pytest tests/api/test_organizations.py -v
PYTHONPATH=src pytest tests/api/test_teams.py -v
```

### Debugging Database Issues

```bash
# Check current migration status
PYTHONPATH=src alembic current

# View migration history
PYTHONPATH=src alembic history --verbose

# Downgrade if needed
PYTHONPATH=src alembic downgrade -1

# Re-initialize database (WARNING: drops all data)
rm resoftai.db  # or drop PostgreSQL database
python scripts/init_db.py
PYTHONPATH=src alembic upgrade head
```

## Branch Strategy

- Development happens on feature branches prefixed with `claude/`
- Branch naming: `claude/<feature-description>-<session-id>`
- Always push to the designated branch in the instructions
- Create PRs to `main` branch when ready

## Important Notes

- **PYTHONPATH**: Always set `PYTHONPATH=src` when running Python commands directly
- **Async/Await**: Most database and LLM operations are async - use `await` and `async def`
- **Type Hints**: Codebase uses type hints extensively - maintain this pattern
- **Testing**: Write tests for all new features - aim for 90%+ coverage
- **Migrations**: Never modify existing migration files - create new ones
- **Environment Variables**: Never commit `.env` files or API keys
- **Database URLs**: Code auto-detects SQLite vs PostgreSQL from `DATABASE_URL` format
