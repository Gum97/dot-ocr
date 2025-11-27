#!/bin/bash
# Setup script for dots.ocr API - Ubuntu/Linux

set -e

echo "======================================"
echo "dots.ocr API Setup"
echo "======================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found. Please install Python 3.10+"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip3 install -r requirements.txt
pip3 install -r api_requirements.txt

echo "✓ Dependencies installed"

# Install PyTorch
echo ""
echo "Installing PyTorch (CPU version)..."
pip3 install torch==2.4.0 torchvision==0.19.0 --index-url https://download.pytorch.org/whl/cpu

echo "✓ PyTorch installed"

# Download model
echo ""
echo "Downloading model weights (~3.5GB, this may take 5-10 minutes)..."
mkdir -p weights

python3 << 'EOF'
from huggingface_hub import snapshot_download

print("Downloading model from HuggingFace Hub...")
snapshot_download(
    repo_id='rednote-hilab/DotsOCR',
    local_dir='./weights/DotsOCR',
    local_dir_use_symlinks=False
)
print("✓ Model downloaded successfully!")
EOF

echo ""
echo "======================================"
echo "✅ Setup completed!"
echo "======================================"
echo ""
echo "To start the API server:"
echo "  python3 scripts/run_api.py"
echo ""
echo "Then visit: http://localhost:8000/docs"
