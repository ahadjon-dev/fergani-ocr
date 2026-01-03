# LLM OCR Updates - January 3, 2026

## Issues Fixed

### 1. ✅ Hugging Face API Endpoint Update

**Problem:** API returned 410 error - old endpoint deprecated

```
"error": "API request failed with status 410: https://api-inference.huggingface.co is no longer supported"
```

**Solution:** Updated to new router endpoint

- **Old:** `https://api-inference.huggingface.co/models/{model}`
- **New:** `https://router.huggingface.co/models/{model}`

**File changed:** `llm_ocr/services.py` line 43

---

### 2. ✅ PDF Support Added

**Problem:** Could not extract text from PDF files using LLM OCR

**Solution:** Added PDF support with automatic conversion

- PDFs are now detected by file extension
- First page is converted to image using `pdf2image`
- Image is then processed by vision-language model
- Works with all 4 models: DeepSeek, Qwen, LLaVA, Phi-3

**Files changed:**

- `llm_ocr/serializers.py` - Changed `ImageField` to `FileField` to accept PDFs
- `llm_ocr/views.py` - Added PDF detection and conversion logic

**New features:**

- Accepts: PNG, JPG, JPEG, PDF files
- Returns `file_type` field in response (`'image'` or `'pdf'`)
- Graceful error handling for PDF processing failures

---

## Usage Examples

### Extract from Image

```bash
curl -X POST http://localhost:8001/api/v1/llm-ocr/extract/ \
  -F "image=@document.png" \
  -F "model=deepseek-vision" \
  -F "language=eng"
```

### Extract from PDF (NEW!)

```bash
curl -X POST http://localhost:8001/api/v1/llm-ocr/extract/ \
  -F "image=@document.pdf" \
  -F "model=qwen-vision" \
  -F "language=eng"
```

### Response Format

```json
{
  "success": true,
  "text": "Extracted text from the document...",
  "model": "deepseek-ai/deepseek-vl-7b-chat",
  "language": "eng",
  "processing_time": 2.34,
  "file_type": "pdf"
}
```

---

## Testing

Test the updated endpoint:

```bash
# Start server
python manage.py runserver 8001

# Test with image
curl -X POST http://localhost:8001/api/v1/llm-ocr/extract/ \
  -F "image=@test.png" -F "model=deepseek-vision"

# Test with PDF
curl -X POST http://localhost:8001/api/v1/llm-ocr/extract/ \
  -F "image=@test.pdf" -F "model=deepseek-vision"
```

---

## Requirements

- `pdf2image>=1.16.0` (already in requirements.txt)
- `poppler-utils` system package for PDF support

**Installation on Linux:**

```bash
sudo apt-get install poppler-utils
```

---

## Notes

- ✅ API endpoint updated to comply with Hugging Face changes
- ✅ PDF support added for all LLM models
- ✅ Backward compatible - all existing image functionality works
- ✅ No breaking changes to API interface
- 🔄 Only processes first page of PDF (multi-page support can be added later)
