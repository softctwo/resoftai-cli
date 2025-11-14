#!/bin/bash
# ============================================================================
# ResoftAI Production Database Setup Script
# ============================================================================
#
# This script sets up a production-ready PostgreSQL database for ResoftAI.
#
# Usage:
#   sudo bash scripts/setup_production_db.sh
#
# Requirements:
#   - PostgreSQL 14+ installed
#   - Root or sudo access
#
# ============================================================================

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DB_NAME=${DB_NAME:-"resoftai_prod"}
DB_USER=${DB_USER:-"resoftai_user"}
DB_PASSWORD=${DB_PASSWORD:-""}
DB_HOST=${DB_HOST:-"localhost"}
DB_PORT=${DB_PORT:-"5432"}

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# ============================================================================
# Helper Functions
# ============================================================================

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

check_postgres_installed() {
    if ! command -v psql &> /dev/null; then
        log_error "PostgreSQL is not installed. Please install PostgreSQL 14+ first."
        echo "Installation command: sudo apt install -y postgresql-14"
        exit 1
    fi
    log_success "PostgreSQL is installed"
}

check_postgres_running() {
    if ! sudo systemctl is-active --quiet postgresql; then
        log_warning "PostgreSQL is not running. Starting PostgreSQL..."
        sudo systemctl start postgresql
        sleep 2
    fi
    log_success "PostgreSQL is running"
}

generate_password() {
    if [ -z "$DB_PASSWORD" ]; then
        DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
        log_info "Generated secure password for database user"
    fi
}

create_database() {
    log_info "Creating database: $DB_NAME"

    sudo -u postgres psql <<EOF
-- Create database
DROP DATABASE IF EXISTS $DB_NAME;
CREATE DATABASE $DB_NAME
    WITH
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Add comment
COMMENT ON DATABASE $DB_NAME IS 'ResoftAI Production Database';
EOF

    log_success "Database created: $DB_NAME"
}

create_user() {
    log_info "Creating database user: $DB_USER"

    sudo -u postgres psql <<EOF
-- Drop user if exists
DROP USER IF EXISTS $DB_USER;

-- Create user with password
CREATE USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASSWORD';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Allow user to create databases (needed for testing)
ALTER USER $DB_USER CREATEDB;
EOF

    log_success "Database user created: $DB_USER"
}

configure_database_permissions() {
    log_info "Configuring database permissions..."

    sudo -u postgres psql -d $DB_NAME <<EOF
-- Grant schema permissions
GRANT ALL ON SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON TABLES TO $DB_USER;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON SEQUENCES TO $DB_USER;
EOF

    log_success "Database permissions configured"
}

install_extensions() {
    log_info "Installing PostgreSQL extensions..."

    sudo -u postgres psql -d $DB_NAME <<EOF
-- UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Password encryption functions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Full-text search
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Additional data types
CREATE EXTENSION IF NOT EXISTS "hstore";
EOF

    log_success "PostgreSQL extensions installed"
}

optimize_postgresql_config() {
    log_info "Optimizing PostgreSQL configuration for production..."

    PG_CONF="/etc/postgresql/$(ls /etc/postgresql | head -n 1)/main/postgresql.conf"

    if [ -f "$PG_CONF" ]; then
        log_info "PostgreSQL config file: $PG_CONF"

        # Backup original config
        sudo cp "$PG_CONF" "${PG_CONF}.backup.$(date +%Y%m%d_%H%M%S)"

        # Apply optimizations
        sudo tee -a "$PG_CONF" > /dev/null <<EOF

# ============================================================================
# ResoftAI Production Optimizations
# Added on $(date)
# ============================================================================

# Memory settings
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 128MB
work_mem = 8MB

# Write-ahead log
wal_buffers = 16MB
checkpoint_completion_target = 0.9
max_wal_size = 1GB
min_wal_size = 80MB

# Query planner
random_page_cost = 1.1
effective_io_concurrency = 200

# Logging
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 0
log_autovacuum_min_duration = 0
log_error_verbosity = default

# Connection settings
max_connections = 100
superuser_reserved_connections = 3

# Autovacuum
autovacuum = on
autovacuum_max_workers = 3
autovacuum_naptime = 10s

# ============================================================================
EOF

        log_success "PostgreSQL configuration optimized"
        log_warning "PostgreSQL restart required for changes to take effect"
    else
        log_warning "PostgreSQL config file not found. Skipping optimization."
    fi
}

configure_pg_hba() {
    log_info "Configuring PostgreSQL authentication..."

    PG_HBA="/etc/postgresql/$(ls /etc/postgresql | head -n 1)/main/pg_hba.conf"

    if [ -f "$PG_HBA" ]; then
        # Backup original config
        sudo cp "$PG_HBA" "${PG_HBA}.backup.$(date +%Y%m%d_%H%M%S)"

        # Add entry for ResoftAI user
        if ! sudo grep -q "$DB_USER" "$PG_HBA"; then
            echo "local   $DB_NAME   $DB_USER   scram-sha-256" | sudo tee -a "$PG_HBA" > /dev/null
            log_success "Added authentication entry for $DB_USER"
        else
            log_info "Authentication entry already exists"
        fi
    else
        log_warning "pg_hba.conf not found. Skipping authentication configuration."
    fi
}

run_migrations() {
    log_info "Running database migrations..."

    cd "$PROJECT_ROOT"

    # Set environment variables
    export PYTHONPATH="$PROJECT_ROOT/src"
    export DATABASE_URL="postgresql+asyncpg://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"

    # Run Alembic migrations
    if [ -f "alembic.ini" ]; then
        python3 -m alembic upgrade head
        log_success "Database migrations completed"
    else
        log_error "alembic.ini not found. Cannot run migrations."
        return 1
    fi
}

create_admin_user() {
    log_info "Creating admin user..."

    cd "$PROJECT_ROOT"

    export PYTHONPATH="$PROJECT_ROOT/src"
    export DATABASE_URL="postgresql+asyncpg://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"

    python3 <<EOF
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from resoftai.models.user import User
from resoftai.auth.password import hash_password

async def create_admin():
    engine = create_async_engine("$DATABASE_URL")
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # Check if admin exists
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.username == "admin"))
        admin = result.scalar_one_or_none()

        if not admin:
            admin = User(
                username="admin",
                email="admin@resoftai.com",
                password_hash=hash_password("admin123"),
                is_active=True,
                is_superuser=True
            )
            session.add(admin)
            await session.commit()
            print("✅ Admin user created (username: admin, password: admin123)")
            print("⚠️  IMPORTANT: Change the default password immediately!")
        else:
            print("ℹ️  Admin user already exists")

    await engine.dispose()

asyncio.run(create_admin())
EOF

    log_success "Admin user setup completed"
}

save_connection_info() {
    log_info "Saving database connection information..."

    CONNECTION_FILE="$PROJECT_ROOT/.database_credentials"

    cat > "$CONNECTION_FILE" <<EOF
# ResoftAI Production Database Credentials
# Created: $(date)
# ============================================================================

Database Name: $DB_NAME
Database User: $DB_USER
Database Password: $DB_PASSWORD
Database Host: $DB_HOST
Database Port: $DB_PORT

# Connection String:
DATABASE_URL=postgresql+asyncpg://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME

# PostgreSQL Command Line:
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME

# ============================================================================
# IMPORTANT: Keep this file secure and never commit it to version control!
# ============================================================================
EOF

    chmod 600 "$CONNECTION_FILE"

    log_success "Connection information saved to: $CONNECTION_FILE"
}

verify_connection() {
    log_info "Verifying database connection..."

    export PGPASSWORD="$DB_PASSWORD"

    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
        log_success "Database connection verified"
    else
        log_error "Failed to connect to database"
        return 1
    fi

    unset PGPASSWORD
}

print_summary() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}Database Setup Complete!${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Database Details:"
    echo "  Database Name: $DB_NAME"
    echo "  Database User: $DB_USER"
    echo "  Database Host: $DB_HOST"
    echo "  Database Port: $DB_PORT"
    echo ""
    echo "Connection String:"
    echo "  postgresql+asyncpg://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
    echo ""
    echo "Admin Credentials:"
    echo "  Username: admin"
    echo "  Password: admin123"
    echo -e "  ${YELLOW}⚠️  CHANGE THIS PASSWORD IMMEDIATELY!${NC}"
    echo ""
    echo "Next Steps:"
    echo "  1. Update .env file with database connection string"
    echo "  2. Restart PostgreSQL: sudo systemctl restart postgresql"
    echo "  3. Start ResoftAI application"
    echo "  4. Change admin password"
    echo ""
    echo "Connection Info Saved:"
    echo "  File: $PROJECT_ROOT/.database_credentials"
    echo "  ${YELLOW}Keep this file secure!${NC}"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# ============================================================================
# Main Script
# ============================================================================

main() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  ResoftAI Production Database Setup"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Preliminary checks
    check_postgres_installed
    check_postgres_running

    # Generate secure password if not provided
    generate_password

    # Database setup
    create_database
    create_user
    configure_database_permissions
    install_extensions

    # Configuration
    optimize_postgresql_config
    configure_pg_hba

    # Restart PostgreSQL to apply changes
    log_info "Restarting PostgreSQL..."
    sudo systemctl restart postgresql
    sleep 3
    log_success "PostgreSQL restarted"

    # Verify connection
    verify_connection

    # Run migrations
    if [ -d "$PROJECT_ROOT/alembic" ]; then
        run_migrations
    else
        log_warning "Alembic directory not found. Skipping migrations."
    fi

    # Create admin user
    if command -v python3 &> /dev/null; then
        create_admin_user
    else
        log_warning "Python3 not found. Skipping admin user creation."
    fi

    # Save connection information
    save_connection_info

    # Print summary
    print_summary
}

# Run main function
main "$@"
