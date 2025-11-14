# ResoftAI Production Deployment Checklist

This checklist ensures a smooth and secure deployment of ResoftAI to production environments.

## Version Information

- **Version**: 0.2.2 (Beta)
- **Release Date**: 2025-11-14
- **Build Status**: ✅ Verified
- **Test Coverage**: 90%+

---

## Pre-Deployment Checklist

### 1. Code Quality and Testing

- [ ] All unit tests passing (`pytest tests/ -v --cov`)
- [ ] Enterprise feature tests passing (`pytest tests/enterprise/ -v`)
- [ ] Plugin system tests passing (`pytest tests/plugins/ -v`)
- [ ] API endpoint tests passing (`pytest tests/api/ -v`)
- [ ] Frontend builds without errors (`npm run build`)
- [ ] Code linting passes (flake8, ruff)
- [ ] Type checking passes (mypy)
- [ ] Security scan clean (bandit)
- [ ] No sensitive data in code (API keys, passwords, secrets)

### 2. Database Preparation

- [ ] Database migrations reviewed (`alembic history`)
- [ ] All migrations applied (`alembic upgrade head`)
- [ ] Database backup strategy in place
- [ ] Database indexes optimized
- [ ] Connection pooling configured (for PostgreSQL)
- [ ] Database user permissions reviewed
- [ ] Database SSL/TLS enabled (production)

### 3. Environment Configuration

- [ ] Production `.env` file created (DO NOT commit!)
- [ ] All required environment variables set
- [ ] LLM API keys configured securely
- [ ] JWT secret keys generated (minimum 32 characters)
- [ ] Database connection string configured
- [ ] CORS origins configured appropriately
- [ ] Log levels set (INFO or WARNING for production)
- [ ] Debug mode disabled (`DEBUG=false`)

### 4. Security Hardening

- [ ] HTTPS/TLS certificates installed
- [ ] Strong password policy enabled
- [ ] Rate limiting configured
- [ ] CORS properly restricted
- [ ] Input validation enabled
- [ ] SQL injection protection verified
- [ ] XSS protection enabled
- [ ] CSRF protection enabled
- [ ] Security headers configured
- [ ] File upload size limits set
- [ ] Session timeout configured

### 5. Infrastructure

- [ ] Server hardware/VM meets minimum requirements
- [ ] Reverse proxy configured (nginx/Apache)
- [ ] Load balancer set up (if applicable)
- [ ] CDN configured for static assets
- [ ] Firewall rules configured
- [ ] Monitoring tools installed
- [ ] Log aggregation configured
- [ ] Backup system in place
- [ ] Disaster recovery plan documented

### 6. Performance Optimization

- [ ] Frontend assets minified and compressed
- [ ] Gzip/Brotli compression enabled
- [ ] Static file caching configured
- [ ] Database query optimization verified
- [ ] API response caching implemented
- [ ] WebSocket scaling configured
- [ ] Resource limits set (CPU, memory)
- [ ] Connection pool sizes optimized

---

## Deployment Steps

### Step 1: Server Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required system packages
sudo apt install -y python3.11 python3.11-venv nginx postgresql-14 redis-server

# Create application user
sudo useradd -m -s /bin/bash resoftai
sudo usermod -aG www-data resoftai

# Create application directory
sudo mkdir -p /opt/resoftai
sudo chown resoftai:resoftai /opt/resoftai
```

### Step 2: Code Deployment

```bash
# Switch to application user
sudo su - resoftai

# Clone repository (or copy files)
cd /opt/resoftai
git clone https://github.com/your-org/resoftai-cli.git .
git checkout main  # or specific release tag

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Gunicorn for production
pip install gunicorn uvicorn[standard]
```

### Step 3: Database Setup

```bash
# Create PostgreSQL database and user
sudo -u postgres psql <<EOF
CREATE DATABASE resoftai_prod;
CREATE USER resoftai_user WITH ENCRYPTED PASSWORD 'CHANGE_THIS_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE resoftai_prod TO resoftai_user;
\c resoftai_prod
GRANT ALL ON SCHEMA public TO resoftai_user;
EOF

# Run database migrations
export PYTHONPATH=/opt/resoftai/src
export DATABASE_URL=postgresql+asyncpg://resoftai_user:CHANGE_THIS_PASSWORD@localhost/resoftai_prod

alembic upgrade head

# Initialize database
python scripts/init_db.py
```

### Step 4: Environment Configuration

```bash
# Create production .env file
cat > /opt/resoftai/.env <<EOF
# Application
DEBUG=false
ENV=production
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')

# Database
DATABASE_URL=postgresql+asyncpg://resoftai_user:CHANGE_THIS_PASSWORD@localhost/resoftai_prod

# JWT Authentication
JWT_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# LLM Providers (configure at least one)
DEEPSEEK_API_KEY=sk-your-deepseek-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GOOGLE_API_KEY=your-google-key
MOONSHOT_API_KEY=sk-your-moonshot-key

# API Configuration
API_V1_PREFIX=/api/v1
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# File Upload
MAX_UPLOAD_SIZE=104857600  # 100MB
UPLOAD_DIR=/opt/resoftai/uploads

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/resoftai/app.log

# Redis (for caching and WebSocket)
REDIS_URL=redis://localhost:6379/0

# Performance
WORKERS=4
MAX_REQUESTS=1000
MAX_REQUESTS_JITTER=50
EOF

# Secure the .env file
chmod 600 /opt/resoftai/.env

# Create necessary directories
mkdir -p /opt/resoftai/uploads
mkdir -p /var/log/resoftai
chmod 755 /opt/resoftai/uploads
```

### Step 5: Frontend Build and Deployment

```bash
# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Build frontend
cd /opt/resoftai/frontend
npm install
npm run build

# Copy built files to web root
sudo mkdir -p /var/www/resoftai
sudo cp -r dist/* /var/www/resoftai/
sudo chown -R www-data:www-data /var/www/resoftai
```

### Step 6: Systemd Service Configuration

```bash
# Create systemd service file
sudo tee /etc/systemd/system/resoftai.service <<EOF
[Unit]
Description=ResoftAI Backend Service
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=resoftai
Group=resoftai
WorkingDirectory=/opt/resoftai
Environment="PATH=/opt/resoftai/venv/bin"
Environment="PYTHONPATH=/opt/resoftai/src"
EnvironmentFile=/opt/resoftai/.env
ExecStart=/opt/resoftai/venv/bin/gunicorn resoftai.api.main:asgi_app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    --access-logfile /var/log/resoftai/access.log \
    --error-logfile /var/log/resoftai/error.log \
    --log-level info \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 50
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable resoftai
sudo systemctl start resoftai
sudo systemctl status resoftai
```

### Step 7: Nginx Configuration

```bash
# Create nginx configuration
sudo tee /etc/nginx/sites-available/resoftai <<EOF
# Rate limiting
limit_req_zone \$binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone \$binary_remote_addr zone=auth_limit:10m rate=5r/m;

# Upstream backend
upstream resoftai_backend {
    server 127.0.0.1:8000 fail_timeout=0;
}

# HTTPS redirect
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://\$server_name\$request_uri;
}

# Main HTTPS server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Frontend static files
    root /var/www/resoftai;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;

    # API proxy
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;

        proxy_pass http://resoftai_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Auth endpoints with stricter rate limiting
    location /api/v1/auth/ {
        limit_req zone=auth_limit burst=5 nodelay;

        proxy_pass http://resoftai_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
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
        proxy_read_timeout 86400;
    }

    # Static files with caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Frontend routing (SPA)
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # File upload size
    client_max_body_size 100M;

    # Access logs
    access_log /var/log/nginx/resoftai_access.log;
    error_log /var/log/nginx/resoftai_error.log;
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/resoftai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 8: SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is configured by default
sudo certbot renew --dry-run
```

### Step 9: Monitoring and Logging

```bash
# Install monitoring tools
pip install prometheus-client
pip install sentry-sdk

# Configure log rotation
sudo tee /etc/logrotate.d/resoftai <<EOF
/var/log/resoftai/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 resoftai resoftai
    sharedscripts
    postrotate
        systemctl reload resoftai > /dev/null 2>&1 || true
    endscript
}
EOF

# Test log rotation
sudo logrotate -f /etc/logrotate.d/resoftai
```

---

## Post-Deployment Verification

### Health Checks

```bash
# Check backend service
sudo systemctl status resoftai
curl https://yourdomain.com/api/v1/health

# Check database connection
sudo -u postgres psql resoftai_prod -c "SELECT COUNT(*) FROM users;"

# Check nginx
sudo systemctl status nginx
curl -I https://yourdomain.com

# Check logs
tail -f /var/log/resoftai/app.log
tail -f /var/log/nginx/resoftai_access.log
```

### Functional Testing

- [ ] Homepage loads correctly
- [ ] User registration works
- [ ] User login works
- [ ] JWT tokens are issued correctly
- [ ] API endpoints respond correctly
- [ ] File upload works
- [ ] Project creation works
- [ ] Agent execution works
- [ ] WebSocket connections work
- [ ] Plugin installation works (if enabled)
- [ ] Organization management works (Enterprise)
- [ ] Team management works (Enterprise)
- [ ] Quota monitoring works (Enterprise)

### Performance Testing

```bash
# Basic load test with Apache Bench
ab -n 1000 -c 10 https://yourdomain.com/

# API endpoint test
ab -n 100 -c 5 -H "Authorization: Bearer YOUR_TOKEN" https://yourdomain.com/api/v1/projects/

# Run Locust performance tests (if available)
locust -f tests/performance/locustfile.py --host=https://yourdomain.com
```

### Security Testing

- [ ] HTTPS enforced (HTTP redirects to HTTPS)
- [ ] Security headers present
- [ ] Rate limiting works
- [ ] Authentication required for protected endpoints
- [ ] CORS configuration correct
- [ ] No sensitive data in responses
- [ ] SQL injection protection works
- [ ] XSS protection works
- [ ] File upload restrictions work

---

## Monitoring Setup

### Application Monitoring

```python
# Add to main.py for Prometheus metrics
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Log Monitoring

```bash
# Install and configure Fail2Ban for brute force protection
sudo apt install -y fail2ban

sudo tee /etc/fail2ban/jail.local <<EOF
[resoftai-auth]
enabled = true
port = https,http
filter = resoftai-auth
logpath = /var/log/resoftai/app.log
maxretry = 5
bantime = 3600
findtime = 600
EOF

sudo tee /etc/fail2ban/filter.d/resoftai-auth.conf <<EOF
[Definition]
failregex = ^.*Authentication failed for user.*from <HOST>.*$
ignoreregex =
EOF

sudo systemctl restart fail2ban
```

### Uptime Monitoring

Set up external monitoring with services like:
- UptimeRobot
- Pingdom
- StatusCake
- New Relic
- Datadog

---

## Backup Strategy

### Database Backups

```bash
# Create backup script
sudo tee /usr/local/bin/backup-resoftai-db.sh <<'EOF'
#!/bin/bash
BACKUP_DIR=/var/backups/resoftai
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
pg_dump resoftai_prod | gzip > $BACKUP_DIR/resoftai_db_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "resoftai_db_*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
# aws s3 cp $BACKUP_DIR/resoftai_db_$DATE.sql.gz s3://your-bucket/backups/
EOF

sudo chmod +x /usr/local/bin/backup-resoftai-db.sh

# Schedule daily backups
sudo tee -a /etc/crontab <<EOF
0 2 * * * postgres /usr/local/bin/backup-resoftai-db.sh
EOF
```

### File Backups

```bash
# Backup uploads directory
sudo tee /usr/local/bin/backup-resoftai-files.sh <<'EOF'
#!/bin/bash
BACKUP_DIR=/var/backups/resoftai
DATE=$(date +%Y%m%d_%H%M%S)

# Backup uploads
tar -czf $BACKUP_DIR/resoftai_files_$DATE.tar.gz /opt/resoftai/uploads

# Keep only last 7 days
find $BACKUP_DIR -name "resoftai_files_*.tar.gz" -mtime +7 -delete
EOF

sudo chmod +x /usr/local/bin/backup-resoftai-files.sh

# Schedule weekly backups
sudo tee -a /etc/crontab <<EOF
0 3 * * 0 root /usr/local/bin/backup-resoftai-files.sh
EOF
```

---

## Scaling Considerations

### Horizontal Scaling

For high-traffic deployments:

1. **Load Balancer**: Use nginx, HAProxy, or cloud load balancer
2. **Multiple Application Servers**: Run multiple backend instances
3. **Session Storage**: Use Redis for shared session storage
4. **File Storage**: Use S3 or similar for file uploads
5. **Database**: Set up PostgreSQL replication (read replicas)

### Vertical Scaling

Recommended server specifications:

**Minimum (< 100 users)**
- 2 vCPU
- 4 GB RAM
- 50 GB SSD

**Recommended (100-1000 users)**
- 4 vCPU
- 8 GB RAM
- 100 GB SSD

**High Performance (1000+ users)**
- 8+ vCPU
- 16+ GB RAM
- 200+ GB SSD

---

## Troubleshooting

### Common Issues

#### Application won't start

```bash
# Check logs
sudo journalctl -u resoftai -n 50 --no-pager

# Check environment variables
sudo systemctl show resoftai | grep Environment

# Check Python path
sudo -u resoftai /opt/resoftai/venv/bin/python -c "import sys; print(sys.path)"
```

#### Database connection errors

```bash
# Test database connection
psql -h localhost -U resoftai_user -d resoftai_prod -c "SELECT 1;"

# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection limits
psql -U postgres -c "SHOW max_connections;"
```

#### High memory usage

```bash
# Check memory usage
free -m
ps aux --sort=-%mem | head

# Reduce worker count in systemd service
sudo systemctl edit resoftai
# Change --workers parameter

# Restart service
sudo systemctl restart resoftai
```

#### WebSocket connection failures

```bash
# Check nginx WebSocket configuration
sudo nginx -t

# Check firewall
sudo ufw status

# Test WebSocket connection
wscat -c wss://yourdomain.com/ws/
```

---

## Maintenance

### Regular Maintenance Tasks

**Daily**
- [ ] Check application logs for errors
- [ ] Monitor system resources (CPU, memory, disk)
- [ ] Verify backups completed successfully

**Weekly**
- [ ] Review security logs
- [ ] Check for failed login attempts
- [ ] Update system packages
- [ ] Review performance metrics

**Monthly**
- [ ] Update Python dependencies (after testing)
- [ ] Review and optimize database queries
- [ ] Clean up old logs and temporary files
- [ ] Review user feedback and bug reports
- [ ] Test backup restoration

**Quarterly**
- [ ] Security audit
- [ ] Penetration testing
- [ ] Disaster recovery drill
- [ ] Performance optimization review

---

## Support and Resources

### Documentation
- User Manual: `/docs/USER_MANUAL.md`
- API Documentation: `/docs/API_DOCUMENTATION.md`
- Mobile Optimization: `/docs/MOBILE_OPTIMIZATION.md`
- Enterprise Features: `/docs/ENTERPRISE.md`

### Getting Help
- GitHub Issues: https://github.com/your-org/resoftai-cli/issues
- Email: support@yourdomain.com
- Documentation: https://docs.yourdomain.com

### Emergency Contacts
- **System Administrator**: [contact]
- **Database Administrator**: [contact]
- **Security Team**: [contact]
- **DevOps Team**: [contact]

---

## Rollback Plan

In case of deployment issues:

```bash
# Stop the service
sudo systemctl stop resoftai

# Restore database from backup
gunzip -c /var/backups/resoftai/resoftai_db_TIMESTAMP.sql.gz | psql resoftai_prod

# Restore previous code version
cd /opt/resoftai
git checkout PREVIOUS_TAG

# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt

# Downgrade database if needed
alembic downgrade -1

# Restart service
sudo systemctl start resoftai
```

---

## Deployment Completion

### Final Checklist

- [ ] All deployment steps completed
- [ ] All health checks passing
- [ ] Monitoring configured and alerts set up
- [ ] Backups verified and tested
- [ ] Documentation updated
- [ ] Team trained on new features
- [ ] Support channels notified
- [ ] Deployment documented in change log
- [ ] Post-deployment review scheduled

### Sign-off

**Deployed by**: ________________
**Date**: ________________
**Version**: 0.2.2 (Beta)
**Environment**: Production
**Approved by**: ________________

---

**Congratulations! Your ResoftAI deployment is complete.**

For ongoing support and updates, refer to the documentation and support resources listed above.
