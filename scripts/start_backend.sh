#!/bin/bash

# ResoftAI Backend Startup Script

set -e

echo "========================================="
echo "Starting ResoftAI Backend"
echo "========================================="
echo

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and configure it:"
    echo "  cp .env.example .env"
    echo "  nano .env  # Edit configuration"
    exit 1
fi

# Check if PostgreSQL is running
echo "Checking PostgreSQL connection..."
if ! python3 -c "
import sys
sys.path.insert(0, 'src')
from resoftai.config import get_settings
settings = get_settings()
print(f'Database URL: {settings.database_url}')
" 2>/dev/null; then
    echo "Warning: Could not load settings. Continuing anyway..."
fi

# Check Python dependencies
echo "Checking Python dependencies..."
if ! python3 -c "import fastapi, sqlalchemy, asyncpg, uvicorn, socketio" 2>/dev/null; then
    echo "Error: Missing Python dependencies!"
    echo "Please install requirements:"
    echo "  pip install -r requirements.txt"
    exit 1
fi

echo "✓ Dependencies OK"
echo

# Ask if user wants to initialize database
read -p "Initialize/update database? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Initializing database..."
    python3 scripts/init_db.py
    echo
fi

# Start the server
echo "Starting FastAPI server..."
echo "API will be available at: http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo "WebSocket: http://localhost:8000/socket.io"
echo
echo "Press Ctrl+C to stop the server"
echo

# Start uvicorn
cd "$(dirname "$0")/.." || exit
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

uvicorn resoftai.api.main:asgi_app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info
