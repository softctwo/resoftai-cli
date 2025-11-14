# Multi-stage build for ResoftAI Backend
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ===== Production Stage =====
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH=/app/src

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create app directory
WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 resoftai && \
    chown -R resoftai:resoftai /app

# Copy application code
COPY --chown=resoftai:resoftai src/ /app/src/
COPY --chown=resoftai:resoftai alembic/ /app/alembic/
COPY --chown=resoftai:resoftai alembic.ini /app/
COPY --chown=resoftai:resoftai pyproject.toml /app/
COPY --chown=resoftai:resoftai docker/backend/entrypoint.sh /app/

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Switch to non-root user
USER resoftai

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "resoftai.api.main:asgi_app", "--host", "0.0.0.0", "--port", "8000"]
