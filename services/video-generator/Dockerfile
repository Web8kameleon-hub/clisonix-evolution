FROM python:3.13

WORKDIR /app

# Install FFmpeg, fonts, and system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    fonts-dejavu-core \
    fonts-liberation \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY services/video-generator/requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy video generator code
COPY video_generator_blerina.py /app/
COPY services/video-generator/main.py /app/

# Create output directories
RUN mkdir -p /app/generated_videos /app/temp

# Expose port
EXPOSE 8029

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8029/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8029"]
