#!/bin/bash

# ResoftAI Docker Deployment Script
# Usage: ./scripts/docker-start.sh [dev|prod|stop|restart|logs]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

# Function to check .env file
check_env_file() {
    if [ ! -f .env ]; then
        print_warn ".env file not found. Creating from .env.example..."
        if [ -f .env.example ]; then
            cp .env.example .env
            print_info ".env file created. Please edit it with your configuration."
            print_warn "Press Enter to continue or Ctrl+C to exit and edit .env first..."
            read
        else
            print_error ".env.example not found. Cannot create .env file."
            exit 1
        fi
    fi
}

# Function to start development environment
start_dev() {
    print_info "Starting ResoftAI in DEVELOPMENT mode..."
    check_env_file

    print_info "Building and starting services..."
    docker-compose up --build -d

    print_info "Waiting for services to be healthy..."
    sleep 10

    print_info "Services status:"
    docker-compose ps

    echo ""
    print_info "✅ Development environment is ready!"
    echo ""
    echo "  Frontend:  http://localhost:5173"
    echo "  Backend:   http://localhost:8000"
    echo "  API Docs:  http://localhost:8000/docs"
    echo ""
    print_info "To view logs: docker-compose logs -f"
    print_info "To stop:      docker-compose down"
}

# Function to start production environment
start_prod() {
    print_info "Starting ResoftAI in PRODUCTION mode..."
    check_env_file

    # Check if required env vars are set
    source .env
    if [ -z "$JWT_SECRET_KEY" ] || [ "$JWT_SECRET_KEY" == "your-secret-key-change-in-production" ]; then
        print_error "JWT_SECRET_KEY is not set or using default value!"
        print_error "Please set a secure JWT_SECRET_KEY in .env file"
        exit 1
    fi

    print_info "Building and starting services..."
    docker-compose -f docker-compose.prod.yml up --build -d

    print_info "Waiting for services to be healthy..."
    sleep 15

    print_info "Services status:"
    docker-compose -f docker-compose.prod.yml ps

    echo ""
    print_info "✅ Production environment is ready!"
    echo ""
    echo "  Application: http://localhost"
    echo ""
    print_info "To view logs: docker-compose -f docker-compose.prod.yml logs -f"
    print_info "To stop:      docker-compose -f docker-compose.prod.yml down"
}

# Function to stop services
stop_services() {
    print_info "Stopping services..."

    if docker-compose ps | grep -q "Up"; then
        docker-compose down
        print_info "Development services stopped"
    fi

    if docker-compose -f docker-compose.prod.yml ps 2>/dev/null | grep -q "Up"; then
        docker-compose -f docker-compose.prod.yml down
        print_info "Production services stopped"
    fi

    print_info "All services stopped"
}

# Function to restart services
restart_services() {
    print_info "Restarting services..."
    stop_services
    sleep 2

    if [ "$1" == "prod" ]; then
        start_prod
    else
        start_dev
    fi
}

# Function to show logs
show_logs() {
    MODE=${1:-dev}
    SERVICE=${2:-}

    if [ "$MODE" == "prod" ]; then
        if [ -n "$SERVICE" ]; then
            docker-compose -f docker-compose.prod.yml logs -f "$SERVICE"
        else
            docker-compose -f docker-compose.prod.yml logs -f
        fi
    else
        if [ -n "$SERVICE" ]; then
            docker-compose logs -f "$SERVICE"
        else
            docker-compose logs -f
        fi
    fi
}

# Function to show status
show_status() {
    print_info "Services status:"
    echo ""

    if docker-compose ps 2>/dev/null | grep -q "Up"; then
        echo "Development environment:"
        docker-compose ps
        echo ""
    fi

    if docker-compose -f docker-compose.prod.yml ps 2>/dev/null | grep -q "Up"; then
        echo "Production environment:"
        docker-compose -f docker-compose.prod.yml ps
        echo ""
    fi
}

# Function to clean up everything
cleanup() {
    print_warn "This will remove all containers, volumes, and images. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_info "Cleaning up..."
        docker-compose down -v --rmi all 2>/dev/null || true
        docker-compose -f docker-compose.prod.yml down -v --rmi all 2>/dev/null || true
        print_info "Cleanup complete"
    else
        print_info "Cleanup cancelled"
    fi
}

# Main script
main() {
    # Change to project root directory
    cd "$(dirname "$0")/.."

    check_docker

    case "${1:-dev}" in
        dev)
            start_dev
            ;;
        prod)
            start_prod
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services "${2:-dev}"
            ;;
        logs)
            show_logs "${2:-dev}" "${3:-}"
            ;;
        status)
            show_status
            ;;
        cleanup)
            cleanup
            ;;
        *)
            echo "Usage: $0 {dev|prod|stop|restart|logs|status|cleanup}"
            echo ""
            echo "Commands:"
            echo "  dev       - Start development environment (default)"
            echo "  prod      - Start production environment"
            echo "  stop      - Stop all services"
            echo "  restart   - Restart services (restart dev|prod)"
            echo "  logs      - Show logs (logs dev|prod [service])"
            echo "  status    - Show services status"
            echo "  cleanup   - Remove all containers, volumes, and images"
            echo ""
            echo "Examples:"
            echo "  $0 dev              # Start development mode"
            echo "  $0 prod             # Start production mode"
            echo "  $0 logs dev backend # Show backend logs in dev mode"
            echo "  $0 restart prod     # Restart production services"
            exit 1
            ;;
    esac
}

main "$@"
