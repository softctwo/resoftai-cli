# ResoftAI Backend Setup Guide

## Prerequisites

1. **PostgreSQL 12+** installed and running
2. **Python 3.9+** installed
3. **pip** package manager

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and configure:

```bash
# Database (REQUIRED)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/resoftai

# LLM Provider (REQUIRED)
LLM_PROVIDER=deepseek  # or anthropic, zhipu, moonshot, minimax, google
LLM_API_KEY=your_actual_api_key_here
LLM_MODEL=deepseek-chat

# JWT Secret (REQUIRED - Generate a secure key!)
JWT_SECRET_KEY=$(openssl rand -hex 32)
```

### 3. Create PostgreSQL Database

```bash
# Using psql
createdb resoftai

# Or manually:
psql -U postgres
CREATE DATABASE resoftai;
\q
```

### 4. Initialize Database

```bash
python scripts/init_db.py
```

This will:
- Create all database tables
- Create default admin user (username: `admin`, password: `admin123`)

### 5. Start the API Server

```bash
# Development mode (with auto-reload)
uvicorn resoftai.api.main:asgi_app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn resoftai.api.main:asgi_app --host 0.0.0.0 --port 8000 --workers 4
```

### 6. Verify Installation

Open your browser:

- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- WebSocket: ws://localhost:8000/socket.io

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login (returns JWT tokens)
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout

### Projects

- `GET /api/projects` - List projects (with pagination)
- `POST /api/projects` - Create project
- `GET /api/projects/{id}` - Get project details
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

### WebSocket Events

Connect to `/socket.io` and emit:

```javascript
// Join project room
socket.emit('join_project', {project_id: 123, user_id: 456})

// Listen for events
socket.on('project.progress', (data) => {
  console.log('Progress:', data.percentage, data.message)
})

socket.on('agent.status', (data) => {
  console.log('Agent:', data.agent_role, data.status)
})

socket.on('log.new', (data) => {
  console.log('Log:', data.level, data.message)
})
```

## Default Credentials

After running `init_db.py`:

```
Username: admin
Password: admin123
```

**⚠️ IMPORTANT**: Change the default password immediately!

## Testing

### Test Authentication

```bash
# Register a new user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

### Test Projects API

```bash
# Get your access token from login response
TOKEN="your_access_token_here"

# Create a project
curl -X POST http://localhost:8000/api/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "requirements": "Build a simple todo app with authentication"
  }'

# List projects
curl -X GET http://localhost:8000/api/projects \
  -H "Authorization: Bearer $TOKEN"
```

## Troubleshooting

### Database Connection Error

```
asyncpg.exceptions.InvalidCatalogNameError: database "resoftai" does not exist
```

**Solution**: Create the database first:
```bash
createdb resoftai
```

### Import Error

```
ModuleNotFoundError: No module named 'resoftai'
```

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### JWT Secret Key Error

```
WARNING: Using default JWT secret key
```

**Solution**: Set a secure JWT_SECRET_KEY in `.env`:
```bash
JWT_SECRET_KEY=$(openssl rand -hex 32)
```

## Development Tips

### Database Migrations

If you modify models, create a migration:

```bash
# Install alembic (should be in requirements.txt)
pip install alembic

# Initialize alembic (already done if you cloned the repo)
alembic init alembic

# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head
```

### Viewing Logs

```bash
# Set log level in .env
RESOFTAI_LOG_LEVEL=DEBUG

# Or in Python:
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing WebSocket

Use a WebSocket client like `socket.io-client`:

```javascript
const io = require('socket.io-client')
const socket = io('http://localhost:8000')

socket.on('connect', () => {
  console.log('Connected!')
  socket.emit('join_project', {project_id: '1'})
})

socket.on('project.progress', (data) => {
  console.log('Progress update:', data)
})
```

## Production Deployment

### Environment Variables

Set these in production:

```bash
# Security
JWT_SECRET_KEY=<strong-random-key>  # Use openssl rand -hex 32

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# API
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false  # Disable auto-reload in production

# Logging
RESOFTAI_LOG_LEVEL=INFO
```

### Using Gunicorn

```bash
pip install gunicorn uvicorn[standard]

gunicorn resoftai.api.main:asgi_app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY scripts/ scripts/

ENV PYTHONPATH=/app/src

CMD ["uvicorn", "resoftai.api.main:asgi_app", "--host", "0.0.0.0", "--port", "8000"]
```

## Need Help?

- Check the API docs: http://localhost:8000/docs
- View logs for error messages
- Ensure PostgreSQL is running: `pg_isready`
- Test database connection: `psql -d resoftai -c "SELECT 1"`

---

**Last Updated**: 2025-11-13
