#!/bin/bash
# Docker entrypoint script - downloads model if not present

set -e

MODEL_DIR="/app/weights/DotsOCR"

echo "========================================="
echo "dots.ocr API Container Starting..."
echo "========================================="

# Check if model exists
if [ ! -d "$MODEL_DIR" ] || [ -z "$(ls -A $MODEL_DIR)" ]; then
    echo "Model not found in $MODEL_DIR"
    echo "Downloading model from HuggingFace Hub..."
    echo "This will take ~5-10 minutes (3.5GB download)..."
    
    python3 -c "
from huggingface_hub import snapshot_download
import os

model_id = 'rednote-hilab/DotsOCR'
local_dir = '/app/weights/DotsOCR'

print(f'Downloading {model_id} to {local_dir}...')
snapshot_download(
    repo_id=model_id,
    local_dir=local_dir,
    local_dir_use_symlinks=False
)
print('Model downloaded successfully!')
"
else
    echo "Model found at $MODEL_DIR ✓"
fi

echo "========================================="
echo "Starting API server..."
echo "========================================="

# Execute the main command
exec "$@"
