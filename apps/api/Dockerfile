# Clisonix API Dockerfile
FROM python:3.14

WORKDIR /app/apps/api

# Build from the repository root so package imports and shared routers exist.
COPY apps/api/ /app/apps/api/
COPY ai_model_versioning.py model_governance.py reviewer_identity_registry.py /app/
COPY routes/alba_routes.py /app/apps/api/routes/alba_routes.py
ENV PYTHONPATH=/app:/app/apps/api

# Install dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r requirements-excel.txt

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
