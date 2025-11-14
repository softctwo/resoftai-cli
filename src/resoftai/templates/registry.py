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
        create_microservice_template(),
        create_data_pipeline_template(),
        create_ml_project_template(),
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


def create_microservice_template() -> Template:
    """Create microservice architecture template."""
    return Template(
        id="microservice-architecture",
        name="Microservice Architecture",
        description="Microservices architecture with FastAPI, Docker, Kubernetes, and gRPC support",
        category=TemplateCategory.MICROSERVICE,
        version="1.0.0",
        variables=[
            TemplateVariable(
                name="project_name",
                description="Project name",
                required=True,
            ),
            TemplateVariable(
                name="description",
                description="Project description",
                default="A microservices project",
            ),
            TemplateVariable(
                name="author",
                description="Author name",
                default="Your Name",
            ),
            TemplateVariable(
                name="use_grpc",
                description="Include gRPC service communication",
                default="true",
                type="boolean",
            ),
            TemplateVariable(
                name="use_message_queue",
                description="Include message queue (RabbitMQ/Kafka)",
                default="true",
                type="boolean",
            ),
        ],
        directories=[
            "services/gateway",
            "services/auth",
            "services/user",
            "shared/proto",
            "shared/models",
            "k8s/deployments",
            "k8s/services",
            "k8s/configmaps",
            "docker",
            "tests",
        ],
        files=[
            TemplateFile(
                path="README.md",
                content="""# {{project_name}} - Microservices Architecture

{{description}}

## Architecture

This project follows a microservices architecture pattern:

- **API Gateway**: Entry point for all client requests
- **Auth Service**: Authentication and authorization
- **User Service**: User management
{% if use_grpc == "true" %}- **gRPC**: Inter-service communication
{% endif %}{% if use_message_queue == "true" %}- **Message Queue**: Asynchronous event handling
{% endif %}
## Services

### Gateway Service (Port 8000)
- Routes requests to appropriate services
- API aggregation
- Rate limiting

### Auth Service (Port 8001)
- JWT token generation
- User authentication
- Permission management

### User Service (Port 8002)
- User CRUD operations
- Profile management
- User data persistence

## Quick Start

```bash
# Start all services with Docker Compose
docker-compose up -d

# Check service health
curl http://localhost:8000/health

# Access API documentation
open http://localhost:8000/docs
```

## Development

```bash
# Install dependencies for a service
cd services/gateway
pip install -r requirements.txt

# Run service locally
uvicorn main:app --reload --port 8000
```

## Kubernetes Deployment

```bash
# Apply Kubernetes configurations
kubectl apply -f k8s/

# Check pods status
kubectl get pods

# Access services
kubectl port-forward svc/gateway 8000:80
```

## Testing

```bash
# Run all tests
pytest tests/

# Test specific service
pytest tests/test_auth_service.py
```

## Author

{{author}}
""",
            ),
            TemplateFile(
                path="docker-compose.yml",
                content="""version: '3.8'

services:
  gateway:
    build:
      context: ./services/gateway
      dockerfile: ../../docker/Dockerfile.service
    ports:
      - "8000:8000"
    environment:
      - SERVICE_NAME=gateway
      - AUTH_SERVICE_URL=http://auth:8001
      - USER_SERVICE_URL=http://user:8002
    depends_on:
      - auth
      - user
{% if use_message_queue == "true" %}      - rabbitmq
{% endif %}
  auth:
    build:
      context: ./services/auth
      dockerfile: ../../docker/Dockerfile.service
    ports:
      - "8001:8001"
    environment:
      - SERVICE_NAME=auth
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/auth_db
      - JWT_SECRET=your-secret-key-change-in-production
    depends_on:
      - postgres

  user:
    build:
      context: ./services/user
      dockerfile: ../../docker/Dockerfile.service
    ports:
      - "8002:8002"
    environment:
      - SERVICE_NAME=user
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/user_db
    depends_on:
      - postgres

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
{% if use_message_queue == "true" %}
  rabbitmq:
    image: rabbitmq:3-management-alpine
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      - RABBITMQ_DEFAULT_USER=guest
      - RABBITMQ_DEFAULT_PASS=guest
{% endif %}
volumes:
  postgres_data:
""",
            ),
            TemplateFile(
                path="services/gateway/main.py",
                content="""\"\"\"API Gateway Service.\"\"\"

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI(
    title="{{project_name}} - API Gateway",
    description="API Gateway for microservices",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8002")


@app.get("/")
async def root():
    return {
        "service": "gateway",
        "message": "{{project_name}} API Gateway",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    \"\"\"Health check endpoint.\"\"\"
    services_health = {}

    async with httpx.AsyncClient() as client:
        # Check auth service
        try:
            response = await client.get(f"{AUTH_SERVICE_URL}/health", timeout=2.0)
            services_health["auth"] = "healthy" if response.status_code == 200 else "unhealthy"
        except Exception:
            services_health["auth"] = "unavailable"

        # Check user service
        try:
            response = await client.get(f"{USER_SERVICE_URL}/health", timeout=2.0)
            services_health["user"] = "healthy" if response.status_code == 200 else "unhealthy"
        except Exception:
            services_health["user"] = "unavailable"

    return {
        "status": "healthy",
        "services": services_health
    }


@app.post("/api/auth/login")
async def login(credentials: dict):
    \"\"\"Proxy to auth service.\"\"\"
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/login", json=credentials)
        return response.json()


@app.get("/api/users/{user_id}")
async def get_user(user_id: int, token: str = None):
    \"\"\"Proxy to user service with auth.\"\"\"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SERVICE_URL}/users/{user_id}", headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
""",
            ),
            TemplateFile(
                path="services/gateway/requirements.txt",
                content="""fastapi>=0.104.0
uvicorn[standard]>=0.24.0
httpx>=0.25.0
pydantic>=2.0.0
""",
            ),
            TemplateFile(
                path="docker/Dockerfile.service",
                content="""FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
            ),
            TemplateFile(
                path="k8s/deployments/gateway-deployment.yaml",
                content="""apiVersion: apps/v1
kind: Deployment
metadata:
  name: gateway
spec:
  replicas: 2
  selector:
    matchLabels:
      app: gateway
  template:
    metadata:
      labels:
        app: gateway
    spec:
      containers:
      - name: gateway
        image: {{project_name|snake_case}}/gateway:latest
        ports:
        - containerPort: 8000
        env:
        - name: AUTH_SERVICE_URL
          value: http://auth:8001
        - name: USER_SERVICE_URL
          value: http://user:8002
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
""",
            ),
            TemplateFile(
                path="k8s/services/gateway-service.yaml",
                content="""apiVersion: v1
kind: Service
metadata:
  name: gateway
spec:
  selector:
    app: gateway
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
""",
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

# Docker
*.log

# Kubernetes
*.secret.yaml

# Environment
.env
.env.local

# IDE
.vscode/
.idea/

# Testing
.coverage
htmlcov/
.pytest_cache/
""",
            ),
        ],
        requirements={"python": ">=3.9", "docker": ">=20.0", "kubernetes": ">=1.20"},
        dependencies=[
            "fastapi",
            "uvicorn",
            "httpx",
            "pydantic",
        ],
        setup_commands=[
            "docker-compose up -d",
            "kubectl apply -f k8s/",
        ],
        tags=["python", "microservices", "fastapi", "docker", "kubernetes", "grpc"],
    )


def create_data_pipeline_template() -> Template:
    """Create data pipeline template with Apache Airflow."""
    return Template(
        id="data-pipeline-airflow",
        name="Data Pipeline with Airflow",
        description="Data pipeline project with Apache Airflow, Pandas, and data quality checks",
        category=TemplateCategory.DATA_PIPELINE,
        version="1.0.0",
        variables=[
            TemplateVariable(
                name="project_name",
                description="Project name",
                required=True,
            ),
            TemplateVariable(
                name="description",
                description="Project description",
                default="A data pipeline project",
            ),
            TemplateVariable(
                name="author",
                description="Author name",
                default="Your Name",
            ),
            TemplateVariable(
                name="use_spark",
                description="Include Apache Spark for big data processing",
                default="false",
                type="boolean",
            ),
            TemplateVariable(
                name="use_dbt",
                description="Include dbt for data transformations",
                default="true",
                type="boolean",
            ),
        ],
        directories=[
            "dags",
            "plugins",
            "data/raw",
            "data/processed",
            "data/staging",
            "sql",
            "scripts",
            "tests",
            "dbt/models",
            "dbt/tests",
        ],
        files=[
            TemplateFile(
                path="README.md",
                content="""# {{project_name}} - Data Pipeline

{{description}}

## Architecture

This data pipeline uses:

- **Apache Airflow**: Workflow orchestration
- **Pandas/Polars**: Data transformation
{% if use_spark == "true" %}- **Apache Spark**: Large-scale data processing
{% endif %}{% if use_dbt == "true" %}- **dbt**: SQL-based transformations
{% endif %}- **Great Expectations**: Data quality validation
- **PostgreSQL**: Metadata and results storage

## Pipeline Stages

1. **Extract**: Fetch data from various sources
2. **Transform**: Clean and process data
3. **Validate**: Data quality checks
4. **Load**: Store processed data

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize Airflow database
airflow db init

# Create admin user
airflow users create \\
    --username admin \\
    --firstname Admin \\
    --lastname User \\
    --role Admin \\
    --email admin@example.com \\
    --password admin

# Start Airflow webserver
airflow webserver --port 8080

# Start scheduler (in another terminal)
airflow scheduler
```

## DAGs

- `example_etl_dag.py`: Basic ETL workflow
- `data_quality_dag.py`: Data quality validation
{% if use_dbt == "true" %}- `dbt_transformation_dag.py`: dbt transformations
{% endif %}
## Development

```bash
# Test a DAG
airflow dags test example_etl_dag 2024-01-01

# List DAGs
airflow dags list

# Run a specific task
airflow tasks test example_etl_dag extract_task 2024-01-01
```

## Testing

```bash
pytest tests/
```

## Author

{{author}}
""",
            ),
            TemplateFile(
                path="requirements.txt",
                content="""apache-airflow==2.8.0
pandas>=2.0.0
polars>=0.20.0
{% if use_spark == "true" %}pyspark>=3.5.0
{% endif %}{% if use_dbt == "true" %}dbt-core>=1.7.0
dbt-postgres>=1.7.0
{% endif %}great-expectations>=0.18.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
pytest>=7.4.0
pytest-cov>=4.1.0
""",
            ),
            TemplateFile(
                path="dags/example_etl_dag.py",
                content="""\"\"\"
Example ETL DAG.
\"\"\"

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import pandas as pd
from pathlib import Path


default_args = {
    'owner': '{{author}}',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'example_etl_dag',
    default_args=default_args,
    description='Example ETL pipeline',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['etl', 'example'],
)


def extract_data(**context):
    \"\"\"Extract data from source.\"\"\"
    # Example: Extract data
    data = {
        'id': [1, 2, 3, 4, 5],
        'value': [10, 20, 30, 40, 50],
        'timestamp': pd.date_range('2024-01-01', periods=5, freq='D')
    }
    df = pd.DataFrame(data)

    # Save to staging
    output_path = Path('data/staging/extracted_data.csv')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Extracted {len(df)} rows")
    return str(output_path)


def transform_data(**context):
    \"\"\"Transform extracted data.\"\"\"
    # Read from staging
    ti = context['ti']
    input_path = ti.xcom_pull(task_ids='extract_task')
    df = pd.read_csv(input_path)

    # Transform
    df['value_doubled'] = df['value'] * 2
    df['processed_at'] = datetime.now()

    # Save to processed
    output_path = Path('data/processed/transformed_data.csv')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Transformed {len(df)} rows")
    return str(output_path)


def validate_data(**context):
    \"\"\"Validate data quality.\"\"\"
    ti = context['ti']
    input_path = ti.xcom_pull(task_ids='transform_task')
    df = pd.read_csv(input_path)

    # Basic validation
    assert not df.isnull().any().any(), "Found null values"
    assert len(df) > 0, "Empty dataset"
    assert df['value_doubled'].min() >= 0, "Invalid values detected"

    print(f"Validation passed for {len(df)} rows")


# Define tasks
extract_task = PythonOperator(
    task_id='extract_task',
    python_callable=extract_data,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_task',
    python_callable=transform_data,
    dag=dag,
)

validate_task = PythonOperator(
    task_id='validate_task',
    python_callable=validate_data,
    dag=dag,
)

# Set task dependencies
extract_task >> transform_task >> validate_task
""",
            ),
            TemplateFile(
                path="airflow.cfg",
                content="""[core]
dags_folder = ./dags
plugins_folder = ./plugins
executor = LocalExecutor

[webserver]
base_url = http://localhost:8080
web_server_port = 8080

[scheduler]
dag_dir_list_interval = 300

[database]
sql_alchemy_conn = postgresql+psycopg2://airflow:airflow@localhost:5432/airflow
""",
            ),
            TemplateFile(
                path="docker-compose.yml",
                content="""version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  airflow-webserver:
    image: apache/airflow:2.8.0
    command: webserver
    depends_on:
      - postgres
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
      AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
    volumes:
      - ./dags:/opt/airflow/dags
      - ./plugins:/opt/airflow/plugins
      - ./data:/opt/airflow/data
    ports:
      - "8080:8080"

  airflow-scheduler:
    image: apache/airflow:2.8.0
    command: scheduler
    depends_on:
      - postgres
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    volumes:
      - ./dags:/opt/airflow/dags
      - ./plugins:/opt/airflow/plugins
      - ./data:/opt/airflow/data

volumes:
  postgres_data:
""",
            ),
            TemplateFile(
                path=".gitignore",
                content="""# Python
__pycache__/
*.py[cod]
venv/
ENV/

# Airflow
airflow.db
airflow-webserver.pid
logs/
*.log

# Data
data/raw/*
!data/raw/.gitkeep
data/staging/*
!data/staging/.gitkeep
data/processed/*
!data/processed/.gitkeep

# dbt
{% if use_dbt == "true" %}dbt/target/
dbt/logs/
{% endif %}
# IDE
.vscode/
.idea/

# Testing
.pytest_cache/
.coverage
""",
            ),
            TemplateFile(path="data/raw/.gitkeep", content=""),
            TemplateFile(path="data/staging/.gitkeep", content=""),
            TemplateFile(path="data/processed/.gitkeep", content=""),
        ],
        requirements={"python": ">=3.9", "postgresql": ">=13"},
        dependencies=[
            "apache-airflow",
            "pandas",
            "great-expectations",
            "sqlalchemy",
        ],
        setup_commands=[
            "pip install -r requirements.txt",
            "airflow db init",
            "docker-compose up -d",
        ],
        tags=["python", "data-pipeline", "airflow", "etl", "data-engineering"],
    )


def create_ml_project_template() -> Template:
    """Create machine learning project template."""
    return Template(
        id="ml-project-template",
        name="Machine Learning Project",
        description="ML project with scikit-learn, PyTorch, MLflow, and experiment tracking",
        category=TemplateCategory.ML_PROJECT,
        version="1.0.0",
        variables=[
            TemplateVariable(
                name="project_name",
                description="Project name",
                required=True,
            ),
            TemplateVariable(
                name="description",
                description="Project description",
                default="A machine learning project",
            ),
            TemplateVariable(
                name="author",
                description="Author name",
                default="Your Name",
            ),
            TemplateVariable(
                name="ml_framework",
                description="Primary ML framework",
                default="scikit-learn",
                type="choice",
                choices=["scikit-learn", "pytorch", "tensorflow"],
            ),
            TemplateVariable(
                name="use_mlflow",
                description="Include MLflow for experiment tracking",
                default="true",
                type="boolean",
            ),
        ],
        directories=[
            "data/raw",
            "data/processed",
            "data/external",
            "models",
            "notebooks",
            "src/data",
            "src/features",
            "src/models",
            "src/evaluation",
            "tests",
            "mlruns",
            "reports/figures",
        ],
        files=[
            TemplateFile(
                path="README.md",
                content="""# {{project_name}} - ML Project

{{description}}

## Project Structure

```
├── data
│   ├── raw              # Original, immutable data
│   ├── processed        # Cleaned, processed data
│   └── external         # External data sources
├── models               # Trained models
├── notebooks            # Jupyter notebooks for exploration
├── src                  # Source code
│   ├── data            # Data loading and preprocessing
│   ├── features        # Feature engineering
│   ├── models          # Model training and prediction
│   └── evaluation      # Model evaluation
├── tests                # Unit tests
{% if use_mlflow == "true" %}├── mlruns               # MLflow experiment tracking
{% endif %}└── reports              # Analysis reports and figures
```

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

## Usage

### 1. Data Preparation

```bash
# Download and preprocess data
python src/data/make_dataset.py

# Generate features
python src/features/build_features.py
```

### 2. Model Training

```bash
# Train model
python src/models/train_model.py --config config/model_config.yaml
{% if use_mlflow == "true" %}
# View experiments
mlflow ui
{% endif %}```

### 3. Model Evaluation

```bash
# Evaluate model
python src/evaluation/evaluate_model.py --model models/best_model.pkl
```

### 4. Prediction

```bash
# Make predictions
python src/models/predict_model.py --input data/new_data.csv
```

## Development

```bash
# Run tests
pytest tests/

# Format code
black src/

# Type checking
mypy src/
```

## ML Framework

This project uses **{{ml_framework}}** as the primary framework.

## Author

{{author}}
""",
            ),
            TemplateFile(
                path="requirements.txt",
                content="""# Core ML
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
{% if ml_framework == "pytorch" %}torch>=2.0.0
torchvision>=0.15.0
{% elif ml_framework == "tensorflow" %}tensorflow>=2.15.0
{% endif %}
# Experiment tracking
{% if use_mlflow == "true" %}mlflow>=2.9.0
{% endif %}
# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.18.0

# Data processing
polars>=0.20.0

# Model interpretation
shap>=0.44.0

# Development
jupyter>=1.0.0
ipykernel>=6.27.0
pytest>=7.4.0
black>=23.12.0
mypy>=1.7.0

# Utilities
pyyaml>=6.0
python-dotenv>=1.0.0
tqdm>=4.66.0
""",
            ),
            TemplateFile(
                path="src/__init__.py",
                content='"""{{project_name}} - {{description}}"""\n\n__version__ = "0.1.0"\n',
            ),
            TemplateFile(
                path="src/data/make_dataset.py",
                content="""\"\"\"
Script to download and prepare raw data.
\"\"\"

import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_raw_data(data_path: Path) -> pd.DataFrame:
    \"\"\"Load raw data from source.\"\"\"
    logger.info(f"Loading data from {data_path}")
    # TODO: Implement data loading logic
    return pd.DataFrame()


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    \"\"\"Preprocess raw data.\"\"\"
    logger.info("Preprocessing data")
    # TODO: Implement preprocessing
    return df


def save_processed_data(df: pd.DataFrame, output_path: Path):
    \"\"\"Save processed data.\"\"\"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Saved processed data to {output_path}")


def main():
    \"\"\"Main execution function.\"\"\"
    # Paths
    raw_data_path = Path("data/raw/dataset.csv")
    processed_data_path = Path("data/processed/dataset_processed.csv")

    # Process data
    df = load_raw_data(raw_data_path)
    df = preprocess_data(df)
    save_processed_data(df, processed_data_path)

    logger.info("Data preparation complete!")


if __name__ == "__main__":
    main()
""",
            ),
            TemplateFile(
                path="src/models/train_model.py",
                content="""\"\"\"
Model training script.
\"\"\"

import pandas as pd
from pathlib import Path
{% if ml_framework == "scikit-learn" %}from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
{% elif ml_framework == "pytorch" %}import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
{% endif %}{% if use_mlflow == "true" %}import mlflow
import mlflow.sklearn
{% endif %}import joblib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_data(data_path: Path) -> tuple:
    \"\"\"Load processed data.\"\"\"
    logger.info(f"Loading data from {data_path}")
    df = pd.read_csv(data_path)

    # TODO: Adjust based on your data
    X = df.drop('target', axis=1)
    y = df['target']

    return X, y


def train_model(X, y):
    \"\"\"Train the model.\"\"\"
{% if ml_framework == "scikit-learn" %}    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train model
    logger.info("Training model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)

    logger.info(f"Train score: {train_score:.4f}")
    logger.info(f"Test score: {test_score:.4f}")

    return model, train_score, test_score
{% else %}    # TODO: Implement training for {{ml_framework}}
    logger.info("Training model with {{ml_framework}}...")
    return None, 0.0, 0.0
{% endif %}

def main():
    \"\"\"Main execution function.\"\"\"
{% if use_mlflow == "true" %}    # Start MLflow run
    with mlflow.start_run():
{% endif %}        # Load data
        X, y = load_data(Path("data/processed/dataset_processed.csv"))

        # Train model
        model, train_score, test_score = train_model(X, y)

{% if use_mlflow == "true" %}        # Log to MLflow
        mlflow.log_param("n_samples", len(X))
        mlflow.log_metric("train_score", train_score)
        mlflow.log_metric("test_score", test_score)
        mlflow.sklearn.log_model(model, "model")
{% endif %}
        # Save model
        model_path = Path("models/model.pkl")
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, model_path)
        logger.info(f"Model saved to {model_path}")


if __name__ == "__main__":
    main()
""",
            ),
            TemplateFile(
                path="src/models/predict_model.py",
                content="""\"\"\"
Model prediction script.
\"\"\"

import pandas as pd
import joblib
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_model(model_path: Path):
    \"\"\"Load trained model.\"\"\"
    logger.info(f"Loading model from {model_path}")
    return joblib.load(model_path)


def predict(model, X):
    \"\"\"Make predictions.\"\"\"
    logger.info(f"Making predictions on {len(X)} samples")
    predictions = model.predict(X)
    return predictions


def main():
    \"\"\"Main execution function.\"\"\"
    # Load model
    model = load_model(Path("models/model.pkl"))

    # Load data
    X_new = pd.read_csv("data/new_data.csv")

    # Predict
    predictions = predict(model, X_new)

    # Save predictions
    output = pd.DataFrame({
        'predictions': predictions
    })
    output.to_csv("data/predictions.csv", index=False)
    logger.info("Predictions saved!")


if __name__ == "__main__":
    main()
""",
            ),
            TemplateFile(
                path="config/model_config.yaml",
                content="""# Model configuration
model:
  type: "{{ml_framework}}"
  parameters:
    random_state: 42

# Training
training:
  test_size: 0.2
  validation_size: 0.1
  batch_size: 32
  epochs: 10

# Data
data:
  features:
    - feature1
    - feature2
  target: target

# MLflow
{% if use_mlflow == "true" %}mlflow:
  experiment_name: "{{project_name}}"
  tracking_uri: "http://localhost:5000"
{% endif %}""",
            ),
            TemplateFile(
                path="notebooks/01_exploratory_analysis.ipynb",
                content="""{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Exploratory Data Analysis\\n",
    "\\n",
    "{{description}}"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\\n",
    "import numpy as np\\n",
    "import matplotlib.pyplot as plt\\n",
    "import seaborn as sns\\n",
    "\\n",
    "sns.set_style('whitegrid')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Load data\\n",
    "df = pd.read_csv('../data/processed/dataset_processed.csv')\\n",
    "df.head()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
""",
            ),
            TemplateFile(
                path="setup.py",
                content="""from setuptools import find_packages, setup

setup(
    name="{{project_name|snake_case}}",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "scikit-learn>=1.3.0",
    ],
    author="{{author}}",
    description="{{description}}",
    python_requires=">=3.9",
)
""",
            ),
            TemplateFile(
                path=".gitignore",
                content="""# Python
__pycache__/
*.py[cod]
*.so
.Python
venv/
ENV/
env/

# Jupyter
.ipynb_checkpoints
*.ipynb_checkpoints

# Data
data/raw/*
!data/raw/.gitkeep
data/processed/*
!data/processed/.gitkeep
data/external/*
!data/external/.gitkeep

# Models
models/*
!models/.gitkeep

# MLflow
{% if use_mlflow == "true" %}mlruns/
mlartifacts/
{% endif %}
# IDE
.vscode/
.idea/

# Testing
.pytest_cache/
.coverage
htmlcov/

# Reports
reports/figures/*
!reports/figures/.gitkeep
""",
            ),
            TemplateFile(path="data/raw/.gitkeep", content=""),
            TemplateFile(path="data/processed/.gitkeep", content=""),
            TemplateFile(path="data/external/.gitkeep", content=""),
            TemplateFile(path="models/.gitkeep", content=""),
            TemplateFile(path="reports/figures/.gitkeep", content=""),
        ],
        requirements={"python": ">=3.9"},
        dependencies=[
            "numpy",
            "pandas",
            "scikit-learn",
            "mlflow",
            "jupyter",
        ],
        setup_commands=[
            "python -m venv venv",
            "source venv/bin/activate",
            "pip install -r requirements.txt",
            "pip install -e .",
        ],
        tags=["python", "machine-learning", "ml", "data-science", "mlflow"],
    )
