# Web Interface Setup Guide

## Overview

Web interface hiện đại cho dots.ocr API với các tính năng:
- 📤 Drag & drop upload
- 🎨 Beautiful UI với animations
- 📱 Responsive design
- 🔄 Real-time progress tracking
- 📊 Multiple result views (Markdown, Layout, JSON)

## Prerequisites

- API Server đang chạy tại `http://localhost:8000`
- Web browser hiện đại (Chrome, Firefox, Edge, Safari)

## Quick Start

### Method 1: Simple HTTP Server (Recommended)

```bash
cd c:\Users\admin\Desktop\dot-ocr\web

# Python 3
python -m http.server 3000

# Hoặc sử dụng live-server (nếu đã cài Node.js)
npx live-server --port=3000
```

Truy cập: **http://localhost:3000**

### Method 2: Direct File Open

Bạn cũng có thể mở trực tiếp file `index.html` trong browser, nhưng một số tính năng có thể không hoạt động do CORS.

## File Structure

```
web/
├── index.html          # Main HTML file
├── css/
│   └── style.css       # Styles with animations
└── js/
    ├── api.js          # API client wrapper
    └── app.js          # Main application logic
```

## Features

### 1. File Upload

**Supported methods:**
- Click "Chọn file" button
- Drag and drop files vào upload area
- Paste từ clipboard (sẽ implement sau)

**Supported file types:**
- Images: JPG, PNG, GIF, BMP, WEBP, TIFF
- Documents: PDF, DOC, DOCX

**Size limit:** 50MB

### 2. Processing Options

#### Prompt Modes

- **Full Layout + OCR** (`prompt_layout_all_en`)
  - Phát hiện layout và extract text
  - Sử dụng cho hầu hết trường hợp

- **Layout Detection Only** (`prompt_layout_only_en`)
  - Chỉ phát hiện vị trí các elements
  - Nhanh hơn, không extract text

- **OCR Text Only** (`prompt_ocr`)
  - Chỉ extract text, không detect layout
  - Nhanh nhất

- **Grounding OCR** (`prompt_grounding_ocr`)
  - OCR trong bounding box cụ thể
  - Yêu cầu bbox parameter (x1,y1,x2,y2)

#### Other Options

- **Fitz Preprocess**: Xử lý image qua PDF pipeline (recommended cho images có DPI thấp)
- **Bounding Box**: Chỉ định vùng cần OCR (chỉ cho grounding mode)

### 3. Results Display

Kết quả hiển thị trong 3 tabs:

#### Tab 1: Markdown
- Rendered markdown preview
- Hỗ trợ LaTeX formulas
- Formatted tables

#### Tab 2: Layout
- Visualization của layout detection
- Bounding boxes vẽ trên image
- Color-coded categories

#### Tab 3: JSON
- Raw JSON data của layout elements
- Syntax highlighting
- Copy-friendly format

### 4. Download Results

Click "Tải kết quả" để download:
- Markdown file (.md)
- JSON file (.json)
- Layout image (.jpg)

## Configuration

### API Base URL

Mặc định API URL là `http://localhost:8000`. Để thay đổi, sửa trong `js/api.js`:

```javascript
const api = new DotsOCRAPI('http://your-api-server:8000');
```

### Styling

Customize colors trong `css/style.css`:

```css
:root {
    --primary: #FF576D;
    --primary-dark: #F72C49;
    --secondary: #4A90E2;
    /* ... */
}
```

## Troubleshooting

### Problem: Cannot connect to API

**Solution:**
1. Kiểm tra API server đang chạy:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

2. Kiểm tra CORS settings trong `api/main.py`:
   ```python
   allow_origins=["*"]  # Allow all origins
   ```

### Problem: File upload failed

**Solution:**
- Check file size < 50MB
- Check file extension được support
- Check console log để xem error message

### Problem: Results not displaying

**Solution:**
- Open browser DevTools (F12)
- Check Console tab for JavaScript errors
- Check Network tab to see API responses

## Development

### Hot Reload

Sử dụng live-server cho auto-reload khi edit code:

```bash
npm install -g live-server
cd web
live-server --port=3000
```

### Debugging

Enable debug mode bằng cách mở browser console (F12) và xem:
- API requests/responses
- Error messages
- Processing status

### Custom Themes

Tạo theme riêng bằng cách:

1. Copy `style.css` → `style-dark.css`
2. Thay đổi color variables
3. Link vào HTML:
   ```html
   <link rel="stylesheet" href="css/style-dark.css">
   ```

## Browser Compatibility

Tested on:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Edge 90+
- ✅ Safari 14+

## Performance Tips

1. **Large Files**: 
   - Files > 10MB có thể mất nhiều thời gian
   - Consider splitting PDF thành nhiều files nhỏ

2. **Batch Processing**:
   - Hiện tại chỉ support 1 file tại 1 thời điểm
   - Để xử lý nhiều files, upload lần lượt

3. **Caching**:
   - Kết quả được cache trên server
   - Clear cache bằng cách restart API server

## Advanced Features (Coming Soon)

- 🔄 Batch upload multiple files
- 💾 Local storage for history
- 🌙 Dark mode
- 📤 Export to multiple formats
- 🔐 Authentication
- 📊 Processing statistics

## Deployment

### Production Deployment

1. Build optimized version (optional):
   ```bash
   # Minify CSS and JS
   npm install -g clean-css-cli uglify-js
   
   cleancss -o css/style.min.css css/style.css
   uglifyjs js/api.js js/app.js -o js/app.min.js
   ```

2. Update HTML to use minified files

3. Serve with production web server:
   - Nginx
   - Apache
   - Caddy

### Example Nginx Config

```nginx
server {
    listen 80;
    server_name dots-ocr.example.com;
    
    root /path/to/web;
    index index.html;
    
    # API proxy
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /results/ {
        proxy_pass http://localhost:8000/results/;
    }
}
```

## License

MIT License - Same as dots.ocr project.
