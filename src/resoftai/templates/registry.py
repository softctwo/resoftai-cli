"""
Registry of built-in project templates.
"""

from resoftai.templates.base import (
    Template,
    TemplateVariable,
    TemplateFile,
    TemplateCategory
)


def get_builtin_templates() -> list[Template]:
    """Get list of all built-in templates."""
    return [
        create_rest_api_template(),
        create_web_app_template(),
        create_cli_tool_template(),
    ]


def create_rest_api_template() -> Template:
    """Create FastAPI REST API template."""
    return Template(
        id="fastapi-rest-api",
        name="FastAPI REST API",
        description="Modern REST API with FastAPI, SQLAlchemy, and JWT authentication",
        category=TemplateCategory.REST_API,
        author="ResoftAI",
        version="1.0.0",
        variables=[
            TemplateVariable(
                name="project_name",
                description="Project name (will be converted to package name)",
                required=True,
            ),
            TemplateVariable(
                name="description",
                description="Project description",
                default="A FastAPI REST API project",
            ),
            TemplateVariable(
                name="author",
                description="Author name",
                default="Your Name",
            ),
            TemplateVariable(
                name="python_version",
                description="Python version",
                default="3.11",
                choices=["3.8", "3.9", "3.10", "3.11", "3.12"],
                type="choice",
            ),
            TemplateVariable(
                name="use_database",
                description="Include database support (SQLAlchemy + Alembic)",
                default="true",
                type="boolean",
            ),
            TemplateVariable(
                name="use_auth",
                description="Include JWT authentication",
                default="true",
                type="boolean",
            ),
        ],
        directories=[
            "{{project_name|snake_case}}",
            "{{project_name|snake_case}}/api",
            "{{project_name|snake_case}}/models",
            "{{project_name|snake_case}}/crud",
            "{{project_name|snake_case}}/schemas",
            "tests",
            "alembic/versions",
        ],
        files=[
            TemplateFile(
                path="README.md",
                content="""# {{project_name}}

{{description}}

## Features

- FastAPI for REST API
{% if use_database == "true" %}- SQLAlchemy ORM with Alembic migrations
- PostgreSQL database support
{% endif %}{% if use_auth == "true" %}- JWT authentication
- User management
{% endif %}- Automatic OpenAPI documentation
- Docker support
- Pytest for testing

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

{% if use_database == "true" %}# Setup database
alembic upgrade head
{% endif %}
# Run development server
uvicorn {{project_name|snake_case}}.main:app --reload
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Author

{{author}}
""",
            ),
            TemplateFile(
                path="requirements.txt",
                content="""fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
{% if use_database == "true" %}sqlalchemy>=2.0.0
alembic>=1.12.0
asyncpg>=0.29.0
{% endif %}{% if use_auth == "true" %}python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
{% endif %}pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.25.0
""",
            ),
            TemplateFile(
                path="{{project_name|snake_case}}/__init__.py",
                content='"""{{project_name}} - {{description}}"""\n\n__version__ = "0.1.0"\n',
            ),
            TemplateFile(
                path="{{project_name|snake_case}}/main.py",
                content="""\"\"\"
Main FastAPI application.
\"\"\"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from {{project_name|snake_case}}.api import router

app = FastAPI(
    title="{{project_name}}",
    description="{{description}}",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Welcome to {{project_name}} API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
""",
            ),
            TemplateFile(
                path="{{project_name|snake_case}}/api/__init__.py",
                content="""\"\"\"
API routes.
\"\"\"

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def api_root():
    return {"message": "{{project_name}} API v1"}
""",
            ),
            TemplateFile(
                path="{{project_name|snake_case}}/config.py",
                content="""\"\"\"
Application configuration.
\"\"\"

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    \"\"\"Application settings.\"\"\"

    app_name: str = "{{project_name}}"
    debug: bool = True
{% if use_database == "true" %}
    database_url: str = "postgresql+asyncpg://user:password@localhost/{{project_name|snake_case}}"
{% endif %}{% if use_auth == "true" %}
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
{% endif %}
    class Config:
        env_file = ".env"


settings = Settings()
""",
            ),
            TemplateFile(
                path=".env.example",
                content="""# Application settings
DEBUG=true
{% if use_database == "true" %}
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/{{project_name|snake_case}}
{% endif %}{% if use_auth == "true" %}
# Authentication
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
{% endif %}""",
            ),
            TemplateFile(
                path=".gitignore",
                content="""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
env/
.venv

# Database
*.db
*.sqlite3

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.coverage
htmlcov/
.pytest_cache/

# Build
dist/
build/
*.egg-info/
""",
            ),
            TemplateFile(
                path="Dockerfile",
                content="""FROM python:{{python_version}}-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "{{project_name|snake_case}}.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
            ),
            TemplateFile(
                path="docker-compose.yml",
                content="""version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=true
{% if use_database == "true" %}      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/{{project_name|snake_case}}
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB={{project_name|snake_case}}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
{% endif %}""",
            ),
            TemplateFile(
                path="tests/__init__.py",
                content="",
            ),
            TemplateFile(
                path="tests/test_main.py",
                content="""\"\"\"
Tests for main application.
\"\"\"

import pytest
from fastapi.testclient import TestClient

from {{project_name|snake_case}}.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_api_root():
    response = client.get("/api/v1/")
    assert response.status_code == 200
""",
            ),
        ],
        requirements={"python": ">=3.8"},
        dependencies=[
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "alembic",
            "pytest",
        ],
        setup_commands=[
            "python -m venv venv",
            "source venv/bin/activate",
            "pip install -r requirements.txt",
            "cp .env.example .env",
        ],
        tags=["python", "fastapi", "rest-api", "backend", "async"],
    )


def create_web_app_template() -> Template:
    """Create React + FastAPI full-stack web app template."""
    return Template(
        id="react-fastapi-webapp",
        name="React + FastAPI Web App",
        description="Full-stack web application with React frontend and FastAPI backend",
        category=TemplateCategory.WEB_APP,
        variables=[
            TemplateVariable(name="project_name", description="Project name", required=True),
            TemplateVariable(name="description", description="Project description",
                           default="A full-stack web application"),
            TemplateVariable(name="author", description="Author name", default="Your Name"),
        ],
        directories=[
            "frontend/src/components",
            "frontend/src/pages",
            "frontend/src/services",
            "frontend/public",
            "backend/{{project_name|snake_case}}",
            "backend/tests",
        ],
        files=[
            TemplateFile(
                path="README.md",
                content="""# {{project_name}}

{{description}}

## Structure

- `frontend/` - React application
- `backend/` - FastAPI backend

## Quick Start

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (in another terminal)
cd frontend
npm install
npm start
```

## Author

{{author}}
""",
            ),
        ],
        tags=["python", "react", "fastapi", "full-stack", "web"],
    )


def create_cli_tool_template() -> Template:
    """Create CLI tool template with Click."""
    return Template(
        id="python-cli-tool",
        name="Python CLI Tool",
        description="Command-line tool with Click, rich output, and configuration support",
        category=TemplateCategory.CLI_TOOL,
        variables=[
            TemplateVariable(name="project_name", description="Project name", required=True),
            TemplateVariable(name="description", description="Project description",
                           default="A CLI tool"),
            TemplateVariable(name="author", description="Author name", default="Your Name"),
            TemplateVariable(name="command_name", description="Main command name",
                           default="cli"),
        ],
        directories=[
            "{{project_name|snake_case}}",
            "{{project_name|snake_case}}/commands",
            "tests",
        ],
        files=[
            TemplateFile(
                path="README.md",
                content="""# {{project_name}}

{{description}}

## Installation

```bash
pip install -e .
```

## Usage

```bash
{{command_name}} --help
```

## Author

{{author}}
""",
            ),
            TemplateFile(
                path="setup.py",
                content="""from setuptools import setup, find_packages

setup(
    name="{{project_name|snake_case}}",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "{{command_name}}={{project_name|snake_case}}.cli:cli",
        ],
    },
    author="{{author}}",
    description="{{description}}",
)
""",
            ),
            TemplateFile(
                path="{{project_name|snake_case}}/cli.py",
                content="""\"\"\"
Main CLI interface.
\"\"\"

import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    \"\"\"{{description}}\"\"\"
    pass


@cli.command()
@click.argument("name")
def hello(name):
    \"\"\"Say hello.\"\"\"
    console.print(f"[bold green]Hello, {name}![/bold green]")


if __name__ == "__main__":
    cli()
""",
            ),
        ],
        tags=["python", "cli", "click", "tool"],
    )
