# Model Download Issues - Solutions

## ❌ Issue: Repository Not Found / 401 Unauthorized

```
RepositoryNotFoundError: 401 Client Error
Repository Not Found for url: https://huggingface.co/api/models/rednote-hilab/DotsOCR/revision/main
```

## ✅ Solutions:

### Option 1: Use Correct Repo Name

The repository might be named `dots.ocr` instead of `DotsOCR`:

```bash
python3 << 'EOF'
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='rednote-hilab/dots.ocr',  # Note: dots.ocr not DotsOCR
    local_dir='./weights/DotsOCR',
    local_dir_use_symlinks=False
)
EOF
```

### Option 2: HuggingFace Login (If Gated)

If model requires authentication:

```bash
# Install huggingface-cli
pip3 install --upgrade huggingface_hub

# Login
huggingface-cli login

# Then download
python3 << 'EOF'
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='rednote-hilab/dots.ocr',
    local_dir='./weights/DotsOCR',
    use_auth_token=True
)
EOF
```

### Option 3: Manual Download

1. Visit https://huggingface.co/rednote-hilab/dots.ocr
2. Click "Files and versions"
3. Download all files to `./weights/DotsOCR/`

### Option 4: Use ModelScope (China mirror)

```bash
python3 << 'EOF'
from modelscope import snapshot_download
snapshot_download(
    'rednote-hilab/DotsOCR',
    cache_dir='./weights'
)
EOF
```

### Option 5: Skip Model Download (Run without)

If you have issues downloading:

1. Comment out model download in `setup.sh`
2. Run API - it will show error but container starts
3. Download model manually later and restart

```bash
# Skip model for now
# Model will be downloaded on first API call (if auto-download enabled in entrypoint)
```

## 📝 Check Repository Existence

```bash
# Check if repo exists
curl https://huggingface.co/api/models/rednote-hilab/dots.ocr

# If 404, try:
curl https://huggingface.co/api/models/rednote-hilab/DotsOCR
```

## 🔧 For Docker Users

Docker entrypoint will handle this automatically. If model download fails in Docker:

```bash
# Run without model
docker run -d -p 8000:8000 --name dots-ocr-api dots-ocr-api:latest

# Download manually into container
docker exec -it dots-ocr-api bash
cd /app/weights
# Download manually here

# Or mount pre-downloaded weights
docker run -d -p 8000:8000 -v /path/to/weights:/app/weights dots-ocr-api:latest
```

## ⚠️ Note

The model repository might be:
- Private/gated (requires HF account)
- Renamed or moved
- Behind agreement (need to accept license)

Check the original dots.ocr README for latest download instructions.
