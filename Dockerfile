# Multi-stage production Dockerfile for CanopyAI
FROM python:3.11-slim AS builder

WORKDIR /build

# Install system build dependencies if necessary
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into isolated wheel directory
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final minimal production stage (< 500MB)
FROM python:3.11-slim AS runner

WORKDIR /app

# Set production environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:$PATH" \
    PORT=8000

# Copy installed python dependencies from builder stage
COPY --from=builder /root/.local /root/.local

# Copy application source code only (tests and .env are excluded via .dockerignore)
COPY app/ /app/app/

# Expose backend port
EXPOSE 8000

# Healthcheck for container orchestrators
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Launch production server via Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

