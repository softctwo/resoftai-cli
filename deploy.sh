#!/bin/bash

# ResoftAI Deployment Script
# Usage: ./deploy.sh [dev|prod]

set -e

ENVIRONMENT=${1:-dev}
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env.${ENVIRONMENT}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if environment file exists
if [[ ! -f "$ENV_FILE" ]]; then
    log_error "Environment file $ENV_FILE not found!"
    log_info "Available environment files:"
    ls -la .env* 2>/dev/null || echo "No environment files found"
    exit 1
fi

log_info "Deploying ResoftAI in $ENVIRONMENT environment..."

# Copy environment file
cp "$ENV_FILE" .env

# Build and start services
log_info "Building and starting services..."
docker-compose -f "$COMPOSE_FILE" down
docker-compose -f "$COMPOSE_FILE" build --no-cache
docker-compose -f "$COMPOSE_FILE" up -d

# Wait for services to be ready
log_info "Waiting for services to be ready..."
sleep 10

# Check if services are running
log_info "Checking service status..."
if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
    log_success "All services are running!"
else
    log_error "Some services failed to start. Check logs with: docker-compose logs"
    exit 1
fi

# Run database migrations
log_info "Running database migrations..."
docker-compose -f "$COMPOSE_FILE" exec backend python -c "
import asyncio
from resoftai.db import init_db
from resoftai.models import Base
from sqlalchemy import create_engine

async def migrate():
    await init_db()
    print('Database initialized successfully')

asyncio.run(migrate())
"

# Create admin user if not exists
log_info "Creating admin user..."
docker-compose -f "$COMPOSE_FILE" exec backend python -c "
import asyncio
from resoftai.db import init_db
from resoftai.crud.user import create_user, get_user_by_username

async def setup_admin():
    await init_db()
    from resoftai.db import get_db
    
    async for session in get_db():
        admin = await get_user_by_username(session, 'admin')
        if not admin:
            admin = await create_user(
                session,
                username='admin',
                email='admin@resoftai.com',
                password='admin123',
                role='admin'
            )
            print('Admin user created successfully')
        else:
            print('Admin user already exists')

asyncio.run(setup_admin())
"

# Display deployment information
log_success "ResoftAI deployment completed!"
log_info ""
log_info "Access URLs:"
log_info "  Frontend: http://localhost:80"
log_info "  Backend API: http://localhost:8000"
log_info "  API Documentation: http://localhost:8000/docs"
log_info ""
log_info "Default Admin Credentials:"
log_info "  Username: admin"
log_info "  Password: admin123"
log_info ""
log_info "Management Commands:"
log_info "  View logs: docker-compose logs -f"
log_info "  Stop services: docker-compose down"
log_info "  Restart services: docker-compose restart"
log_info ""
log_warning "IMPORTANT: Change default admin password after first login!"
log_warning "IMPORTANT: Update JWT_SECRET_KEY and LLM_API_KEY in .env.production!"

# Clean up temporary .env file
rm -f .env

log_success "Deployment script completed successfully!"