# Quick Fix Guide for Docker Build Errors

## ✅ Fixed: flash-attn Error

**Problem:** `flash-attn` requires CUDA but CPU-only Docker image doesn't have it.

**Solution:** Created separate requirements files:

### For CPU Build (Dockerfile):
```bash
docker build -t your-username/dots-ocr-api:latest-cpu -f Dockerfile .
```
Uses: `requirements.txt` (without flash-attn)

### For GPU Build (Dockerfile.gpu):
```bash
docker build -t your-username/dots-ocr-api:latest-gpu -f Dockerfile.gpu .
```
Uses: `requirements-gpu.txt` (with flash-attn)

## 🚀 Now you can build:

```bash
# Login
docker login

# Build CPU version (recommended)
docker build -t your-username/dots-ocr-api:latest -f Dockerfile .

# Or build GPU version (if you have CUDA)
docker build -t your-username/dots-ocr-api:latest-gpu -f Dockerfile.gpu .

# Push to Docker Hub
docker push your-username/dots-ocr-api:latest
```

## 📝 Files Changed:

- `requirements.txt` - Removed flash-attn (CPU compatible)
- `requirements-gpu.txt` - NEW, includes flash-attn
- `Dockerfile.gpu` - Updated to use requirements-gpu.txt

## ✅ Test Build Locally:

```bash
# Quick test (without push)
docker build -t test-dots-ocr -f Dockerfile .

# If successful, you should see:
# Successfully built...
# Successfully tagged test-dots-ocr:latest
```
