#!/bin/bash
# ============================================================================
# ResoftAI SSL Certificate Setup Script
# ============================================================================
#
# This script automates SSL certificate setup using Let's Encrypt.
#
# Usage:
#   sudo bash scripts/setup_ssl.sh yourdomain.com
#
# Requirements:
#   - Nginx installed and running
#   - Domain pointing to server
#   - Port 80 and 443 open
#
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DOMAIN=$1
EMAIL=${2:-"admin@$DOMAIN"}

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

check_domain() {
    if [ -z "$DOMAIN" ]; then
        log_error "Domain not provided"
        echo "Usage: sudo bash scripts/setup_ssl.sh yourdomain.com [email@example.com]"
        exit 1
    fi
    log_info "Domain: $DOMAIN"
    log_info "Email: $EMAIL"
}

check_nginx() {
    if ! command -v nginx &> /dev/null; then
        log_error "Nginx is not installed"
        echo "Install with: sudo apt install -y nginx"
        exit 1
    fi
    log_success "Nginx is installed"
}

install_certbot() {
    log_info "Installing Certbot..."

    if ! command -v certbot &> /dev/null; then
        sudo apt update
        sudo apt install -y certbot python3-certbot-nginx
        log_success "Certbot installed"
    else
        log_success "Certbot already installed"
    fi
}

create_nginx_config() {
    log_info "Creating Nginx configuration..."

    cat | sudo tee /etc/nginx/sites-available/resoftai > /dev/null <<EOF
# ResoftAI Nginx Configuration
# Domain: $DOMAIN
# Created: $(date)

# Rate limiting zones
limit_req_zone \$binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone \$binary_remote_addr zone=auth_limit:10m rate=5r/m;
limit_req_zone \$binary_remote_addr zone=upload_limit:10m rate=2r/s;

# Upstream backend
upstream resoftai_backend {
    server 127.0.0.1:8000 fail_timeout=0;
}

# HTTP server (redirect to HTTPS)
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN www.$DOMAIN;

    # Let's Encrypt verification
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL certificates (will be added by certbot)
    # ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/$DOMAIN/chain.pem;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;

    # Root directory for static files
    root /var/www/resoftai;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/x-font-ttf font/opentype image/svg+xml;

    # Brotli compression (if available)
    # brotli on;
    # brotli_comp_level 6;
    # brotli_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;

    # API endpoints
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;

        proxy_pass http://resoftai_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-Port \$server_port;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";

        # Buffering
        proxy_buffering off;
        proxy_request_buffering off;
    }

    # Auth endpoints with stricter rate limiting
    location /api/v1/auth/ {
        limit_req zone=auth_limit burst=5 nodelay;

        proxy_pass http://resoftai_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # File upload endpoint with rate limiting
    location /api/v1/files/ {
        limit_req zone=upload_limit burst=5 nodelay;

        proxy_pass http://resoftai_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # Larger timeouts for file uploads
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;

        # Disable buffering for uploads
        proxy_request_buffering off;
    }

    # WebSocket endpoint
    location /ws/ {
        proxy_pass http://resoftai_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # Long timeout for WebSocket connections
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }

    # Metrics endpoint (restrict access)
    location /metrics {
        # Allow only localhost
        allow 127.0.0.1;
        deny all;

        proxy_pass http://resoftai_backend;
        proxy_set_header Host \$host;
    }

    # Static files with caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot|map)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # API documentation (disable in production if not needed)
    location /docs {
        proxy_pass http://resoftai_backend;
        proxy_set_header Host \$host;

        # Optional: Restrict access
        # allow 10.0.0.0/8;  # Internal network
        # deny all;
    }

    location /redoc {
        proxy_pass http://resoftai_backend;
        proxy_set_header Host \$host;
    }

    # Frontend SPA routing
    location / {
        try_files \$uri \$uri/ /index.html;

        # Additional security headers for HTML
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' wss: https:;" always;
    }

    # Deny access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    # File upload size limit
    client_max_body_size 100M;
    client_body_buffer_size 128k;

    # Client timeout
    client_body_timeout 60s;
    client_header_timeout 60s;

    # Access and error logs
    access_log /var/log/nginx/resoftai_access.log combined;
    error_log /var/log/nginx/resoftai_error.log warn;
}
EOF

    log_success "Nginx configuration created"
}

enable_nginx_site() {
    log_info "Enabling Nginx site..."

    # Remove default site if exists
    if [ -L /etc/nginx/sites-enabled/default ]; then
        sudo rm /etc/nginx/sites-enabled/default
        log_info "Removed default site"
    fi

    # Enable ResoftAI site
    if [ ! -L /etc/nginx/sites-enabled/resoftai ]; then
        sudo ln -s /etc/nginx/sites-available/resoftai /etc/nginx/sites-enabled/
        log_success "ResoftAI site enabled"
    else
        log_info "ResoftAI site already enabled"
    fi

    # Test configuration
    if sudo nginx -t; then
        log_success "Nginx configuration is valid"
        sudo systemctl reload nginx
        log_success "Nginx reloaded"
    else
        log_error "Nginx configuration is invalid"
        exit 1
    fi
}

obtain_certificate() {
    log_info "Obtaining SSL certificate from Let's Encrypt..."

    sudo certbot --nginx \
        -d "$DOMAIN" \
        -d "www.$DOMAIN" \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        --redirect

    if [ $? -eq 0 ]; then
        log_success "SSL certificate obtained successfully"
    else
        log_error "Failed to obtain SSL certificate"
        exit 1
    fi
}

setup_auto_renewal() {
    log_info "Setting up automatic renewal..."

    # Test renewal
    if sudo certbot renew --dry-run; then
        log_success "Certificate renewal test passed"
    else
        log_warning "Certificate renewal test failed"
    fi

    # Certbot automatically sets up a systemd timer
    if sudo systemctl is-enabled --quiet certbot.timer; then
        log_success "Auto-renewal timer is active"
    else
        sudo systemctl enable certbot.timer
        sudo systemctl start certbot.timer
        log_success "Auto-renewal timer enabled"
    fi
}

configure_firewall() {
    log_info "Configuring firewall..."

    if command -v ufw &> /dev/null; then
        sudo ufw allow 'Nginx Full'
        sudo ufw delete allow 'Nginx HTTP' 2>/dev/null || true
        log_success "Firewall configured"
    else
        log_warning "UFW not found. Please configure firewall manually."
    fi
}

verify_ssl() {
    log_info "Verifying SSL certificate..."

    sleep 2

    if curl -sSf "https://$DOMAIN" > /dev/null 2>&1; then
        log_success "SSL certificate is working"
    else
        log_warning "Could not verify SSL certificate"
    fi
}

print_summary() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}SSL Certificate Setup Complete!${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Domain: https://$DOMAIN"
    echo "Certificate: /etc/letsencrypt/live/$DOMAIN/fullchain.pem"
    echo "Private Key: /etc/letsencrypt/live/$DOMAIN/privkey.pem"
    echo ""
    echo "Certificate Details:"
    sudo certbot certificates -d "$DOMAIN" | grep -A 5 "Certificate Name: $DOMAIN" || true
    echo ""
    echo "Auto-renewal: Enabled (runs twice daily)"
    echo ""
    echo "Nginx Configuration: /etc/nginx/sites-available/resoftai"
    echo ""
    echo "Test your SSL certificate:"
    echo "  https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# ============================================================================
# Main Script
# ============================================================================

main() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  ResoftAI SSL Certificate Setup"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    check_domain
    check_nginx
    install_certbot
    create_nginx_config
    enable_nginx_site
    obtain_certificate
    setup_auto_renewal
    configure_firewall
    verify_ssl
    print_summary
}

main "$@"
