FROM python:3.13

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uvicorn fastapi httpx redis

COPY api.py .
COPY discovery.py .
COPY explore.py .
COPY search.py .
COPY __init__.py .

EXPOSE 8011

CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8011"]
