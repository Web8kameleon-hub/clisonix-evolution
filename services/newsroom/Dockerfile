FROM python:3.13

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

ENV NEWSROOM_PORT=9800
ENV PUBLISH_INTERVAL=3600
ENV MAX_LABS=200
ENV POSTS_PER_DAY=10

EXPOSE 9800

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:9800/health', timeout=5)"

CMD ["python", "main.py"]
