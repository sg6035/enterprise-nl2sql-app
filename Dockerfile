# Production Dockerfile for NL2SQL Enterprise Service
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000

# Create app directory and user
RUN groupadd -r appuser && useradd -r -g appuser appuser
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create necessary directories
RUN mkdir -p /app/logs /app/data \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Expose port
EXPOSE $PORT

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
