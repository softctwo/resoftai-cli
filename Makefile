# ResoftAI Makefile

.PHONY: help install dev test build deploy clean

# Default target
help:
	@echo "ResoftAI Development Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make install          Install all dependencies"
	@echo "  make dev              Start development environment"
	@echo "  make dev-backend      Start backend development server"
	@echo "  make dev-frontend     Start frontend development server"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run all tests"
	@echo "  make test-backend     Run backend tests"
	@echo "  make test-frontend    Run frontend tests"
	@echo "  make lint             Run code linting"
	@echo ""
	@echo "Deployment:"
	@echo "  make build            Build Docker images"
	@echo "  make deploy-dev       Deploy to development environment"
	@echo "  make deploy-prod      Deploy to production environment"
	@echo "  make deploy-k8s       Deploy to Kubernetes"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean            Clean up temporary files"
	@echo "  make db-init          Initialize database"
	@echo "  make db-migrate       Run database migrations"

# Installation
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Development
dev: dev-backend dev-frontend

dev-backend:
	@echo "Starting backend development server..."
	python -m uvicorn src.resoftai.api.main:asgi_app --host 0.0.0.0 --port 8000 --reload

dev-frontend:
	@echo "Starting frontend development server..."
	cd frontend && npm run dev

dev-docker:
	@echo "Starting development environment with Docker..."
	docker-compose -f docker-compose.dev.yml up --build

# Testing
test: test-backend test-frontend

test-backend:
	@echo "Running backend tests..."
	pytest tests/ -v --cov=src --cov-report=html

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm test

lint:
	@echo "Running code linting..."
	black --check src/ tests/
	ruff check src/ tests/
	mypy src/
	cd frontend && npm run lint

# Building
build:
	@echo "Building Docker images..."
	docker build -f Dockerfile.backend -t resoftai-backend:latest .
	cd frontend && docker build -t resoftai-frontend:latest .

# Deployment
deploy-dev:
	@echo "Deploying to development environment..."
	./deploy.sh dev

deploy-prod:
	@echo "Deploying to production environment..."
	./deploy.sh prod

deploy-k8s:
	@echo "Deploying to Kubernetes..."
	./deploy-k8s.sh

# Database
db-init:
	@echo "Initializing database..."
	python -c "
import asyncio
from resoftai.db import init_db
from resoftai.models import Base
from sqlalchemy import create_engine

async def migrate():
    await init_db()
    print('Database initialized successfully')

asyncio.run(migrate())
"

db-migrate:
	@echo "Running database migrations..."
	alembic upgrade head

# Cleanup
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name "htmlcov" -delete
	find . -type f -name ".coverage" -delete
	cd frontend && npm run clean

# Development utilities
dev-setup: install db-init
	@echo "Development setup complete!"
	@echo "Run 'make dev' to start the development servers"