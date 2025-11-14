#!/bin/bash

# Performance Testing Runner Script for ResoftAI
# This script runs various performance test scenarios

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
HOST="${API_HOST:-http://localhost:8000}"
REPORT_DIR="tests/performance/reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create report directory
mkdir -p "$REPORT_DIR"

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if backend is running
check_backend() {
    print_info "Checking if backend is accessible at $HOST..."

    if curl -sf "${HOST}/health" > /dev/null; then
        print_success "Backend is running and accessible"
        return 0
    else
        print_error "Backend is not accessible at $HOST"
        print_info "Please start the backend server first"
        return 1
    fi
}

# Function to check dependencies
check_dependencies() {
    print_info "Checking dependencies..."

    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi

    # Check if locust is installed
    if ! python3 -c "import locust" 2>/dev/null; then
        print_warning "Locust is not installed"
        print_info "Installing locust..."
        pip install locust python-socketio[asyncio_client]
    fi

    print_success "All dependencies are satisfied"
}

# Function to run smoke test
run_smoke_test() {
    print_info "Running smoke test (1 user, 1 minute)..."

    locust -f tests/performance/locustfile.py \
        --host="$HOST" \
        --users=1 \
        --spawn-rate=1 \
        --run-time=1m \
        --headless \
        --html="$REPORT_DIR/smoke_test_${TIMESTAMP}.html" \
        --csv="$REPORT_DIR/smoke_test_${TIMESTAMP}"

    print_success "Smoke test completed"
}

# Function to run baseline test
run_baseline_test() {
    print_info "Running baseline test (10 users, 5 minutes)..."

    locust -f tests/performance/locustfile.py \
        --host="$HOST" \
        --users=10 \
        --spawn-rate=2 \
        --run-time=5m \
        --headless \
        --html="$REPORT_DIR/baseline_test_${TIMESTAMP}.html" \
        --csv="$REPORT_DIR/baseline_test_${TIMESTAMP}"

    print_success "Baseline test completed"
}

# Function to run stress test
run_stress_test() {
    print_info "Running stress test (100 users, 15 minutes)..."

    locust -f tests/performance/locustfile.py \
        --host="$HOST" \
        --users=100 \
        --spawn-rate=10 \
        --run-time=15m \
        --headless \
        --html="$REPORT_DIR/stress_test_${TIMESTAMP}.html" \
        --csv="$REPORT_DIR/stress_test_${TIMESTAMP}"

    print_success "Stress test completed"
}

# Function to run spike test
run_spike_test() {
    print_info "Running spike test (0->200 users in 4 seconds)..."

    locust -f tests/performance/locustfile.py \
        --host="$HOST" \
        --users=200 \
        --spawn-rate=50 \
        --run-time=5m \
        --headless \
        --html="$REPORT_DIR/spike_test_${TIMESTAMP}.html" \
        --csv="$REPORT_DIR/spike_test_${TIMESTAMP}"

    print_success "Spike test completed"
}

# Function to run endurance test
run_endurance_test() {
    print_info "Running endurance test (50 users, 60 minutes)..."

    locust -f tests/performance/locustfile.py \
        --host="$HOST" \
        --users=50 \
        --spawn-rate=5 \
        --run-time=60m \
        --headless \
        --html="$REPORT_DIR/endurance_test_${TIMESTAMP}.html" \
        --csv="$REPORT_DIR/endurance_test_${TIMESTAMP}"

    print_success "Endurance test completed"
}

# Function to run custom test
run_custom_test() {
    local users=${1:-10}
    local spawn_rate=${2:-2}
    local duration=${3:-5m}

    print_info "Running custom test ($users users, spawn rate $spawn_rate, duration $duration)..."

    locust -f tests/performance/locustfile.py \
        --host="$HOST" \
        --users="$users" \
        --spawn-rate="$spawn_rate" \
        --run-time="$duration" \
        --headless \
        --html="$REPORT_DIR/custom_test_${TIMESTAMP}.html" \
        --csv="$REPORT_DIR/custom_test_${TIMESTAMP}"

    print_success "Custom test completed"
}

# Function to run WebSocket test
run_websocket_test() {
    local connections=${1:-100}
    local duration=${2:-60}

    print_info "Running WebSocket test ($connections connections, $duration seconds)..."

    python3 tests/performance/websocket_test.py \
        --url="$HOST" \
        --connections="$connections" \
        --duration="$duration"

    print_success "WebSocket test completed"
}

# Function to run interactive mode
run_interactive() {
    print_info "Starting Locust in interactive mode..."
    print_info "Web UI will be available at http://localhost:8089"

    locust -f tests/performance/locustfile.py --host="$HOST"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  smoke         - Quick smoke test (1 user, 1 minute)"
    echo "  baseline      - Baseline test (10 users, 5 minutes)"
    echo "  stress        - Stress test (100 users, 15 minutes)"
    echo "  spike         - Spike test (200 users, 5 minutes)"
    echo "  endurance     - Endurance test (50 users, 60 minutes)"
    echo "  websocket     - WebSocket load test"
    echo "  custom        - Custom test (provide users, spawn_rate, duration)"
    echo "  interactive   - Start Locust web UI"
    echo "  all           - Run all test scenarios"
    echo "  help          - Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  API_HOST      - Backend API URL (default: http://localhost:8000)"
    echo ""
    echo "Examples:"
    echo "  $0 smoke                     # Run smoke test"
    echo "  $0 baseline                  # Run baseline test"
    echo "  $0 custom 50 5 10m           # Run custom test with 50 users"
    echo "  $0 websocket 200 120         # Run WebSocket test with 200 connections"
    echo "  API_HOST=http://prod.example.com $0 baseline"
    echo ""
}

# Main script
main() {
    echo "======================================================================"
    echo "  ResoftAI Performance Testing Suite"
    echo "======================================================================"
    echo ""

    # Check dependencies
    check_dependencies

    # Check if backend is running
    if ! check_backend; then
        exit 1
    fi

    echo ""
    echo "Configuration:"
    echo "  - Target: $HOST"
    echo "  - Report Directory: $REPORT_DIR"
    echo "  - Timestamp: $TIMESTAMP"
    echo ""

    # Parse command
    case "${1:-help}" in
        smoke)
            run_smoke_test
            ;;
        baseline)
            run_baseline_test
            ;;
        stress)
            run_stress_test
            ;;
        spike)
            run_spike_test
            ;;
        endurance)
            run_endurance_test
            ;;
        websocket)
            run_websocket_test "${2:-100}" "${3:-60}"
            ;;
        custom)
            run_custom_test "$2" "$3" "$4"
            ;;
        interactive)
            run_interactive
            ;;
        all)
            print_info "Running all test scenarios..."
            run_smoke_test
            sleep 5
            run_baseline_test
            sleep 5
            run_stress_test
            sleep 5
            run_websocket_test
            print_success "All tests completed!"
            ;;
        help|--help|-h)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_usage
            exit 1
            ;;
    esac

    echo ""
    echo "======================================================================"
    print_success "Performance testing completed!"
    echo "======================================================================"
    echo ""
    echo "📊 Reports are available in: $REPORT_DIR"
    echo ""
    echo "View HTML report:"
    echo "  open $REPORT_DIR/*_${TIMESTAMP}.html"
    echo ""
}

# Run main function
main "$@"
