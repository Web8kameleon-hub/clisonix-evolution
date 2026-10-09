FROM python:3.13

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY services/kloud_upstream_runtime/requirements.txt /tmp/requirements.txt
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm -rf /var/lib/apt/lists/* /tmp/requirements.txt

COPY services/kloud_upstream_runtime/ /app/

EXPOSE 9080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9080"]
