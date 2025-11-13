# Known Issues and Pending Tasks

**Last Updated**: 2025-11-13

## 🚨 Critical Issues (Blocking)

### 1. PostgreSQL Not Running in Environment
**Status**: ❌ Unresolved
**Impact**: Database cannot be initialized, backend API cannot start with database features

**Error**:
```
pg_isready: /var/run/postgresql:5432 - no response
sudo service postgresql start: Permission denied (sudo configuration issue)
```

**Details**:
- PostgreSQL 16.10 is installed but not running
- Cannot start PostgreSQL service due to sudo permission issues in container
- Database initialization script (`scripts/init_db.py`) cannot be run
- All database-dependent features are blocked

**Workaround**:
- Use SQLite for development (requires code changes)
- Run PostgreSQL in separate container
- Run in environment with proper PostgreSQL service

**Fix Required**:
- Start PostgreSQL service manually: `pg_ctl -D /path/to/data start`
- Or update environment to allow PostgreSQL service startup
- Create database: `createdb resoftai`
- Run init script: `python scripts/init_db.py`

---

### 2. Cryptography Library Conflict
**Status**: ❌ Unresolved
**Impact**: JWT authentication cannot be tested, user auth routes will fail

**Error**:
```
ModuleNotFoundError: No module named '_cffi_backend'
pyo3_runtime.PanicException: Python API call failed
ERROR: Cannot uninstall cryptography 41.0.7, RECORD file not found.
Hint: The package was installed by debian.
```

**Details**:
- System-installed cryptography (41.0.7) conflicts with python-jose requirements
- Cannot uninstall/upgrade cryptography due to Debian package management
- JWT token creation and verification functions cannot be tested
- Authentication routes will fail when API starts

**Workaround**:
- Use PyJWT instead of python-jose
- Run in virtual environment
- Use Docker container with clean Python environment

**Fix Required**:
```bash
# Option 1: Use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Option 2: Update requirements.txt to use PyJWT
# Replace python-jose[cryptography] with PyJWT
```

---

## ⚠️ High Priority Issues (Partially Blocking)

### 3. Database Models Not Fully Tested
**Status**: ⚠️ Partially Resolved
**Impact**: Cannot verify database schema correctness

**Fixed**:
- ✅ SQLAlchemy `metadata` column conflict in Log model (renamed to `extra_data`)
- ✅ All model imports succeed
- ✅ Model relationships defined correctly

**Not Tested**:
- ❌ Database table creation
- ❌ Foreign key constraints
- ❌ Index performance
- ❌ CRUD operations with real database

**Fix Required**:
- Start PostgreSQL
- Run `python scripts/init_db.py`
- Test CRUD operations
- Verify relationships and constraints

---

### 4. API Endpoints Not Tested
**Status**: ❌ Unresolved
**Impact**: Cannot verify API functionality

**Not Tested**:
- ❌ Authentication endpoints (register, login, refresh, logout)
- ❌ Projects CRUD endpoints
- ❌ WebSocket connection and events
- ❌ CORS configuration
- ❌ Error handling

**Fix Required**:
- Start backend API: `uvicorn resoftai.api.main:asgi_app --reload`
- Test with curl/Postman
- Verify OpenAPI docs at http://localhost:8000/docs

---

### 5. Frontend-Backend Integration Not Tested
**Status**: ❌ Unresolved
**Impact**: Cannot verify full-stack functionality

**Not Tested**:
- ❌ Login flow
- ❌ API authentication (JWT tokens in headers)
- ❌ Project CRUD from frontend
- ❌ WebSocket real-time updates
- ❌ CORS between frontend and backend

**Fix Required**:
- Start backend: `cd /home/user/resoftai-cli && uvicorn resoftai.api.main:asgi_app --reload`
- Start frontend: `cd /home/user/resoftai-cli/frontend && npm run dev`
- Test login at http://localhost:5173
- Verify API calls work

---

## 📋 Medium Priority Issues (Non-Blocking)

### 6. Mock Data in Frontend Components
**Status**: ⚠️ Partially Resolved
**Impact**: Frontend shows placeholder data instead of real data

**Components Using Mock Data**:
- `Agents.vue`: Agent activities (line 160)
- `Files.vue`: File tree (line 119)
- `Models.vue`: LLM configurations (line 297)

**Fix Required**:
- Implement backend API endpoints:
  - `GET /api/agent-activities?project_id=X`
  - `GET /api/projects/{id}/files`
  - `GET /api/llm-configs`
  - `POST /api/llm-configs`
- Update frontend to call real APIs instead of mock data

---

### 7. Missing Backend API Endpoints
**Status**: ❌ Unresolved
**Impact**: Some frontend features won't work

**Missing Endpoints**:
- ❌ `GET /api/agent-activities` - List agent activities
- ❌ `GET /api/projects/{id}/files` - List project files
- ❌ `POST /api/projects/{id}/files` - Create file
- ❌ `DELETE /api/files/{id}` - Delete file
- ❌ `GET /api/files/{id}/versions` - File version history
- ❌ `GET /api/llm-configs` - List LLM configurations
- ❌ `POST /api/llm-configs` - Create LLM config
- ❌ `PUT /api/llm-configs/{id}` - Update LLM config
- ❌ `DELETE /api/llm-configs/{id}` - Delete LLM config
- ❌ `POST /api/llm-configs/{id}/test` - Test LLM connection

**Fix Required**:
- Create CRUD modules in `src/resoftai/crud/`
- Create API routes in `src/resoftai/api/routes/`
- Add routes to `src/resoftai/api/main.py`

---

### 8. Monaco Editor Not Integrated
**Status**: ❌ Unresolved
**Impact**: Cannot edit code files in browser

**Current State**:
- Files.vue uses simple textarea and `<pre><code>` blocks
- No syntax highlighting
- No IntelliSense
- No code formatting

**Fix Required**:
```bash
cd frontend
npm install monaco-editor @monaco-editor/react
```

Create `MonacoEditor.vue` component and integrate into `Files.vue`

---

### 9. Agent Workflow Not Implemented
**Status**: ❌ Unresolved
**Impact**: Cannot execute multi-agent development workflow

**Not Implemented**:
- ❌ Project workflow orchestration
- ❌ Agent task execution
- ❌ Inter-agent communication
- ❌ Task dependency management
- ❌ Code generation and file writing
- ❌ Test execution and verification

**Fix Required**:
- Implement `WorkflowOrchestrator` class
- Create project execution endpoint: `POST /api/projects/{id}/execute`
- Integrate agents with real LLM API calls
- Implement file system operations

---

## 📝 Low Priority Issues (Future Enhancement)

### 10. No Database Migrations
**Status**: ⚠️ Needs Setup
**Impact**: Schema changes require manual database updates

**Current State**:
- Alembic installed but not configured
- No migration files exist
- Schema changes require dropping and recreating tables

**Fix Required**:
```bash
# Initialize Alembic
alembic init alembic

# Create first migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

---

### 11. No Unit Tests
**Status**: ❌ Unresolved
**Impact**: Cannot verify code correctness

**Not Implemented**:
- ❌ Model tests
- ❌ CRUD tests
- ❌ API route tests
- ❌ Authentication tests
- ❌ LLM provider tests
- ❌ Agent tests

**Fix Required**:
- Add pytest and dependencies
- Create tests in `tests/` directory
- Add GitHub Actions CI

---

### 12. No API Rate Limiting
**Status**: ❌ Unresolved
**Impact**: API can be abused

**Fix Required**:
- Add `slowapi` or `fastapi-limiter`
- Configure rate limits per endpoint
- Add rate limit headers

---

### 13. No Logging Configuration
**Status**: ⚠️ Basic Only
**Impact**: Hard to debug production issues

**Current State**:
- Basic Python logging
- No log rotation
- No structured logging
- No log aggregation

**Fix Required**:
- Configure `structlog` or `loguru`
- Add log rotation (max size, max files)
- Add log levels per environment
- Consider external logging service (e.g., Sentry)

---

### 14. No Docker Configuration
**Status**: ❌ Unresolved
**Impact**: Deployment is manual

**Fix Required**:
- Create `Dockerfile` for backend
- Create `Dockerfile` for frontend
- Create `docker-compose.yml`
- Add environment variable documentation

---

### 15. No Production Configuration
**Status**: ⚠️ Dev Config Only
**Impact**: Not production-ready

**Missing**:
- ❌ HTTPS/SSL configuration
- ❌ Gunicorn/uWSGI setup
- ❌ Nginx reverse proxy config
- ❌ Environment-specific settings
- ❌ Secrets management
- ❌ Health check endpoints
- ❌ Metrics and monitoring

---

## ✅ Successfully Completed

### Backend Development
- ✅ PostgreSQL database models (8 tables)
- ✅ SQLAlchemy 2.0 async ORM configuration
- ✅ JWT authentication system
- ✅ Password hashing (bcrypt)
- ✅ WebSocket real-time communication (Socket.IO)
- ✅ LLM abstraction layer (6 providers)
- ✅ Agent base class with LLM integration
- ✅ Basic API structure (FastAPI)
- ✅ Authentication endpoints
- ✅ Projects CRUD endpoints
- ✅ Database initialization script
- ✅ Configuration management (.env)

### Frontend Development
- ✅ Vue 3 + Composition API setup
- ✅ Element Plus UI integration
- ✅ Pinia state management
- ✅ Authentication store
- ✅ Route guards
- ✅ Login/Register page
- ✅ Dashboard page
- ✅ Projects management page
- ✅ Project detail page
- ✅ Agents monitoring page
- ✅ Files management page
- ✅ Models configuration page
- ✅ WebSocket composable
- ✅ Real-time updates integration

### Documentation
- ✅ README.md with project overview
- ✅ BACKEND_SETUP.md with setup instructions
- ✅ .env.example with configuration template
- ✅ Detailed development tasks document
- ✅ Feature planning and analysis
- ✅ This issues document

---

## 🎯 Next Steps

### Immediate (To Make System Usable)
1. Fix PostgreSQL startup issue
2. Resolve cryptography library conflict
3. Initialize database
4. Start and test backend API
5. Test frontend-backend integration

### Short-term (1-2 Days)
1. Implement missing API endpoints
2. Replace mock data with real API calls
3. Test authentication flow end-to-end
4. Test WebSocket real-time updates
5. Implement basic agent workflow

### Medium-term (1 Week)
1. Add Monaco Editor integration
2. Implement full agent workflow
3. Add unit tests
4. Set up Docker containers
5. Add database migrations

### Long-term (Future)
1. Add comprehensive testing
2. Implement rate limiting
3. Add monitoring and metrics
4. Production deployment guide
5. Performance optimization

---

## 📊 Testing Summary

### ✅ Tested and Working
- Settings configuration loading
- LLM factory (DeepSeek provider creation)
- Database model imports
- WebSocket manager import

### ❌ Not Tested (Blocked)
- Database table creation
- CRUD operations
- JWT authentication
- API endpoints
- WebSocket connections
- Frontend-backend integration
- Agent execution

### ⚠️ Partially Tested
- Environment configuration (loaded but DB not tested)
- Model relationships (defined but not verified)

---

## 💡 Recommendations

1. **Priority 1**: Set up proper PostgreSQL instance
   - Use Docker: `docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:16`
   - Or fix sudo permissions

2. **Priority 2**: Fix cryptography dependency
   - Use virtual environment
   - Or switch to PyJWT library

3. **Priority 3**: Create comprehensive test suite
   - Start with unit tests for models
   - Add integration tests for API
   - Add E2E tests for full workflow

4. **Priority 4**: Improve error handling
   - Add global exception handlers
   - Improve error messages
   - Add request validation

5. **Priority 5**: Add monitoring
   - Health check endpoints
   - Prometheus metrics
   - Application logging

---

**For immediate help with setup, refer to**: `BACKEND_SETUP.md`
**For development planning, refer to**: `docs/development-tasks.md`
