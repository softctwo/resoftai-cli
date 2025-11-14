#!/bin/bash
set -e

echo "Starting ResoftAI Backend..."

# Wait for database to be ready
if [ -n "$DATABASE_URL" ]; then
    echo "Waiting for database to be ready..."

    # Extract database host and port from DATABASE_URL
    # Format: postgresql://user:pass@host:port/db or sqlite:///path
    if [[ $DATABASE_URL == postgresql* ]]; then
        DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
        DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')

        echo "Checking PostgreSQL at $DB_HOST:$DB_PORT..."

        # Wait for PostgreSQL
        max_retries=30
        retry_count=0
        until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null || [ $retry_count -eq $max_retries ]; do
            retry_count=$((retry_count+1))
            echo "PostgreSQL is unavailable ($retry_count/$max_retries) - sleeping"
            sleep 2
        done

        if [ $retry_count -eq $max_retries ]; then
            echo "Failed to connect to PostgreSQL after $max_retries attempts"
            echo "Continuing anyway (database might be SQLite or will connect later)..."
        else
            echo "PostgreSQL is up - continuing"
        fi
    else
        echo "Using SQLite database"
    fi
fi

# Run database migrations (if needed)
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running database migrations..."
    alembic upgrade head || echo "Migration failed or not configured, continuing..."
fi

# Initialize database (if needed)
if [ "$INIT_DB" = "true" ]; then
    echo "Initializing database..."
    python scripts/init_db.py || echo "Database initialization failed or already initialized"
fi

echo "Starting application..."

# Execute the main command
exec "$@"
