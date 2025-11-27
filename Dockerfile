# Multi-stage build for dots.ocr API
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt api_requirements.txt ./
COPY setup.py ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r api_requirements.txt

# Install PyTorch CPU version (smaller image)
RUN pip install --no-cache-dir \
    torch==2.4.0 \
    torchvision==0.19.0 \
    --index-url https://download.pytorch.org/whl/cpu

# Copy application code
COPY dots_ocr/ ./dots_ocr/
COPY api/ ./api/
COPY web/ ./web/
COPY scripts/ ./scripts/
COPY .env.example ./.env

# Install dots_ocr package
RUN pip install -e .

# Create directories for data
RUN mkdir -p /app/weights /app/uploads /app/results /app/temp

# Copy entrypoint script
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Expose port
EXPOSE 8000

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV DEVICE=cpu
ENV MODEL_PATH=/app/weights/DotsOCR

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Set entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Run the API
CMD ["python", "scripts/run_api.py", "--host", "0.0.0.0", "--port", "8000"]
