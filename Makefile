.PHONY: help install dev test lint format clean docker-dev docker-down db-upgrade db-downgrade db-reset

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

## help: Show this help message
help:
	@echo "$(BLUE)ResoftAI Development Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""

##@ Installation & Setup

## install: Install all dependencies
install:
	@echo "$(GREEN)Installing Python dependencies...$(NC)"
	pip install -r requirements.txt
	@echo "$(GREEN)Installing development dependencies...$(NC)"
	pip install pytest pytest-asyncio pytest-cov pytest-mock black ruff mypy ipython ipdb debugpy
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

## setup: Initial project setup (create .env, database)
setup:
	@echo "$(GREEN)Setting up ResoftAI development environment...$(NC)"
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✓ Created .env file from .env.example$(NC)"; \
		echo "$(YELLOW)⚠ Please update .env with your actual configuration$(NC)"; \
	else \
		echo "$(YELLOW)⚠ .env already exists, skipping...$(NC)"; \
	fi
	@mkdir -p workspace logs
	@echo "$(GREEN)✓ Created workspace and logs directories$(NC)"
	@echo "$(GREEN)✓ Setup complete!$(NC)"

##@ Development

## dev: Start development server with hot reload
dev:
	@echo "$(GREEN)Starting development server...$(NC)"
	PYTHONPATH=src uvicorn resoftai.api.main:asgi_app --host 0.0.0.0 --port 8000 --reload --reload-dir src --log-level debug

## dev-cli: Start CLI in development mode
dev-cli:
	@echo "$(GREEN)Starting CLI in development mode...$(NC)"
	PYTHONPATH=src python -m resoftai.cli.main

## shell: Start IPython shell with app context
shell:
	@echo "$(GREEN)Starting IPython shell...$(NC)"
	PYTHONPATH=src ipython

##@ Testing

## test: Run all tests
test:
	@echo "$(GREEN)Running all tests...$(NC)"
	PYTHONPATH=src pytest tests/ -v

## test-unit: Run unit tests only
test-unit:
	@echo "$(GREEN)Running unit tests...$(NC)"
	PYTHONPATH=src pytest tests/ -v -m "not integration"

## test-integration: Run integration tests only
test-integration:
	@echo "$(GREEN)Running integration tests...$(NC)"
	PYTHONPATH=src pytest tests/ -v -m integration

## test-cov: Run tests with coverage report
test-cov:
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	PYTHONPATH=src pytest tests/ --cov=src/resoftai --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/index.html$(NC)"

## test-watch: Run tests in watch mode
test-watch:
	@echo "$(GREEN)Running tests in watch mode...$(NC)"
	PYTHONPATH=src pytest-watch tests/ -- -v

##@ Code Quality

## lint: Run all linters
lint: lint-ruff lint-mypy
	@echo "$(GREEN)✓ All linting checks passed!$(NC)"

## lint-ruff: Run ruff linter
lint-ruff:
	@echo "$(GREEN)Running ruff...$(NC)"
	ruff check src/ tests/

## lint-mypy: Run mypy type checker
lint-mypy:
	@echo "$(GREEN)Running mypy...$(NC)"
	PYTHONPATH=src mypy src/resoftai --ignore-missing-imports

## format: Format code with black and ruff
format:
	@echo "$(GREEN)Formatting code with black...$(NC)"
	black src/ tests/
	@echo "$(GREEN)Fixing with ruff...$(NC)"
	ruff check --fix src/ tests/
	@echo "$(GREEN)✓ Code formatted$(NC)"

## format-check: Check code formatting without making changes
format-check:
	@echo "$(GREEN)Checking code formatting...$(NC)"
	black --check src/ tests/
	ruff check src/ tests/

##@ Database

## db-upgrade: Run database migrations (upgrade to head)
db-upgrade:
	@echo "$(GREEN)Running database migrations...$(NC)"
	alembic upgrade head
	@echo "$(GREEN)✓ Database upgraded to latest version$(NC)"

## db-downgrade: Rollback last database migration
db-downgrade:
	@echo "$(YELLOW)Rolling back last migration...$(NC)"
	alembic downgrade -1
	@echo "$(GREEN)✓ Database downgraded$(NC)"

## db-reset: Reset database (downgrade all, then upgrade)
db-reset:
	@echo "$(RED)Resetting database (WARNING: This will delete all data!)$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		alembic downgrade base; \
		alembic upgrade head; \
		echo "$(GREEN)✓ Database reset complete$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

## db-revision: Create a new database migration
db-revision:
	@read -p "Migration message: " message; \
	alembic revision --autogenerate -m "$$message"
	@echo "$(GREEN)✓ Migration created$(NC)"

## db-shell: Connect to database via psql
db-shell:
	@echo "$(GREEN)Connecting to database...$(NC)"
	psql postgresql://postgres:postgres@localhost:5432/resoftai

##@ Docker

## docker-dev: Start development environment with Docker Compose
docker-dev:
	@echo "$(GREEN)Starting Docker development environment...$(NC)"
	docker-compose -f docker-compose.dev.yml up -d
	@echo "$(GREEN)✓ Development environment started$(NC)"
	@echo "$(BLUE)Services:$(NC)"
	@echo "  • Backend API: http://localhost:8000"
	@echo "  • API Docs: http://localhost:8000/docs"
	@echo "  • Adminer (DB UI): http://localhost:8080"
	@echo "  • PostgreSQL: localhost:5432"
	@echo "  • Redis: localhost:6379"

## docker-logs: View Docker logs
docker-logs:
	docker-compose -f docker-compose.dev.yml logs -f

## docker-down: Stop Docker development environment
docker-down:
	@echo "$(YELLOW)Stopping Docker development environment...$(NC)"
	docker-compose -f docker-compose.dev.yml down
	@echo "$(GREEN)✓ Environment stopped$(NC)"

## docker-rebuild: Rebuild Docker images
docker-rebuild:
	@echo "$(GREEN)Rebuilding Docker images...$(NC)"
	docker-compose -f docker-compose.dev.yml build --no-cache
	@echo "$(GREEN)✓ Images rebuilt$(NC)"

## docker-clean: Remove Docker containers, volumes, and images
docker-clean:
	@echo "$(RED)Cleaning Docker resources...$(NC)"
	docker-compose -f docker-compose.dev.yml down -v --rmi all
	@echo "$(GREEN)✓ Docker resources cleaned$(NC)"

##@ Cleaning

## clean: Clean all generated files
clean:
	@echo "$(GREEN)Cleaning generated files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage coverage.xml
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

## clean-all: Deep clean including workspace and logs
clean-all: clean
	@echo "$(RED)Deep cleaning (includes workspace and logs)...$(NC)"
	rm -rf workspace/* logs/*
	@echo "$(GREEN)✓ Deep cleanup complete$(NC)"

##@ Documentation

## docs-serve: Serve API documentation locally
docs-serve:
	@echo "$(GREEN)Starting API documentation server...$(NC)"
	@echo "$(BLUE)API Docs will be available at:$(NC)"
	@echo "  • Swagger UI: http://localhost:8000/docs"
	@echo "  • ReDoc: http://localhost:8000/redoc"
	@make dev

## docs-openapi: Generate OpenAPI spec JSON file
docs-openapi:
	@echo "$(GREEN)Generating OpenAPI specification...$(NC)"
	PYTHONPATH=src python -c "from resoftai.api.main import app; import json; print(json.dumps(app.openapi(), indent=2))" > openapi.json
	@echo "$(GREEN)✓ OpenAPI spec saved to openapi.json$(NC)"

##@ Utilities

## security-check: Run security checks
security-check:
	@echo "$(GREEN)Running security checks...$(NC)"
	pip install safety bandit
	safety check
	bandit -r src/

## requirements-update: Update requirements.txt from current environment
requirements-update:
	@echo "$(GREEN)Updating requirements.txt...$(NC)"
	pip freeze > requirements.txt
	@echo "$(GREEN)✓ requirements.txt updated$(NC)"

## version: Show version information
version:
	@echo "$(BLUE)ResoftAI Version Information:$(NC)"
	@python -c "import sys; print(f'Python: {sys.version}')"
	@pip show resoftai 2>/dev/null || echo "ResoftAI: Development mode"
	@echo ""
