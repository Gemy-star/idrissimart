# =============================================================================
# Dockerfile for Idrissimart Django Application
# Multi-stage build for production optimization
# =============================================================================

# Stage 1: Base Python image with system dependencies
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.8.0 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    pkg-config \
    libpq-dev \
    libmariadb-dev \
    libmariadb-dev-compat \
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    zlib1g-dev \
    gettext \
    curl \
    libglib2.0-0 \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

# Stage 2: Builder stage for installing Python dependencies
FROM base AS builder

# Install Poetry in builder
ENV PATH="/opt/poetry/bin:$PATH"

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies using Poetry (without creating venv since we're in Docker)
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-root --no-interaction --no-ansi

# Stage 3: Production image
FROM base AS production

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Copy Poetry installation from base
COPY --from=base /opt/poetry /opt/poetry
ENV PATH="/opt/poetry/bin:$PATH"

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser . /app/

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R appuser:appuser /app

# Expose ports
# 8000 for Gunicorn (HTTP)
# 8001 for Daphne (WebSocket)
EXPOSE 8000 8001

# Switch to app user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Default command (can be overridden in docker-compose)
CMD ["gunicorn", "idrissimart.wsgi:application", "--bind", "0.0.0.0:8000"]
