#!/bin/bash
# ============================================================================
# ResoftAI Production Deployment Script
# ============================================================================
#
# This script automates the complete deployment of ResoftAI to production.
#
# Usage:
#   sudo bash scripts/deploy_production.sh [domain]
#
# Example:
#   sudo bash scripts/deploy_production.sh resoftai.example.com
#
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
DOMAIN=${1:-""}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_USER="resoftai"
APP_DIR="/opt/resoftai"
VENV_DIR="$APP_DIR/venv"
UPLOAD_DIR="/opt/resoftai/uploads"
LOG_DIR="/var/log/resoftai"
BACKUP_DIR="/var/backups/resoftai"
WEB_ROOT="/var/www/resoftai"

# ============================================================================
# Helper Functions
# ============================================================================

log_header() {
    echo ""
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${MAGENTA}  $1${NC}"
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

confirm_deployment() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  ResoftAI Production Deployment"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "This script will:"
    echo "  • Install system dependencies"
    echo "  • Create application user and directories"
    echo "  • Deploy application code"
    echo "  • Setup PostgreSQL database"
    echo "  • Configure systemd service"
    echo "  • Setup Nginx reverse proxy"
    if [ -n "$DOMAIN" ]; then
        echo "  • Obtain SSL certificate for $DOMAIN"
    fi
    echo "  • Build and deploy frontend"
    echo "  • Configure monitoring and logging"
    echo ""
    echo -e "${YELLOW}Target Environment: PRODUCTION${NC}"
    echo ""
    read -p "Do you want to continue? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log_info "Deployment cancelled"
        exit 0
    fi
}

# ============================================================================
# System Preparation
# ============================================================================

update_system() {
    log_header "1. System Update"

    log_info "Updating package lists..."
    apt update -qq

    log_info "Upgrading system packages..."
    DEBIAN_FRONTEND=noninteractive apt upgrade -y -qq

    log_success "System updated"
}

install_dependencies() {
    log_header "2. Installing Dependencies"

    log_info "Installing system packages..."

    apt install -y -qq \
        python3.11 \
        python3.11-venv \
        python3-pip \
        postgresql-14 \
        postgresql-contrib \
        redis-server \
        nginx \
        git \
        curl \
        wget \
        build-essential \
        libpq-dev \
        python3-dev \
        supervisor \
        ufw \
        fail2ban \
        logrotate \
        htop \
        iotop \
        net-tools

    log_success "System dependencies installed"

    # Install Node.js 20.x
    log_info "Installing Node.js 20.x..."
    if ! command -v node &> /dev/null; then
        curl -fsSL https://deb.nodesource.com/setup_20.x | bash - > /dev/null 2>&1
        apt install -y -qq nodejs
    fi

    log_success "Node.js $(node --version) installed"
}

# ============================================================================
# User and Directory Setup
# ============================================================================

create_app_user() {
    log_header "3. Creating Application User"

    if ! id "$APP_USER" &>/dev/null; then
        useradd -m -s /bin/bash "$APP_USER"
        usermod -aG www-data "$APP_USER"
        log_success "User $APP_USER created"
    else
        log_info "User $APP_USER already exists"
    fi
}

create_directories() {
    log_header "4. Creating Directories"

    mkdir -p "$APP_DIR"
    mkdir -p "$UPLOAD_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$WEB_ROOT"

    chown -R "$APP_USER:$APP_USER" "$APP_DIR"
    chown -R "$APP_USER:$APP_USER" "$UPLOAD_DIR"
    chown -R "$APP_USER:$APP_USER" "$LOG_DIR"
    chown -R "$APP_USER:$APP_USER" "$BACKUP_DIR"
    chown -R www-data:www-data "$WEB_ROOT"

    chmod 755 "$APP_DIR"
    chmod 755 "$UPLOAD_DIR"
    chmod 755 "$LOG_DIR"

    log_success "Directories created"
}

# ============================================================================
# Application Deployment
# ============================================================================

deploy_code() {
    log_header "5. Deploying Application Code"

    log_info "Copying source code to $APP_DIR..."

    # Copy project files
    rsync -a --exclude='.git' \
              --exclude='node_modules' \
              --exclude='__pycache__' \
              --exclude='*.pyc' \
              --exclude='.env' \
              --exclude='venv' \
              --exclude='dist' \
              --exclude='build' \
              "$PROJECT_ROOT/" "$APP_DIR/"

    chown -R "$APP_USER:$APP_USER" "$APP_DIR"

    log_success "Application code deployed"
}

setup_python_env() {
    log_header "6. Setting Up Python Environment"

    log_info "Creating virtual environment..."
    sudo -u "$APP_USER" python3.11 -m venv "$VENV_DIR"

    log_info "Installing Python packages..."
    sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install --upgrade pip -q
    sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt" -q
    sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install gunicorn uvicorn[standard] -q

    log_success "Python environment configured"
}

# ============================================================================
# Database Setup
# ============================================================================

setup_database() {
    log_header "7. Setting Up Database"

    if [ -f "$PROJECT_ROOT/scripts/setup_production_db.sh" ]; then
        bash "$PROJECT_ROOT/scripts/setup_production_db.sh"
        log_success "Database setup completed"
    else
        log_warning "Database setup script not found. Please run manually."
    fi
}

# ============================================================================
# Frontend Build
# ============================================================================

build_frontend() {
    log_header "8. Building Frontend"

    log_info "Installing frontend dependencies..."
    cd "$APP_DIR/frontend"
    sudo -u "$APP_USER" npm install --production -q

    log_info "Building production frontend..."
    sudo -u "$APP_USER" npm run build

    log_info "Deploying frontend to $WEB_ROOT..."
    rm -rf "$WEB_ROOT/*"
    cp -r "$APP_DIR/frontend/dist"/* "$WEB_ROOT/"
    chown -R www-data:www-data "$WEB_ROOT"

    log_success "Frontend built and deployed"
}

# ============================================================================
# System Services
# ============================================================================

create_systemd_service() {
    log_header "9. Configuring Systemd Service"

    cat > /etc/systemd/system/resoftai.service <<EOF
[Unit]
Description=ResoftAI Multi-Agent Platform
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=notify
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
Environment="PYTHONPATH=$APP_DIR/src"
EnvironmentFile=$APP_DIR/.env

ExecStart=$VENV_DIR/bin/gunicorn resoftai.api.main:asgi_app \\
    --worker-class uvicorn.workers.UvicornWorker \\
    --workers 4 \\
    --bind 127.0.0.1:8000 \\
    --access-logfile $LOG_DIR/access.log \\
    --error-logfile $LOG_DIR/error.log \\
    --log-level info \\
    --timeout 120 \\
    --max-requests 1000 \\
    --max-requests-jitter 50

Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_DIR $UPLOAD_DIR $LOG_DIR

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable resoftai
    log_success "Systemd service configured"
}

configure_nginx() {
    log_header "10. Configuring Nginx"

    if [ -n "$DOMAIN" ]; then
        bash "$PROJECT_ROOT/scripts/setup_ssl.sh" "$DOMAIN"
    else
        log_warning "No domain provided. Creating basic Nginx config without SSL."

        cat > /etc/nginx/sites-available/resoftai <<'EOF'
server {
    listen 80;
    server_name _;

    root /var/www/resoftai;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }

    client_max_body_size 100M;
}
EOF

        ln -sf /etc/nginx/sites-available/resoftai /etc/nginx/sites-enabled/
        rm -f /etc/nginx/sites-enabled/default
        nginx -t && systemctl reload nginx
    fi

    log_success "Nginx configured"
}

# ============================================================================
# Security Configuration
# ============================================================================

configure_firewall() {
    log_header "11. Configuring Firewall"

    ufw --force enable
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 'Nginx Full'

    log_success "Firewall configured"
}

configure_fail2ban() {
    log_header "12. Configuring Fail2Ban"

    cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[nginx-http-auth]
enabled = true

[nginx-noscript]
enabled = true

[nginx-badbots]
enabled = true

[nginx-noproxy]
enabled = true
EOF

    systemctl enable fail2ban
    systemctl restart fail2ban

    log_success "Fail2Ban configured"
}

# ============================================================================
# Logging and Monitoring
# ============================================================================

configure_logging() {
    log_header "13. Configuring Logging"

    cat > /etc/logrotate.d/resoftai <<EOF
$LOG_DIR/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 $APP_USER $APP_USER
    sharedscripts
    postrotate
        systemctl reload resoftai > /dev/null 2>&1 || true
    endscript
}
EOF

    log_success "Log rotation configured"
}

# ============================================================================
# Final Steps
# ============================================================================

start_services() {
    log_header "14. Starting Services"

    systemctl start postgresql
    systemctl start redis-server
    systemctl start resoftai
    systemctl start nginx

    sleep 3

    log_success "All services started"
}

verify_deployment() {
    log_header "15. Verifying Deployment"

    # Check services
    if systemctl is-active --quiet resoftai; then
        log_success "ResoftAI service is running"
    else
        log_error "ResoftAI service is not running"
    fi

    if systemctl is-active --quiet nginx; then
        log_success "Nginx is running"
    else
        log_error "Nginx is not running"
    fi

    if systemctl is-active --quiet postgresql; then
        log_success "PostgreSQL is running"
    else
        log_error "PostgreSQL is not running"
    fi

    if systemctl is-active --quiet redis-server; then
        log_success "Redis is running"
    else
        log_error "Redis is not running"
    fi

    # Check application endpoint
    sleep 2
    if curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        log_success "Application health check passed"
    else
        log_warning "Application health check failed (may need environment configuration)"
    fi
}

print_summary() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}  Deployment Complete!${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Application Details:"
    echo "  Installation Directory: $APP_DIR"
    echo "  Upload Directory: $UPLOAD_DIR"
    echo "  Log Directory: $LOG_DIR"
    echo "  Web Root: $WEB_ROOT"
    echo ""
    echo "Services:"
    echo "  Application: systemctl status resoftai"
    echo "  Nginx: systemctl status nginx"
    echo "  PostgreSQL: systemctl status postgresql"
    echo "  Redis: systemctl status redis-server"
    echo ""
    if [ -n "$DOMAIN" ]; then
        echo "Access URL: https://$DOMAIN"
    else
        echo "Access URL: http://$(hostname -I | awk '{print $1}')"
    fi
    echo ""
    echo "Database Credentials: $APP_DIR/.database_credentials"
    echo ""
    echo "Important Next Steps:"
    echo "  1. Review and update .env file in $APP_DIR"
    echo "  2. Change default admin password (admin/admin123)"
    echo "  3. Configure LLM API keys"
    echo "  4. Test all functionality"
    echo "  5. Set up monitoring and alerts"
    echo "  6. Configure backups"
    echo ""
    echo "Logs:"
    echo "  Application: tail -f $LOG_DIR/app.log"
    echo "  Access: tail -f $LOG_DIR/access.log"
    echo "  Error: tail -f $LOG_DIR/error.log"
    echo "  Nginx: tail -f /var/log/nginx/resoftai_access.log"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# ============================================================================
# Main Deployment Flow
# ============================================================================

main() {
    check_root
    confirm_deployment

    update_system
    install_dependencies
    create_app_user
    create_directories
    deploy_code
    setup_python_env
    setup_database
    build_frontend
    create_systemd_service
    configure_nginx
    configure_firewall
    configure_fail2ban
    configure_logging
    start_services
    verify_deployment
    print_summary

    echo ""
    log_success "Deployment successful! 🎉"
    echo ""
}

# Run deployment
main "$@"
