FROM nvidia/cuda:12.3.2-cudnn9-runtime-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1 HF_HOME=/models/cache OMP_NUM_THREADS=2
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip ca-certificates && rm -rf /var/lib/apt/lists/*
RUN pip3 install --no-cache-dir faster-whisper==1.2.1 fastapi==0.115.12 uvicorn==0.34.0 edge-tts==7.2.8
WORKDIR /app
COPY app.py ./app.py
EXPOSE 8045
CMD ["python3", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8045"]
