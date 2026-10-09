# CLX BRAIN Docker Image
# Multi-stage build for optimal size

FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY services/clx_brain/requirements.txt .

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt


# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Set PATH
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY services/clx_brain /app/clx_brain

# Create non-root user
RUN useradd -m -u 1000 clxbrain && chown -R clxbrain:clxbrain /app

USER clxbrain

# Expose port
EXPOSE 1001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:1001/brain/status || exit 1

# Run the service
CMD ["python", "-m", "uvicorn", "clx_brain.api:app", "--host", "0.0.0.0", "--port", "1001"]
