# dots.ocr API Documentation

## Overview

**dots.ocr API** là REST API thông minh để xử lý tài liệu, hỗ trợ:
- ✅ Auto-detect file types (PDF, Image, DOC, DOCX)
- ✅ Auto-convert documents
- ✅ OCR với nhiều prompt modes
- ✅ Layout detection
- ✅ CPU & GPU auto-detection
- ✅ 100+ languages

## Quick Start

### 1. Installation

```bash
# Clone repository
cd c:\Users\admin\Desktop\dot-ocr

# Install API dependencies
pip install -r api_requirements.txt

# Install PyTorch (choose based on your hardware)
# For CPU:
pip install torch==2.4.0 torchvision==0.19.0 --index-url https://download.pytorch.org/whl/cpu

# For GPU (CUDA 12.1):
pip install torch==2.4.0 torchvision==0.19.0 --index-url https://download.pytorch.org/whl/cu121
```

### 2. Download Model Weights

```bash
python tools/download_model.py
```

Model sẽ được lưu tại `./weights/DotsOCR` (khoảng 3-4GB)

### 3. Start API Server

```bash
# Basic
python scripts/run_api.py

# With options
python scripts/run_api.py --host 0.0.0.0 --port 8000

# Force CPU mode
python scripts/run_api.py --cpu

# Development mode (auto-reload)
python scripts/run_api.py --reload
```

Server sẽ chạy tại: **http://localhost:8000**

API Docs tại: **http://localhost:8000/docs**

## API Endpoints

### 1. Process Document (Unified Endpoint)

**POST** `/api/v1/process`

Upload và xử lý bất kỳ loại tài liệu nào. API tự động:
- Nhận diện loại file
- Convert DOC/DOCX → PDF nếu cần
- Thực hiện OCR

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | ✅ Yes | File để xử lý (PDF, JPG, PNG, DOCX, DOC) |
| `prompt_mode` | String | No | Chế độ xử lý (mặc định: `prompt_layout_all_en`) |
| `fitz_preprocess` | Boolean | No | Enable fitz preprocessing cho images (mặc định: `true`) |
| `bbox` | String | No | Bounding box cho grounding OCR (format: `x1,y1,x2,y2`) |

#### Prompt Modes

| Mode | Description |
|------|-------------|
| `prompt_layout_all_en` | **Full** - Layout detection + OCR (mặc định) |
| `prompt_layout_only_en` | **Layout Only** - Chỉ detect layout elements |
| `prompt_ocr` | **OCR Only** - Chỉ extract text |
| `prompt_grounding_ocr` | **Grounding** - OCR trong bbox cụ thể |

#### Example Requests

**cURL:**
```bash
# Basic - Full OCR
curl -X POST "http://localhost:8000/api/v1/process" \
  -F "file=@document.pdf" \
  -F "prompt_mode=prompt_layout_all_en"

# Layout detection only
curl -X POST "http://localhost:8000/api/v1/process" \
  -F "file=@document.pdf" \
  -F "prompt_mode=prompt_layout_only_en"

# OCR with specific bbox
curl -X POST "http://localhost:8000/api/v1/process" \
  -F "file=@image.jpg" \
  -F "prompt_mode=prompt_grounding_ocr" \
  -F "bbox=100,200,500,600"

# DOCX file (auto-convert to PDF)
curl -X POST "http://localhost:8000/api/v1/process" \
  -F "file=@document.docx"
```

**Python:**
```python
import requests

# Upload file
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/process',
        files={'file': f},
        data={
            'prompt_mode': 'prompt_layout_all_en',
            'fitz_preprocess': True
        }
    )

result = response.json()
print(result)
```

**JavaScript:**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('prompt_mode', 'prompt_layout_all_en');

const response = await fetch('http://localhost:8000/api/v1/process', {
    method: 'POST',
    body: formData
});

const result = await response.json();
console.log(result);
```

#### Response

```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "file_type": "pdf",
  "original_filename": "document.pdf",
  "message": "Successfully processed 5 pages",
  
  "markdown_content": "# Title\n\nContent...",
  "layout_elements": [
    {
      "bbox": [100, 200, 500, 300],
      "category": "Text",
      "text": "Sample text"
    }
  ],
  
  "layout_image_url": "/results/a1b2c3d4/layout_image_0.jpg",
  "json_url": "/results/a1b2c3d4/layout_info_0.json",
  "markdown_url": "/results/a1b2c3d4/md_content_0.md",
  
  "total_pages": 5,
  "processing_time": 12.34,
  "device_used": "cuda",
  
  "created_at": "2025-11-27T23:00:00",
  "completed_at": "2025-11-27T23:00:12"
}
```

### 2. Health Check

**GET** `/api/v1/health`

Kiểm tra trạng thái API server.

#### Response

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "device": "cuda",
  "gpu_available": true,
  "model_loaded": true,
  "timestamp": 1701234567.89
}
```

## Response Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid parameters) |
| 413 | Payload Too Large (file > 50MB) |
| 500 | Internal Server Error |

## File Type Support

### Supported Formats

| Format | Extensions | Notes |
|--------|-----------|-------|
| **Images** | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.tiff` | Direct OCR |
| **PDF** | `.pdf` | Direct OCR, multi-page support |
| **Word** | `.docx`, `.doc` | Auto-convert to PDF then OCR |

### Auto-Conversion

Khi upload file DOCX/DOC:
1. API tự động detect loại file
2. Convert DOCX → PDF (sử dụng `python-docx` hoặc LibreOffice)
3. Thực hiện OCR trên PDF

## Layout Categories

API có thể phát hiện các loại layout sau:

- `Text` - Văn bản thông thường
- `Title` - Tiêu đề
- `Section-header` - Đầu mục
- `List-item` - Danh sách
- `Table` - Bảng (output HTML)
- `Formula` - Công thức toán học (output LaTeX)
- `Picture` - Hình ảnh
- `Caption` - Chú thích
- `Footnote` - Chú thích chân trang
- `Page-header` - Đầu trang
- `Page-footer` - Chân trang

## Performance

### Processing Speed

| Hardware | Speed (approx) |
|----------|----------------|
| **CPU** | 5-10s per page |
| **GPU (CUDA)** | 1-2s per page |

### Resource Usage

- **Model Size**: ~3.5GB
- **Memory (CPU)**: ~8GB RAM
- **Memory (GPU)**: ~4GB VRAM

## Configuration

### Environment Variables

Tạo file `.env` từ `.env.example`:

```bash
cp .env.example .env
```

Key configurations:

```bash
# Device (auto, cpu, cuda)
DEVICE=auto

# Model path
MODEL_PATH=./weights/DotsOCR

# Upload limits
MAX_UPLOAD_SIZE=52428800  # 50MB

# Document conversion
USE_LIBREOFFICE=false
```

## Error Handling

### Common Errors

**File too large:**
```json
{
  "error": "File too large. Max size: 50MB"
}
```

**Unsupported file type:**
```json
{
  "error": "Unsupported file type: .xyz"
}
```

**Processing failed:**
```json
{
  "status": "failed",
  "error": "OCR processing failed",
  "traceback": "..."
}
```

## Best Practices

1. **File Size**: Giữ file dưới 50MB để tốc độ xử lý tối ưu
2. **Image Quality**: DPI >= 200 cho kết quả tốt nhất
3. **Prompt Mode**: Chọn prompt phù hợp với nhu cầu:
   - `prompt_layout_all_en` - Khi cần cả layout và text
   - `prompt_layout_only_en` - Khi chỉ cần vị trí elements
   - `prompt_ocr` - Khi chỉ cần extract text nhanh
4. **Batch Processing**: Xử lý từng file riêng lẻ, không gộp PDF

## Examples

### Process PDF Document

```python
import requests

response = requests.post(
    'http://localhost:8000/api/v1/process',
    files={'file': open('report.pdf', 'rb')},
    data={'prompt_mode': 'prompt_layout_all_en'}
)

result = response.json()
print(f"Processed {result['total_pages']} pages")
print(f"Markdown: {result['markdown_content'][:100]}...")
```

### Process Image with Layout Detection

```python
response = requests.post(
    'http://localhost:8000/api/v1/process',
    files={'file': open('invoice.jpg', 'rb')},
    data={'prompt_mode': 'prompt_layout_all_en'}
)

result = response.json()

# Get layout elements
for elem in result['layout_elements']:
    print(f"{elem['category']}: {elem['text'][:50]}...")
```

### Process DOCX (Auto-Convert)

```python
# API tự động convert DOCX → PDF → OCR
response = requests.post(
    'http://localhost:8000/api/v1/process',
    files={'file': open('document.docx', 'rb')}
)

result = response.json()
print(f"File type: {result['file_type']}")  # Will show 'pdf'
print(f"Markdown: {result['markdown_content']}")
```

## License

MIT License - See LICENSE file for details.

## Support

- **GitHub**: https://github.com/rednote-hilab/dots.ocr
- **Issues**: https://github.com/rednote-hilab/dots.ocr/issues
- **API Docs**: http://localhost:8000/docs
