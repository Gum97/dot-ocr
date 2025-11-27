# 🚀 Quick Start Guide - dots.ocr API

3 cách để chạy dots.ocr API dễ nhất:

## 📦 Method 1: Docker từ Docker Hub (EASIEST)

```bash
# Bước 1: Pull image
docker pull your-username/dots-ocr-api:latest

# Bước 2: Run (model sẽ tự download lần đầu ~5-10 phút)
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/weights:/app/weights \
  --name dots-ocr-api \
  your-username/dots-ocr-api:latest

# Bước 3: Check logs
docker logs -f dots-ocr-api

# Bước 4: Truy cập
# API: http://localhost:8000/docs
```

**✅ Xong! API đã chạy.**

---

## 🐳 Method 2: Docker Compose (API + Web)

```bash
# Bước 1: Clone repo
git clone https://github.com/your-username/dot-ocr.git
cd dot-ocr

# Bước 2: Start cả API + Web
docker-compose --profile web up -d

# Bước 3: Truy cập
# API: http://localhost:8000/docs
# Web: http://localhost:3000
```

**✅ Xong! Có cả Web Interface.**

---

## 💻 Method 3: Local Development

```bash
# Bước 1: Install dependencies (Ubuntu/Linux)
pip3 install -r requirements.txt
pip3 install -r api_requirements.txt
pip3 install torch==2.4.0 torchvision==0.19.0 --index-url https://download.pytorch.org/whl/cpu

# Bước 2: Download model (automated script)
chmod +x setup.sh
./setup.sh

# OR manual download:
mkdir -p weights
python3 << 'EOF'
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='rednote-hilab/DotsOCR',
    local_dir='./weights/DotsOCR',
    local_dir_use_symlinks=False
)
EOF

# Bước 3: Run API
python3 scripts/run_api.py

# Bước 4 (Optional): Run Web
cd web && python3 -m http.server 3000
```

**✅ Xong! Chạy local.**

---

## 🧪 Test API

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Upload PDF
curl -X POST "http://localhost:8000/api/v1/process" \
  -F "file=@test.pdf"

# Upload DOCX (auto-convert)
curl -X POST "http://localhost:8000/api/v1/process" \
  -F "file=@document.docx"
```

---

## 🎯 Quick Commands

```bash
# Build Docker locally
docker build -t dots-ocr-api -f Dockerfile .

# Run with GPU
docker run --gpus all -p 8000:8000 dots-ocr-api:latest-gpu

# Stop
docker stop dots-ocr-api

# Remove
docker rm dots-ocr-api

# View logs
docker logs -f dots-ocr-api
```

---

## 📚 More Info

- **Full README**: [README.md](README.md)
- **API Docs**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Web Setup**: [WEB_SETUP.md](WEB_SETUP.md)
- **Docker Guide**: [DOCKER_GUIDE.md](DOCKER_GUIDE.md)

---

**Need help? Check [README.md](README.md) or [Troubleshooting](#troubleshooting)**
