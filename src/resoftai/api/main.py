"""FastAPI main application."""
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import socketio

from resoftai.config import Settings
from resoftai.db import init_db, close_db
from resoftai.api.routes import auth, projects, agent_activities, files, llm_configs, execution, monitoring
from resoftai.api.errors import ResoftAIError, handle_resoftai_error
from resoftai.websocket import sio

logger = logging.getLogger(__name__)
settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting ResoftAI API server...")
    await init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down ResoftAI API server...")
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI app
app = FastAPI(
    title="ResoftAI API",
    description="Multi-Agent Software Development Platform API",
    version="0.2.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(agent_activities.router, prefix="/api")
app.include_router(files.router, prefix="/api")
app.include_router(llm_configs.router, prefix="/api")
app.include_router(execution.router, prefix="/api")
app.include_router(monitoring.router, prefix="/api")

# Mount Socket.IO
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ResoftAI API",
        "version": "0.2.0",
        "docs": "/docs",
        "websocket": "/socket.io"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "resoftai-api"
    }


# Exception handlers
@app.exception_handler(ResoftAIError)
async def resoftai_exception_handler(request: Request, exc: ResoftAIError):
    """Handle ResoftAI custom errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


# Export the socket app as the main ASGI application
asgi_app = socket_app
