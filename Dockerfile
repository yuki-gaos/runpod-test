# RunPod Test API - Dockerfile
# Multi-stage build for optimal image size

# Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/
COPY requirements.txt .

# Create directories for temporary files
RUN mkdir -p /tmp/runpod-outputs && \
    chown -R app:app /app /tmp/runpod-outputs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV RUNPOD_DEBUG=false

# Switch to non-root user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from src.utils import get_environment_config; print('healthy')" || exit 1

# Default command - starts the RunPod serverless handler
CMD ["python", "-m", "src.handler"]

# Labels for metadata
LABEL maintainer="yuki@gaos.ca"
LABEL description="RunPod Test API - Long-running processes with streaming progress"
LABEL version="1.0.0"
LABEL runpod.compatible="true"
LABEL runpod.serverless="true"