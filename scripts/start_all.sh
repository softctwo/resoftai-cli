#!/bin/bash

# ResoftAI Complete Startup Script
# Starts both backend and frontend in separate terminal windows/tabs

set -e

echo "========================================="
echo "Starting ResoftAI Complete System"
echo "========================================="
echo

SCRIPT_DIR="$(dirname "$0")"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Make scripts executable
chmod +x "$SCRIPT_DIR/start_backend.sh"
chmod +x "$SCRIPT_DIR/start_frontend.sh"

# Check if tmux is available
if command -v tmux &> /dev/null; then
    echo "Starting services in tmux session..."
    echo "Use 'tmux attach -t resoftai' to view"
    echo "Use 'Ctrl+B then D' to detach"
    echo "Use 'tmux kill-session -t resoftai' to stop all services"
    echo

    # Create new tmux session
    tmux new-session -d -s resoftai -n backend

    # Start backend in first pane
    tmux send-keys -t resoftai:backend "$SCRIPT_DIR/start_backend.sh" C-m

    # Create new window for frontend
    tmux new-window -t resoftai -n frontend
    tmux send-keys -t resoftai:frontend "$SCRIPT_DIR/start_frontend.sh" C-m

    # Attach to the session
    tmux attach -t resoftai

elif command -v gnome-terminal &> /dev/null; then
    echo "Starting services in separate terminal tabs..."

    gnome-terminal \
        --tab --title="Backend" -- bash -c "$SCRIPT_DIR/start_backend.sh; exec bash" \
        --tab --title="Frontend" -- bash -c "sleep 3 && $SCRIPT_DIR/start_frontend.sh; exec bash"

elif command -v xterm &> /dev/null; then
    echo "Starting services in separate xterm windows..."

    xterm -title "ResoftAI Backend" -e "$SCRIPT_DIR/start_backend.sh" &
    sleep 3
    xterm -title "ResoftAI Frontend" -e "$SCRIPT_DIR/start_frontend.sh" &

else
    echo "No terminal multiplexer found (tmux, gnome-terminal, xterm)"
    echo "Please start backend and frontend manually:"
    echo
    echo "  Terminal 1: $SCRIPT_DIR/start_backend.sh"
    echo "  Terminal 2: $SCRIPT_DIR/start_frontend.sh"
    echo
    exit 1
fi
