FROM python:3.14-bookworm

WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn matplotlib networkx httpx
COPY packages/__init__.py /app/packages/__init__.py
COPY packages/gram /app/packages/gram
USER 1001
EXPOSE 9710
HEALTHCHECK --interval=30s --timeout=8s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:9710/health', timeout=5)"
CMD ["uvicorn", "packages.gram.server:app", "--host", "0.0.0.0", "--port", "9710"]
