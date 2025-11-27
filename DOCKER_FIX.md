# Model Download Issue - FIXED

## Problem

Model weights không được tìm thấy trong Docker container:
```
HFValidationError: Repo id must be in the form 'repo_name' or 'namespace/repo_name': './weights/DotsOCR'
```

## Solution

Tạo entrypoint script tự động download model nếu chưa có.

## 🚀 How to Use

### Option 1: Auto-download (Slow first run)

```bash
# Run container - model will download automatically on first run (~5-10 mins)
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/weights:/app/weights \
  --name dots-ocr-api \
  your-username/dots-ocr-api:latest

# Check logs
docker logs -f dots-ocr-api
```

Lần đầu chạy sẽ mất ~5-10 phút để download model (3.5GB). Những lần sau sẽ nhanh vì model đã được lưu trong volume.

### Option 2: Pre-download (Faster)

```bash
# Download model trước
mkdir -p weights
python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='rednote-hilab/DotsOCR',
    local_dir='./weights/DotsOCR',
    local_dir_use_symlinks=False
)
"

# Run container với model đã download
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/weights:/app/weights \
  --name dots-ocr-api \
  your-username/dots-ocr-api:latest
```

## Files Changed

1. **`docker-entrypoint.sh`** - Auto-download script
2. **`Dockerfile`** - Added entrypoint
3. **`Dockerfile.gpu`** - Added entrypoint

## Build & Push

```bash
# Build
docker build -t your-username/dots-ocr-api:latest -f Dockerfile .

# Push
docker push your-username/dots-ocr-api:latest
```

## Important Notes

- **Volume mount**: `-v $(pwd)/weights:/app/weights` giữ model persist
- **First run**: Có thể mất 5-10 phút để download
- **Subsequent runs**: Nhanh vì model đã có
- **Download progress**: Check logs với `docker logs -f container-name`

## Verify

```bash
# Check if API is ready
curl http://localhost:8000/api/v1/health

# Should return:
# {"status":"healthy","model_loaded":true,...}
```
