FROM python:3.13

WORKDIR /app

# Install Docker CLI for container commands
RUN apt-get update && apt-get install -y \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY excel_reporting_api.py .

EXPOSE 8010

CMD ["uvicorn", "excel_reporting_api:app", "--host", "0.0.0.0", "--port", "8010"]
