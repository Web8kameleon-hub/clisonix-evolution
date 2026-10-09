FROM python:3.13

WORKDIR /app

# Install git + curl for blog sync and health checks
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Copy root-level content factory modules
COPY blerina_core.py /app/
COPY eap_layer.py /app/
COPY clx_publisher.py /app/
COPY content_factory.py /app/

# Copy service requirements and code
COPY services/content-factory/requirements.txt /app/
COPY services/content-factory/main.py /app/
COPY services/content-factory/auto_publisher.py /app/
COPY services/content-factory/blog_sync.py /app/
COPY services/content-factory/academic_reporter.py /app/

# Create output directories for published articles and blog repo
RUN mkdir -p /app/published /app/blog-repo

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 4003

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-4003}"]
