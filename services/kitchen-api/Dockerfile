FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY services/kitchen-api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY services/kitchen-api/main.py /app/main.py
COPY hybrid_protocol_pipeline.py /app/hybrid_protocol_pipeline.py

EXPOSE 8065

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8065"]
