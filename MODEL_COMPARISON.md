# dots.ocr vs dots.ocr.base - So sánh

## 📊 Tổng quan

| Feature | dots.ocr | dots.ocr.base |
|---------|----------|---------------|
| **Likes** | 1.14k ⭐ | 9 ⭐ |
| **Popularity** | Cao (official release) | Thấp (base model) |
| **Model Type** | Full model | Base model |
| **Status** | Main/Recommended | Development/Base |

## 🔍 Phân tích chi tiết

### `rednote-hilab/dots.ocr` ✅ RECOMMENDED

**Đây là bản CHÍNH THỨC và được khuyến nghị sử dụng.**

**Đặc điểm:**
- ✅ **Full model** - đã train đầy đủ
- ✅ **Production ready** - sẵn sàng cho production
- ✅ **1.14k likes** - được cộng đồng tin dùng
- ✅ **Optimized** - đã optimize cho inference
- ✅ **Complete weights** - có đầy đủ checkpoint

**Use cases:**
- Production deployment
- API services
- Real applications
- Best performance

### `rednote-hilab/dots.ocr.base` ⚠️ BASE MODEL

**Đây là bản BASE MODEL - chỉ dùng cho development/fine-tuning.**

**Đặc điểm:**
- ⚠️ **Base checkpoint** - chưa hoàn chỉnh
- ⚠️ **For fine-tuning** - dùng để fine-tune
- ⚠️ **9 likes** - ít người dùng
- ⚠️ **May lack optimization** - có thể chưa optimize
- ⚠️ **Development only** - chỉ cho dev

**Use cases:**
- Research
- Fine-tuning on custom data
- Model development
- Experimentation

## 🎯 Nên dùng cái nào?

### ✅ Dùng `dots.ocr` nếu:
- Bạn muốn **deploy production**
- Cần **performance tốt nhất**
- Muốn model **ổn định**
- Làm **API/service** real-world

### ⚠️ Dùng `dots.ocr.base` nếu:
- Bạn muốn **fine-tune** model
- Làm **research**
- Cần **customize** model
- **Experiment** với architecture

## 💡 Recommendation

**Cho dự án của bạn (API + Web):**

```python
# ✅ SỬ DỤNG:
repo_id = 'rednote-hilab/dots.ocr'  # Main model - RECOMMENDED

# ❌ KHÔNG DÙNG (trừ khi fine-tuning):
repo_id = 'rednote-hilab/dots.ocr.base'  # Base model - For research only
```

## 📝 Update code

Đảm bảo bạn dùng model chính:

```bash
# setup.sh - Đã update
python3 << 'EOF'
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='rednote-hilab/dots.ocr',  # ✅ Correct - Main model
    local_dir='./weights/DotsOCR',
    local_dir_use_symlinks=False
)
EOF
```

## 🔐 Download

Cả 2 model đều public, nhưng có thể cần HuggingFace login:

```bash
# Login HuggingFace (nếu cần)
pip3 install --upgrade huggingface_hub
huggingface-cli login

# Download main model
python3 << 'EOF'
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='rednote-hilab/dots.ocr',
    local_dir='./weights/DotsOCR',
    use_auth_token=True  # Nếu cần authentication
)
EOF
```

## ✅ Kết luận

**Cho production API của bạn:**
- ✅ Dùng: `rednote-hilab/dots.ocr` (main model)
- ❌ Không dùng: `rednote-hilab/dots.ocr.base` (base model)

Code đã được update đúng trong `setup.sh` và các file config! 🎉
