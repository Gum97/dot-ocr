# dots.ocr - Intelligent Document OCR API & Web Interface

Complete REST API and modern web interface for [dots.ocr](https://github.com/rednote-hilab/dots.ocr) - Multilingual Document Layout Parsing with Vision-Language Model.

[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://hub.docker.com)
[![Python](https://img.shields.io/badge/Python-3.10+-green)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-red)](https://fastapi.tiangolo.com)

## ✨ Features

- 🎯 **Unified API Endpoint** - One endpoint handles all file types (PDF, Image, DOCX)
- 🔄 **Auto-Convert** - DOCX → PDF automatic conversion before OCR
- 🖥️ **CPU & GPU Support** - Auto-detect and use available hardware
- 🌐 **Modern Web UI** - Beautiful drag-and-drop interface
- 📝 **4 Prompt Modes** - Full Layout, Layout Only, OCR Only, Grounding
- 🌍 **100+ Languages** - Multilingual support including Vietnamese
- 🐳 **Docker Ready** - Easy deployment with Docker/Docker Compose

## 📋 Table of Contents

- [Quick Start](#-quick-start)
  - [Option 1: Docker (Recommended)](#option-1-docker-recommended)
  - [Option 2: Docker Compose](#option-2-docker-compose)
  - [Option 3: Local Development](#option-3-local-development)
- [Project Structure](#-project-structure)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)

## 🚀 Quick Start

### Option 1: Docker (Recommended)

**Pull and run from Docker Hub:**

```bash
# Pull image
docker pull your-username/dots-ocr-api:latest

# Run with auto model download
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/weights:/app/weights \
  --name dots-ocr-api \
  your-username/dots-ocr-api:latest

# Check logs (model will download on first run ~5-10 min)
docker logs -f dots-ocr-api
```

**Or build locally:**

```bash
# Clone repository
git clone https://github.com/your-username/dot-ocr.git
cd dot-ocr

# Build
docker build -t dots-ocr-api:latest -f Dockerfile .

# Run
docker run -d -p 8000:8000 -v $(pwd)/weights:/app/weights dots-ocr-api:latest
```

**Access:**
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health

### Option 2: Docker Compose

```bash
# Start API only
docker-compose up -d dots-ocr-api-cpu

# Start API + Web interface
docker-compose --profile web up -d

# For GPU support (requires nvidia-docker)
docker-compose --profile gpu up -d dots-ocr-api-gpu
```

**Access:**
- API: http://localhost:8000
- Web UI: http://localhost:3000

### Option 3: Local Development

#### Step 1: Install Dependencies

```bash
# Install Python dependencies
pip3 install -r requirements.txt
pip3 install -r api_requirements.txt

# Install PyTorch (choose based on your hardware)
# For CPU:
pip3 install torch==2.4.0 torchvision==0.19.0 --index-url https://download.pytorch.org/whl/cpu

# For GPU (CUDA 12.1):
pip3 install torch==2.4.0 torchvision==0.19.0 --index-url https://download.pytorch.org/whl/cu121
```

#### Step 2: Download Model

```bash
# Create weights directory
mkdir -p weights

# Download model (~3.5GB)
python3 << 'EOF'
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='rednote-hilab/DotsOCR',
    local_dir='./weights/DotsOCR',
    local_dir_use_symlinks=False
)
EOF
```

**Or use automated setup script:**

```bash
# Make executable
chmod +x setup.sh

# Run setup
./setup.sh
```

#### Step 3: Run API

```bash
# Start API server
python3 scripts/run_api.py

# Or with custom settings
python3 scripts/run_api.py --host 0.0.0.0 --port 8000 --reload
```

#### Step 4: Run Web Interface (Optional)

```bash
# Open new terminal
cd web
python3 -m http.server 3000
```

**Access:**
- API: http://localhost:8000/docs
- Web: http://localhost:3000

## 📁 Project Structure

```
dot-ocr/
├── api/                      # FastAPI Backend
│   ├── main.py              # App entry point
│   ├── config.py            # Settings & config
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   ├── routers/
│   │   └── process.py       # Unified API endpoint
│   └── services/
│       ├── detector.py      # File type detection
│       ├── converter.py     # DOCX→PDF conversion
│       └── ocr_service.py   # Main OCR logic
│
├── web/                     # Web Interface
│   ├── index.html          # Main page
│   ├── css/style.css       # Styles
│   └── js/
│       ├── api.js          # API client
│       └── app.js          # Main logic
│
├── dots_ocr/                # Core OCR Engine
│   ├── parser.py           # Main parser
│   ├── model/              # Model code
│   └── utils/              # Utilities
│
├── scripts/
│   └── run_api.py          # API launcher
│
├── Dockerfile               # CPU Docker image
├── Dockerfile.gpu           # GPU Docker image
├── docker-compose.yml       # Multi-service setup
├── docker-entrypoint.sh     # Auto model download
│
├── requirements.txt         # Core dependencies
├── api_requirements.txt     # API dependencies
├── requirements-gpu.txt     # GPU dependencies
│
└── .env.example            # Config template
```

## 💡 Usage

### API Usage

#### Upload PDF
```bash
curl -X POST "http://localhost:8000/api/v1/process" \
  -F "file=@document.pdf"
```

#### Upload DOCX (auto-converts)
```bash
curl -X POST "http://localhost:8000/api/v1/process" \
  -F "file=@document.docx" \
  -F "prompt_mode=prompt_layout_all_en"
```

#### Upload Image with Layout Detection Only
```bash
curl -X POST "http://localhost:8000/api/v1/process" \
  -F "file=@invoice.jpg" \
  -F "prompt_mode=prompt_layout_only_en"
```

#### Python Client
```python
import requests

# Upload file
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/process',
        files={'file': f},
        data={'prompt_mode': 'prompt_layout_all_en'}
    )

result = response.json()
print(f"Status: {result['status']}")
print(f"Pages: {result['total_pages']}")
print(f"Markdown:\n{result['markdown_content']}")
```

### Prompt Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `prompt_layout_all_en` | Full layout + OCR (default) | Most cases |
| `prompt_layout_only_en` | Layout detection only | Need positions only |
| `prompt_ocr` | OCR text only | Fast text extraction |
| `prompt_grounding_ocr` | OCR in specific bbox | Specific region |

## 📚 API Documentation

Full API documentation: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

**Key Endpoints:**

- `POST /api/v1/process` - Process document (unified endpoint)
- `GET /api/v1/health` - Health check
- `GET /docs` - Interactive API docs (Swagger UI)

**Response Format:**
```json
{
  "task_id": "uuid",
  "status": "completed",
  "file_type": "pdf",
  "markdown_content": "# Content...",
  "layout_elements": [...],
  "layout_image_url": "/results/uuid/layout_0.jpg",
  "total_pages": 5,
  "processing_time": 12.34,
  "device_used": "cuda"
}
```

## ⚙️ Configuration

### Environment Variables

Create `.env` file from template:

```bash
cp .env.example .env
```

Key settings:

```bash
# Device (auto, cpu, cuda)
DEVICE=auto

# Model path
MODEL_PATH=./weights/DotsOCR

# Server
HOST=0.0.0.0
PORT=8000

# Upload limit (50MB)
MAX_UPLOAD_SIZE=52428800

# DOCX conversion
USE_LIBREOFFICE=false  # true for better quality
```

### Runtime Options

```bash
# Force CPU mode
python scripts/run_api.py --cpu

# Custom port
python scripts/run_api.py --port 8080

# Development mode (auto-reload)
python scripts/run_api.py --reload

# Multiple workers (production)
python scripts/run_api.py --workers 4
```

## 🐳 Deployment

### Deploy to Docker Hub

#### Method 1: Quick Deploy (Interactive)

```powershell
# Windows
.\quick-deploy.ps1
```

```bash
# Linux/Mac
chmod +x docker-build.sh
./docker-build.sh
```

#### Method 2: Manual

```bash
# Login
docker login

# Build & tag
docker build -t your-username/dots-ocr-api:latest -f Dockerfile .
docker build -t your-username/dots-ocr-api:latest-gpu -f Dockerfile.gpu .

# Push
docker push your-username/dots-ocr-api:latest
docker push your-username/dots-ocr-api:latest-gpu
```

### Production Deployment

**Docker Compose (Production):**

```yaml
version: '3.8'
services:
  api:
    image: your-username/dots-ocr-api:latest
    ports:
      - "8000:8000"
    volumes:
      - ./weights:/app/weights
      - ./results:/app/results
    environment:
      - DEVICE=auto
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4'
```

**Cloud Platforms:**

- **AWS ECS**: See [DOCKER_GUIDE.md](DOCKER_GUIDE.md#aws-ecs)
- **Google Cloud Run**: See [DOCKER_GUIDE.md](DOCKER_GUIDE.md#cloud-run-gcp)
- **Azure Container Instances**: See [DOCKER_GUIDE.md](DOCKER_GUIDE.md)

## 🐛 Troubleshooting

### Issue: Model not found

**Solution:**
```bash
# Download model manually
python -c "from huggingface_hub import snapshot_download; snapshot_download('rednote-hilab/DotsOCR', './weights/DotsOCR', local_dir_use_symlinks=False)"
```

### Issue: GPU not detected

**Solution:**
```bash
# Check CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Force CPU if needed
python scripts/run_api.py --cpu
```

### Issue: Port already in use

**Solution:**
```bash
# Use different port
python scripts/run_api.py --port 8080
```

### Issue: Out of memory

**Solution:**
```bash
# Use CPU mode
DEVICE=cpu python scripts/run_api.py

# Or increase Docker memory limit
docker run --memory="8g" ...
```

### Issue: DOCX conversion failed

**Solution:**
```bash
# Install LibreOffice for better conversion
# Ubuntu:
sudo apt-get install libreoffice

# Set in .env:
USE_LIBREOFFICE=true
LIBREOFFICE_PATH=/usr/bin/libreoffice
```

## 📊 Performance

| Hardware | Speed (per page) | Memory |
|----------|------------------|--------|
| **CPU** (Intel i7) | 5-10s | ~8GB RAM |
| **GPU** (NVIDIA) | 1-2s | ~4GB VRAM |

**File Support:**
- **Images**: JPG, PNG, GIF, BMP, WEBP, TIFF
- **Documents**: PDF (multi-page), DOC, DOCX
- **Max Size**: 50MB (configurable)

## 📖 Additional Documentation

- [API Documentation](API_DOCUMENTATION.md) - Complete API reference
- [Web Setup Guide](WEB_SETUP.md) - Web interface setup
- [Docker Guide](DOCKER_GUIDE.md) - Advanced Docker deployment
- [Docker Fix Guide](DOCKER_FIX.md) - Common Docker issues

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - Same as [dots.ocr](https://github.com/rednote-hilab/dots.ocr)

## 🙏 Credits

- **dots.ocr** by [rednote-hilab](https://github.com/rednote-hilab)
- This API & Web extension adds REST API and modern web interface

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/rednote-hilab/dots.ocr/issues)
- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Original Project**: [dots.ocr](https://github.com/rednote-hilab/dots.ocr)

---

**Made with ❤️ for the AI/ML community**

## 🌟 Quick Links

- [🚀 Quick Start](#-quick-start)
- [📖 API Docs](http://localhost:8000/docs)
- [🌐 Web Interface](http://localhost:3000)
- [🐳 Docker Hub](https://hub.docker.com)
