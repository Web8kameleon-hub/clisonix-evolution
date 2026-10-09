FROM python:3.13

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    stripe \
    pydantic \
    python-multipart

COPY services/blog-paywall/blog_paywall_service.py .

EXPOSE 8020

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8020/health || exit 1

CMD ["uvicorn", "blog_paywall_service:app", "--host", "0.0.0.0", "--port", "8020"]
