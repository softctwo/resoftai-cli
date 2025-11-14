#!/bin/bash

# Performance Optimization Setup Script
# This script sets up performance monitoring, caching, and load testing tools

set -e  # Exit on error

echo "=========================================="
echo "ResoftAI Performance Optimization Setup"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root (for system package installation)
if [ "$EUID" -ne 0 ] && command -v apt-get &> /dev/null; then
    echo -e "${YELLOW}Note: Some operations may require sudo privileges${NC}"
fi

# Step 1: Check Python version
echo "1. Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}Error: Python $REQUIRED_VERSION or higher is required${NC}"
    echo "Current version: $PYTHON_VERSION"
    exit 1
else
    echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"
fi

# Step 2: Install Redis (optional but recommended)
echo ""
echo "2. Checking Redis installation..."
if command -v redis-server &> /dev/null; then
    REDIS_VERSION=$(redis-server --version | grep -oP 'v=\K[0-9.]+')
    echo -e "${GREEN}✓ Redis $REDIS_VERSION is installed${NC}"

    # Check if Redis is running
    if systemctl is-active --quiet redis 2>/dev/null || pgrep redis-server > /dev/null; then
        echo -e "${GREEN}✓ Redis is running${NC}"
    else
        echo -e "${YELLOW}! Redis is not running${NC}"
        read -p "Do you want to start Redis? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if command -v systemctl &> /dev/null; then
                sudo systemctl start redis
                echo -e "${GREEN}✓ Redis started${NC}"
            else
                redis-server --daemonize yes
                echo -e "${GREEN}✓ Redis started in background${NC}"
            fi
        fi
    fi
else
    echo -e "${YELLOW}! Redis is not installed${NC}"
    read -p "Do you want to install Redis? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y redis-server
            sudo systemctl enable redis
            sudo systemctl start redis
            echo -e "${GREEN}✓ Redis installed and started${NC}"
        elif command -v brew &> /dev/null; then
            brew install redis
            brew services start redis
            echo -e "${GREEN}✓ Redis installed and started${NC}"
        else
            echo -e "${RED}Please install Redis manually${NC}"
            echo "Visit: https://redis.io/download"
        fi
    else
        echo -e "${YELLOW}Skipping Redis installation (caching will be disabled)${NC}"
    fi
fi

# Step 3: Install Python dependencies
echo ""
echo "3. Installing Python dependencies..."

# Install performance monitoring dependencies
if [ -f "requirements.txt" ]; then
    pip install -q redis>=5.0.0 || echo -e "${YELLOW}Warning: Failed to install redis${NC}"
    echo -e "${GREEN}✓ Performance monitoring dependencies installed${NC}"
else
    echo -e "${YELLOW}Warning: requirements.txt not found${NC}"
fi

# Install load testing dependencies
if [ -f "requirements-loadtest.txt" ]; then
    read -p "Install load testing tools (locust, etc.)? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install -q -r requirements-loadtest.txt
        echo -e "${GREEN}✓ Load testing dependencies installed${NC}"
    else
        echo "Skipping load testing dependencies"
    fi
else
    echo -e "${YELLOW}Warning: requirements-loadtest.txt not found${NC}"
fi

# Step 4: Run database migrations
echo ""
echo "4. Checking database migrations..."
if [ -d "alembic" ]; then
    read -p "Run database migrations to add performance indexes? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        alembic upgrade head
        echo -e "${GREEN}✓ Database migrations applied${NC}"
    else
        echo "Skipping database migrations"
    fi
else
    echo -e "${YELLOW}Warning: alembic directory not found${NC}"
fi

# Step 5: Create .env file if it doesn't exist
echo ""
echo "5. Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}! .env file not found${NC}"
    read -p "Create .env from .env.example? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env file created${NC}"
        echo -e "${YELLOW}Please edit .env to configure your settings${NC}"

        # Generate JWT secret key
        if command -v openssl &> /dev/null; then
            JWT_SECRET=$(openssl rand -hex 32)
            sed -i "s/your-secret-key-change-in-production-please/$JWT_SECRET/" .env
            echo -e "${GREEN}✓ Generated JWT secret key${NC}"
        fi
    fi
else
    echo -e "${GREEN}✓ .env file exists${NC}"

    # Check if Redis URL is configured
    if ! grep -q "^REDIS_URL=" .env; then
        echo -e "${YELLOW}! Redis URL not configured in .env${NC}"
        read -p "Add default Redis URL to .env? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "REDIS_URL=redis://localhost:6379/0" >> .env
            echo -e "${GREEN}✓ Redis URL added to .env${NC}"
        fi
    fi
fi

# Step 6: Test Redis connection
echo ""
echo "6. Testing Redis connection..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Redis connection successful${NC}"
    else
        echo -e "${RED}✗ Redis connection failed${NC}"
        echo "Please check if Redis is running: systemctl status redis"
    fi
else
    echo -e "${YELLOW}redis-cli not found, skipping connection test${NC}"
fi

# Step 7: Create log directory
echo ""
echo "7. Creating log directory..."
LOG_DIR="/var/log/resoftai"
if [ -d "$LOG_DIR" ]; then
    echo -e "${GREEN}✓ Log directory exists: $LOG_DIR${NC}"
else
    read -p "Create log directory $LOG_DIR? (requires sudo) (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo mkdir -p "$LOG_DIR"
        sudo chown $USER:$USER "$LOG_DIR"
        echo -e "${GREEN}✓ Log directory created${NC}"
    else
        echo "Using default log location"
    fi
fi

# Step 8: Verify installation
echo ""
echo "=========================================="
echo "Verification"
echo "=========================================="

# Check Python packages
echo ""
echo "Installed Python packages:"
pip list | grep -E "(redis|locust|socketio|aiohttp)" || echo "No performance packages found"

# Display setup summary
echo ""
echo "=========================================="
echo "Setup Summary"
echo "=========================================="
echo ""

if command -v redis-server &> /dev/null && pgrep redis-server > /dev/null; then
    echo -e "${GREEN}✓ Redis: Installed and running${NC}"
elif command -v redis-server &> /dev/null; then
    echo -e "${YELLOW}⚠ Redis: Installed but not running${NC}"
else
    echo -e "${YELLOW}⚠ Redis: Not installed (caching disabled)${NC}"
fi

if [ -f ".env" ]; then
    echo -e "${GREEN}✓ Configuration: .env file exists${NC}"
else
    echo -e "${YELLOW}⚠ Configuration: .env file missing${NC}"
fi

if pip show locust > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Load Testing: Locust installed${NC}"
else
    echo -e "${YELLOW}⚠ Load Testing: Not installed${NC}"
fi

echo ""
echo "=========================================="
echo "Next Steps"
echo "=========================================="
echo ""
echo "1. Review and update .env configuration:"
echo "   vi .env"
echo ""
echo "2. Start the API server with performance monitoring:"
echo "   uvicorn src.resoftai.api.main:app --workers 4"
echo ""
echo "3. Monitor performance metrics:"
echo "   curl http://localhost:8000/api/performance/metrics"
echo ""
echo "4. Run load tests:"
echo "   python tests/load/websocket_load_test.py --users 50 --duration 60"
echo ""
echo "5. View performance documentation:"
echo "   cat docs/PERFORMANCE_OPTIMIZATION.md"
echo ""
echo -e "${GREEN}Setup completed!${NC}"
