FROM python:3.13

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY api.py ./
COPY __init__.py ./

EXPOSE 9211

CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "9211"]
