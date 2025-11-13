#!/bin/bash

# ResoftAI Frontend Startup Script

set -e

echo "========================================="
echo "Starting ResoftAI Frontend"
echo "========================================="
echo

cd "$(dirname "$0")/../frontend" || exit

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
    echo
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating frontend .env file..."
    cat > .env << EOF
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000/api

# WebSocket URL
VITE_SOCKET_URL=http://localhost:8000
EOF
    echo "✓ Created .env file"
    echo
fi

echo "Starting Vite development server..."
echo "Frontend will be available at: http://localhost:5173"
echo
echo "Press Ctrl+C to stop the server"
echo

npm run dev
