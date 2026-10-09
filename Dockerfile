FROM node:20-alpine AS frontend-builder

WORKDIR /app

# Copy package files from root (monorepo uses root package-lock.json)
COPY package.json package-lock.json* ./
COPY apps/web/package.json apps/web/

# Install dependencies
RUN npm ci --workspace=apps/web || npm install

# Copy frontend source
COPY apps/web apps/web

# Build frontend
WORKDIR /app/apps/web
RUN npm run build

# Backend stage
FROM python:3.13

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements (only files that exist)
COPY requirements.txt .
COPY requirements-ocean.txt .
COPY apps/api/requirements.txt apps/api/
COPY apps/api/requirements-excel.txt apps/api/

# Install Python dependencies (numpy first, then Excel deps isolated)
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-ocean.txt && \
    pip install --no-cache-dir -r apps/api/requirements.txt && \
    pip install --no-cache-dir -r apps/api/requirements-excel.txt

# Copy application code
COPY apps/api /app/apps/api
COPY ocean-core /app/ocean-core
COPY --from=frontend-builder /app/apps/web/.next /app/apps/web/.next
COPY --from=frontend-builder /app/apps/web/public /app/apps/web/public
COPY --from=frontend-builder /app/apps/web/package.json /app/apps/web/

# Copy shared files
COPY . /app

# Expose ports
EXPOSE 8000 8030 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Default command (can be overridden)
CMD ["python", "-m", "uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
