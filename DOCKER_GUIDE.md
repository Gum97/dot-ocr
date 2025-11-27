# Docker Deployment Guide - dots.ocr API

Hướng dẫn đóng gói và deploy dots.ocr API lên Docker Hub.

## 📋 Prerequisites

1. **Docker installed**: 
   ```bash
   docker --version
   ```

2. **Docker Hub account**: 
   - Đăng ký tại: https://hub.docker.com/
   - Tạo repository: `your-username/dots-ocr-api`

3. **Model weights** (optional):
   ```bash
   python tools/download_model.py
   ```
   Nếu không download trước, image sẽ nhẹ hơn nhưng phải download khi run lần đầu.

## 🚀 Quick Start

### Method 1: Build & Push Manually

#### Step 1: Login to Docker Hub

```bash
docker login
# Nhập username và password Docker Hub
```

#### Step 2: Build Images

**CPU version (recommended cho deployment):**
```bash
docker build -t your-username/dots-ocr-api:latest-cpu -f Dockerfile .
```

**GPU version (nếu server có GPU):**
```bash
docker build -t your-username/dots-ocr-api:latest-gpu -f Dockerfile.gpu .
```

#### Step 3: Tag as Latest

```bash
docker tag your-username/dots-ocr-api:latest-cpu your-username/dots-ocr-api:latest
```

#### Step 4: Push to Docker Hub

```bash
docker push your-username/dots-ocr-api:latest-cpu
docker push your-username/dots-ocr-api:latest-gpu
docker push your-username/dots-ocr-api:latest
```

### Method 2: Use Build Script (Easier)

**Windows:**
```bash
# Sửa username trong docker-build.bat trước
set DOCKER_USERNAME=your-username

# Run script
docker-build.bat
```

**Linux/Mac:**
```bash
# Sửa username trong docker-build.sh trước
export DOCKER_USERNAME=your-username

# Run script
chmod +x docker-build.sh
./docker-build.sh
```

## 📦 Using Docker Compose

### Run CPU Version

```bash
docker-compose up -d dots-ocr-api-cpu
```

### Run GPU Version

```bash
# Cần nvidia-docker installed
docker-compose --profile gpu up -d dots-ocr-api-gpu
```

### Run với Web Interface

```bash
docker-compose --profile web up -d
```

Truy cập:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Web: http://localhost:3000

## 🌐 Pull & Run từ Docker Hub

### Simple Run

```bash
# Pull image
docker pull your-username/dots-ocr-api:latest

# Run (without model weights)
docker run -d \
  -p 8000:8000 \
  --name dots-ocr-api \
  your-username/dots-ocr-api:latest
```

**Note**: Lần đầu chạy sẽ download model (~3.5GB), có thể mất thời gian.

### Run với Volumes (Recommended)

```bash
# Create directories
mkdir -p weights uploads results temp

# Download model trước (optional)
# python tools/download_model.py

# Run with volumes
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/weights:/app/weights \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/results:/app/results \
  -v $(pwd)/temp:/app/temp \
  --name dots-ocr-api \
  your-username/dots-ocr-api:latest
```

### Run GPU Version

```bash
docker run -d \
  -p 8000:8000 \
  --gpus all \
  -v $(pwd)/weights:/app/weights \
  --name dots-ocr-api-gpu \
  your-username/dots-ocr-api:latest-gpu
```

## 🔧 Configuration

### Environment Variables

```bash
docker run -d \
  -p 8000:8000 \
  -e DEVICE=cpu \
  -e DEBUG=false \
  -e MAX_UPLOAD_SIZE=52428800 \
  your-username/dots-ocr-api:latest
```

Available variables:
- `DEVICE`: `auto`, `cpu`, `cuda` (default: `cpu`)
- `DEBUG`: `true`, `false` (default: `false`)
- `MAX_UPLOAD_SIZE`: Max file size in bytes (default: 50MB)
- `MODEL_PATH`: Model weights path (default: `/app/weights/DotsOCR`)

## 📊 Image Sizes

| Version | Size (approx) | Notes |
|---------|---------------|-------|
| CPU only | ~3-4GB | Without model weights |
| CPU + weights | ~7-8GB | With model baked in |
| GPU only | ~5-6GB | CUDA base image |
| GPU + weights | ~9-10GB | Full GPU image |

**Recommendation**: Use version without weights, mount as volume. Nhẹ hơn và reuse được.

## 🧪 Testing

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

### Upload Test

```bash
curl -X POST "http://localhost:8000/api/v1/process" \
  -F "file=@test.pdf"
```

### Check Logs

```bash
docker logs dots-ocr-api
```

## 🔄 Update & Redeploy

```bash
# Pull latest
docker pull your-username/dots-ocr-api:latest

# Stop old container
docker stop dots-ocr-api
docker rm dots-ocr-api

# Run new version
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/weights:/app/weights \
  --name dots-ocr-api \
  your-username/dots-ocr-api:latest
```

## 📝 Docker Hub Repository Setup

1. Tạo repository trên Docker Hub:
   - Tên: `dots-ocr-api`
   - Visibility: Public hoặc Private
   - Description: "Intelligent Document OCR API with auto file type detection"

2. Tags recommended:
   - `latest` - CPU version mới nhất
   - `latest-cpu` - Specifically CPU
   - `latest-gpu` - GPU version
   - `v1.0.0-cpu` - Versioned releases

## 🚨 Troubleshooting

### Issue: Model not found

**Solution**: Download model hoặc mount volume:
```bash
docker run -v $(pwd)/weights:/app/weights ...
```

### Issue: Out of memory

**Solution**: Increase Docker memory limit:
```bash
docker run --memory="8g" ...
```

### Issue: Slow processing

**Solution**: Use GPU version nếu có:
```bash
docker run --gpus all your-username/dots-ocr-api:latest-gpu
```

## 📚 Advanced Usage

### Multi-container Setup

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  api:
    image: your-username/dots-ocr-api:latest
    replicas: 3
    deploy:
      resources:
        limits:
          memory: 8G
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    depends_on:
      - api
```

### Custom Build với Model Weights

```dockerfile
# Dockerfile.with-weights
FROM your-username/dots-ocr-api:latest

# Download model during build
RUN python -c "from dots_ocr.parser import DotsOCRParser; \
    import os; os.makedirs('/app/weights', exist_ok=True)"
RUN wget -O /app/weights/model.tar.gz \
    https://huggingface.co/rednote-hilab/dots.ocr/resolve/main/model.tar.gz && \
    cd /app/weights && tar -xzf model.tar.gz && rm model.tar.gz
```

## 🎯 Production Deployment

### Cloud Run (GCP)

```bash
gcloud run deploy dots-ocr-api \
  --image your-username/dots-ocr-api:latest \
  --platform managed \
  --region asia-southeast1 \
  --memory 8Gi \
  --cpu 4
```

### AWS ECS

```bash
aws ecs run-task \
  --cluster dots-ocr-cluster \
  --task-definition dots-ocr-api \
  --count 1
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dots-ocr-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: your-username/dots-ocr-api:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            memory: "8Gi"
            cpu: "4"
```

## 📞 Support

- Docker Hub: https://hub.docker.com/r/your-username/dots-ocr-api
- GitHub Issues: https://github.com/rednote-hilab/dots.ocr/issues
- Documentation: http://localhost:8000/docs

---

**Happy Deploying! 🚀**
