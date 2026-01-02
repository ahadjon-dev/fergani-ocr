# Fergani OCR Project

A production-ready Django REST API application for extracting text from images and PDF files using Tesseract OCR with intelligent caching, database persistence, and comprehensive audit logging.

> **🚀 Ready to deploy?** Check out [QUICK_DEPLOY.md](QUICK_DEPLOY.md) for a 5-minute deployment guide to Railway or Render!

## Features

### Core Functionality

- 🖼️ **Image OCR**: Extract text from PNG, JPEG, TIFF, BMP, GIF, WebP images
- 📄 **PDF Processing**: Extract text from both text-based and scanned PDFs
- 🔍 **Smart Detection**: Automatically detects if PDF is text-based or scanned
- 📑 **Page Selection**: Extract specific pages from PDFs
- 🌍 **Multi-language Support**: 100+ languages including English, Arabic, Chinese, Japanese, etc.

### Advanced Features

- 💾 **Database Persistence**: Optional document and result storage
- ⚡ **Intelligent Caching**: SHA256-based duplicate detection and result caching
- 📊 **Processing Metrics**: Track processing time, confidence scores, word/character counts
- 🔐 **UUID Public IDs**: Secure document identification without enumeration risks
- �️ **Soft Delete**: Data retention with archival capabilities
- 📝 **Audit Logging**: Comprehensive processing logs with structured JSON details
- 🎯 **Service Layer**: Clean separation of concerns with business logic in services
- 🧪 **Comprehensive Testing**: 44+ integration and unit tests

### User Interface & API

- 🎨 **Beautiful UI**: Modern, responsive frontend with gradient design
- 📋 **Copy to Clipboard**: Easy one-click copy of extracted text
- 🔌 **REST API**: Clean REST API endpoints for integration
- 🔄 **Multi-format Support**: Auto-detects file type (image or PDF)
- ⚙️ **Configurable Storage**: Control database saving via API parameter

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Testing](#testing)
- [CI/CD Pipeline](#cicd-pipeline)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

- Python 3.8+
- Tesseract OCR

### Install Tesseract OCR

**Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-ara  # For Arabic support
```

**macOS:**

```bash
brew install tesseract
```

**Windows:**
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

### Install Language Packs (Optional)

For additional language support:

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr-ara  # Arabic
sudo apt-get install tesseract-ocr-chi-sim  # Chinese Simplified
sudo apt-get install tesseract-ocr-jpn  # Japanese
sudo apt-get install tesseract-ocr-rus  # Russian
sudo apt-get install tesseract-ocr-spa  # Spanish
sudo apt-get install tesseract-ocr-fra  # French

# List all available language packs
apt-cache search tesseract-ocr-
```

## Quick Start

### Installation

1. Clone the repository

```bash
cd /home/ahadjon/work/fergani/fergani-ocr
```

2. Install Python dependencies

```bash
pip install -r requirements.txt
```

3. Run migrations

```bash
cd fergani
python manage.py migrate
```

4. Create a superuser (optional, for admin panel access)

```bash
python manage.py createsuperuser
```

5. Start the development server

```bash
python manage.py runserver 8001
```

6. Access the application:

- **Web UI**: http://127.0.0.1:8001
- **API Root**: http://127.0.0.1:8001/api/
- **Admin Panel**: http://127.0.0.1:8001/admin/

## Architecture

### Overview

The project follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                   Views Layer (HTTP)                     │
│  - Request/Response handling                             │
│  - Validation with DRF serializers                       │
│  - Error handling and formatting                         │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                 Service Layer (Business Logic)           │
│  - OCRService: Image processing logic                    │
│  - PDFService: PDF extraction logic                      │
│  - MultiFormatService: Multi-format handling             │
│  - Database persistence and caching                      │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              Utility Layer (Core Processing)             │
│  - OCRProcessor: Tesseract integration                   │
│  - PDFProcessor: PDF text extraction                     │
│  - Image preprocessing and optimization                  │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  Data Layer (Models)                     │
│  - OCRDocument: File storage and metadata                │
│  - OCRResult: Extraction results                         │
│  - PDFPageResult: Per-page PDF results                   │
│  - OCRProcessingLog: Audit trail                         │
└─────────────────────────────────────────────────────────┘
```

### Design Patterns

#### Service Layer Pattern

Business logic is encapsulated in service classes (`ocr/services.py`):

- **OCRService**: Handles image OCR processing
- **PDFService**: Handles PDF text extraction
- **MultiFormatService**: Auto-detects and processes multiple formats

Benefits:

- Views remain thin and focused on HTTP concerns
- Business logic is reusable and testable
- Easy to add features without modifying views

#### Repository Pattern (via Django ORM)

Database operations are abstracted through Django models:

- Clean query interface
- Built-in validation
- Automatic migration management

#### Caching Strategy

SHA256-based file hashing for intelligent caching:

- Duplicate files return cached results instantly
- Saves processing time and resources
- Configurable per-request via `save_to_db` parameter

### Class-Based Views (APIView)

The project uses Django REST Framework's `APIView` for better customization:

**OCRExtractTextView** (`/api/ocr/extract/`)

- POST: Process image and extract text
- GET: Return API information
- Delegates to `OCRService.process_image_extraction()`

**PDFExtractTextView** (`/api/pdf/extract/`)

- POST: Process PDF and extract text
- GET: Return API information
- Delegates to `PDFService.process_pdf_extraction()`

**MultiFormatExtractView** (`/api/extract/`)

- POST: Auto-detect format and extract text
- GET: Return API information
- Delegates to `MultiFormatService.process_file()`

**OCRHealthCheckView** (`/api/ocr/health/`)

- GET: Check service health and Tesseract installation

**SupportedLanguagesView** (`/api/ocr/languages/`)

- GET: List all supported OCR languages

## API Documentation

### Base URL

```
http://127.0.0.1:8001/api/
```

### 1. Extract Text from Image

**Endpoint:** `POST /api/ocr/extract/`

**Description:** Extract text from uploaded image using Tesseract OCR with optional database persistence

**Request:**

- Method: POST
- Content-Type: multipart/form-data
- Body:
  - `image`: Image file (PNG, JPEG, TIFF, BMP, GIF, WebP) - **Required**
  - `language`: Language code (default: 'eng') - **Optional**
  - `save_to_db`: Save to database (default: true, accepts: true/false/1/0/yes/no) - **Optional**

**Response:**

```json
{
  "success": true,
  "text": "Extracted text content...",
  "filename": "example.png",
  "file_size": 123456,
  "image_dimensions": "800x600",
  "image_format": "PNG",
  "language": "eng",
  "character_count": 150,
  "word_count": 25,
  "processing_time_ms": 245,
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "cached": false,
  "confidence": {
    "average_confidence": 92.5,
    "min_confidence": 85,
    "max_confidence": 98,
    "total_words": 25
  }
}
```

**Response Fields:**

- `document_id`: UUID of the saved document (only if `save_to_db=true`)
- `cached`: Whether result was returned from cache (duplicate file)
- `processing_time_ms`: Time taken to process in milliseconds
- `confidence`: OCR confidence scores (if available)

**Example using cURL:**

```bash
# With database saving (default)
curl -X POST http://127.0.0.1:8001/api/ocr/extract/ \
  -F "image=@/path/to/image.png" \
  -F "language=eng"

# Without database saving (stateless)
curl -X POST http://127.0.0.1:8001/api/ocr/extract/ \
  -F "image=@/path/to/image.png" \
  -F "language=eng" \
  -F "save_to_db=false"
```

**Example using Python requests:**

```python
import requests

url = 'http://127.0.0.1:8001/api/ocr/extract/'
files = {'image': open('image.png', 'rb')}
data = {
    'language': 'eng',
    'save_to_db': 'true'  # or 'false' for stateless processing
}

response = requests.post(url, files=files, data=data)
result = response.json()

if result.get('cached'):
    print("Result returned from cache!")
print(f"Document ID: {result.get('document_id')}")
print(f"Extracted text: {result['text']}")
```

**Get API Information:**

```bash
curl http://127.0.0.1:8001/api/ocr/extract/
```

### 2. Extract Text from PDF

**Endpoint:** `POST /api/pdf/extract/`

**Description:** Extract text from PDF files (text-based or scanned) with optional page selection

**Request:**

- Method: POST
- Content-Type: multipart/form-data
- Body:
  - `file`: PDF file - **Required**
  - `language`: Language code (default: 'eng') - **Optional**
  - `use_ocr`: Use OCR for scanned PDFs (default: true) - **Optional**
  - `pages`: Comma-separated page numbers (e.g., "1,3,5") - **Optional**
  - `save_to_db`: Save to database (default: true) - **Optional**

**Response:**

```json
{
  "success": true,
  "text": "Extracted text from all pages...",
  "filename": "document.pdf",
  "file_size": 2456789,
  "total_pages": 10,
  "pages_extracted": 10,
  "method": "text_extraction",
  "language": "eng",
  "character_count": 5000,
  "word_count": 850,
  "processing_time_ms": 1250,
  "document_id": "550e8400-e29b-41d4-a716-446655440001",
  "cached": false,
  "pages": [
    {
      "page_number": 1,
      "text": "Page 1 text...",
      "word_count": 85,
      "character_count": 500,
      "method": "text_extraction"
    }
  ]
}
```

**Method Values:**

- `text_extraction`: Text was extracted from text-based PDF
- `ocr`: Text was extracted using OCR (scanned PDF)
- `mixed`: Some pages used text extraction, others used OCR

**Example using cURL:**

```bash
# Extract all pages
curl -X POST http://127.0.0.1:8001/api/pdf/extract/ \
  -F "file=@/path/to/document.pdf" \
  -F "language=eng" \
  -F "use_ocr=true"

# Extract specific pages only
curl -X POST http://127.0.0.1:8001/api/pdf/extract/ \
  -F "file=@/path/to/document.pdf" \
  -F "pages=1,3,5"

# Stateless processing (no database)
curl -X POST http://127.0.0.1:8001/api/pdf/extract/ \
  -F "file=@/path/to/document.pdf" \
  -F "save_to_db=false"
```

### 3. Multi-Format Extract

**Endpoint:** `POST /api/extract/`

**Description:** Auto-detect file type (image or PDF) and extract text

**Request:**

- Method: POST
- Content-Type: multipart/form-data
- Body:
  - `file`: Image or PDF file - **Required**
  - `language`: Language code (default: 'eng') - **Optional**
  - `save_to_db`: Save to database (default: true) - **Optional**

**Response:** Same format as image or PDF endpoint depending on file type

**Example:**

```bash
curl -X POST http://127.0.0.1:8001/api/extract/ \
  -F "file=@/path/to/file.png" \
  -F "language=eng"
```

curl -X POST http://127.0.0.1:8001/api/extract/ \
 -F "file=@/path/to/file.png" \
 -F "language=eng"

````

### 4. Health Check

**Endpoint:** `GET /api/ocr/health/`

**Description:** Check if OCR service is working properly

**Response:**

```json
{
  "status": "healthy",
  "tesseract_installed": true,
  "tesseract_version": "5.3.0",
  "supported_languages": 14
}
````

**Example:**

```bash
curl http://127.0.0.1:8001/api/ocr/health/
```

### 5. Supported Languages

**Endpoint:** `GET /api/ocr/languages/`

**Description:** Get list of all supported OCR languages installed on the system

**Response:**

```json
{
  "success": true,
  "count": 14,
  "languages": {
    "eng": "English",
    "ara": "Arabic",
    "spa": "Spanish",
    "fra": "French",
    "deu": "German",
    "rus": "Russian",
    "chi_sim": "Chinese (Simplified)",
    "jpn": "Japanese"
  }
}
```

**Example:**

```bash
curl http://127.0.0.1:8001/api/ocr/languages/
```

## Database Schema

The application uses 4 main models for document management and audit logging. For complete details, see [DATABASE_ARCHITECTURE.md](DATABASE_ARCHITECTURE.md).

### OCRDocument

Stores uploaded documents with metadata and processing status.

**Key Fields:**

- `uuid`: Public UUID identifier (prevents enumeration)
- `file`: Uploaded file (stored in `media/ocr_documents/YYYY/MM/DD/`)
- `file_hash`: SHA256 hash for duplicate detection
- `file_type`: 'image' or 'pdf'
- `status`: 'pending', 'processing', 'completed', 'failed', 'archived'
- `language`: OCR language code
- `is_deleted`: Soft delete flag

**Methods:**

- `soft_delete()`: Mark as deleted without removing from database
- `archive()`: Move to archived status
- `calculate_file_hash(content)`: Generate SHA256 hash

### OCRResult

Stores text extraction results with metrics.

**Key Fields:**

- `document`: Foreign key to OCRDocument
- `extracted_text`: The extracted text content
- `extraction_method`: 'ocr', 'text_extraction', or 'mixed'
- `word_count`: Automatically calculated
- `character_count`: Automatically calculated
- `processing_time_ms`: Processing duration in milliseconds
- `confidence_score`: Average OCR confidence (0-100)

### PDFPageResult

Stores per-page results for PDF documents.

**Key Fields:**

- `result`: Foreign key to OCRResult
- `page_number`: Page number (1-indexed)
- `extracted_text`: Text from this page
- `word_count`: Words on this page
- `extraction_method`: Method used for this page

### OCRProcessingLog

Audit trail for all processing events.

**Key Fields:**

- `document`: Foreign key to OCRDocument
- `level`: 'info', 'warning', 'error'
- `message`: Human-readable message
- `details`: JSON field for structured data

**Example Log Entry:**

```json
{
  "level": "info",
  "message": "Successfully extracted text from example.pdf",
  "details": {
    "total_pages": 10,
    "method": "text_extraction",
    "word_count": 850,
    "processing_time_ms": 1250
  }
}
```

### Caching & Duplicate Detection

The system uses SHA256 file hashing to detect duplicates:

1. When a file is uploaded, its hash is calculated
2. System checks for existing documents with same hash
3. If found and `save_to_db=true`:
   - Returns cached result instantly
   - Response includes `"cached": true`
   - No reprocessing needed
4. If not found:
   - Processes file normally
   - Saves to database for future cache hits

**Benefits:**

- Faster responses for duplicate files
- Reduced server load
- Cost savings on processing resources

## Testing

The project includes comprehensive test coverage with 44+ tests.

### Test Structure

```
tests/
├── README.md                          # Testing documentation
└── ocr/
    ├── __init__.py
    ├── test_ocr_extract.py           # Image OCR integration tests (7 tests)
    ├── test_health_check.py          # Health endpoint tests (4 tests)
    ├── test_supported_languages.py   # Language listing tests (5 tests)
    ├── test_pdf_extract.py           # PDF extraction tests (6 tests)
    ├── test_multiformat_extract.py   # Multi-format tests (9 tests)
    └── test_services.py              # Service layer unit tests (13 tests)
```

### Running Tests

```bash
# Run all tests
cd fergani
python manage.py test

# Run specific test file
python manage.py test tests.ocr.test_ocr_extract

# Run with coverage
coverage run --source='ocr' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Test Categories

**Integration Tests** (tests/ocr/test\_\*.py)

- Test API endpoints end-to-end
- Verify request/response formats
- Check error handling
- Test file uploads and processing

**Unit Tests** (tests/ocr/test_services.py)

- Test service layer methods in isolation
- Mock external dependencies
- Verify business logic
- Test edge cases

**Example Test:**

```python
from django.test import TestCase
from rest_framework.test import APITestCase
from PIL import Image
import io

class OCRExtractTests(APITestCase):
    def test_extract_text_from_image(self):
        # Create test image
        image = Image.new('RGB', (100, 100), color='white')
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)

        # Make API request
        response = self.client.post('/api/ocr/extract/', {
            'image': buffer,
            'language': 'eng',
            'save_to_db': 'true'
        }, format='multipart')

        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        self.assertIn('document_id', response.data)
```

For complete testing documentation, see [tests/README.md](fergani/tests/README.md).

## CI/CD Pipeline

The project includes a comprehensive CI/CD pipeline using **GitHub Actions**.

### 🔄 Automated Workflows

#### CI Workflow (Pull Requests to `develop`)

Every PR to the `develop` branch automatically:

✅ **Checks code formatting** (Black)  
✅ **Validates import sorting** (isort)  
✅ **Runs linting** (Flake8)  
✅ **Verifies migrations** (no unapplied changes)  
✅ **Runs all tests** (44+ tests)  
✅ **Measures coverage** (minimum 70% required)

#### Deploy Workflow (Push to `main`)

Every push to `main` branch:

🚀 **Runs deployment checks**  
🚀 **Auto-deploys to Railway/Render**  
🚀 **Monitors deployment status**

### 📋 Branch Strategy

```
feature/branch → PR → develop (CI checks) → main (auto-deploy)
```

- **`develop`**: Development branch, all PRs merge here
- **`main`**: Production branch, auto-deploys to live server

### 🛠️ Setting Up CI/CD Locally

**Install development tools:**

```bash
pip install black flake8 isort coverage
```

**Install pre-commit hook** (automatically runs checks before each commit):

```bash
chmod +x pre-commit-hook.sh
cp pre-commit-hook.sh .git/hooks/pre-commit
```

**Manual checks:**

```bash
cd fergani

# Format code
black .
isort .

# Run linting
flake8 .

# Check migrations
python manage.py makemigrations --check --dry-run

# Run tests with coverage
coverage run --source='ocr' manage.py test tests/
coverage report
```

### 📊 Code Quality Standards

| Tool         | Purpose         | Configuration        |
| ------------ | --------------- | -------------------- |
| **Black**    | Code formatting | 127 char line length |
| **isort**    | Import sorting  | Black-compatible     |
| **Flake8**   | Linting         | Max complexity: 10   |
| **Coverage** | Test coverage   | Minimum: 70%         |

### 📚 Full CI/CD Documentation

- **Quick Setup**: [SETUP_CI.md](SETUP_CI.md)
- **Detailed Guide**: [CI_CD.md](CI_CD.md)
- **Workflow Files**: `.github/workflows/`

### 🎯 Workflow Status

![CI Status](https://github.com/YOUR_USERNAME/fergani-ocr/workflows/CI%20-%20Fergani%20OCR/badge.svg?branch=develop)
![Deployment](https://github.com/YOUR_USERNAME/fergani-ocr/workflows/Deploy%20to%20Production/badge.svg?branch=main)

> **Note**: Replace `YOUR_USERNAME` with your GitHub username to see live status badges.

## Configuration

### Django Settings

Key settings in `fergani/settings.py`:

```python
# Media files (uploaded documents)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Maximum file upload size (Django)
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB

# View-level max sizes
OCRExtractTextView.MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB for images
PDFExtractTextView.MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB for PDFs
```

### Environment Variables

For production, use environment variables:

```bash
# .env file
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Tesseract configuration
TESSERACT_CMD=/usr/bin/tesseract  # Path to tesseract binary
```

### Admin Panel

Access the admin panel at `/admin/` to:

- View all uploaded documents
- Monitor processing status
- View extraction results
- Check audit logs
- Perform bulk actions (archive, soft delete)
- View colored status indicators

**Admin Features:**

- **Colored Status Badges**: Visual indicators for document status
- **File Size Formatting**: Human-readable file sizes
- **Bulk Actions**: Archive or soft delete multiple documents
- **Processing Metrics**: View confidence scores and processing times
- **Audit Trail**: Read-only access to all processing logs
- **Search & Filters**: Find documents by name, status, date, etc.

## Deployment

### Production Checklist

1. **Environment Configuration**

```bash
export DEBUG=False
export SECRET_KEY='generate-strong-secret-key'
export ALLOWED_HOSTS='yourdomain.com'
```

2. **Database Setup**

```bash
# Use PostgreSQL in production
pip install psycopg2-binary
python manage.py migrate
python manage.py createsuperuser
```

3. **Static Files**

```bash
python manage.py collectstatic --no-input
```

4. **Web Server**
   Use Gunicorn + Nginx:

```bash
# Install Gunicorn
pip install gunicorn

# Run Gunicorn
gunicorn fergani.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

5. **Nginx Configuration**

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /media/ {
        alias /path/to/fergani-ocr/fergani/media/;
    }

    location /static/ {
        alias /path/to/fergani-ocr/fergani/staticfiles/;
    }
}
```

6. **Security**

- Enable HTTPS with SSL certificates (Let's Encrypt)
- Set secure cookie flags
- Configure CORS properly
- Regular security updates
- Backup database regularly

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Install Tesseract and dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-ara \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY fergani/ /app/
RUN python manage.py collectstatic --no-input

EXPOSE 8000
CMD ["gunicorn", "fergani.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## Project Structure

```
fergani-ocr/
├── README.md                      # This file
├── DATABASE_ARCHITECTURE.md       # Database design documentation
├── requirements.txt               # Python dependencies
├── fergani/                       # Django project root
│   ├── manage.py                  # Django management script
│   ├── fergani/                   # Project configuration
│   │   ├── __init__.py
│   │   ├── settings.py           # Django settings
│   │   ├── urls.py               # URL routing
│   │   ├── asgi.py               # ASGI config
│   │   └── wsgi.py               # WSGI config
│   ├── ocr/                      # Main OCR application
│   │   ├── __init__.py
│   │   ├── admin.py              # Admin panel configuration
│   │   ├── apps.py               # App configuration
│   │   ├── models.py             # Database models (4 models)
│   │   ├── views.py              # API views (image OCR)
│   │   ├── pdf_views.py          # PDF and multi-format views
│   │   ├── services.py           # Service layer (business logic)
│   │   ├── serializers.py        # DRF serializers
│   │   ├── utils.py              # OCR and PDF processors
│   │   ├── migrations/           # Database migrations
│   │   │   ├── __init__.py
│   │   │   └── 0001_initial.py   # Initial schema
│   │   └── templates/            # Frontend templates
│   │       └── ocr/
│   │           └── index.html    # Web UI
│   ├── tests/                    # Test suite
│   │   ├── README.md             # Test documentation
│   │   └── ocr/                  # OCR app tests
│   │       ├── __init__.py
│   │       ├── test_ocr_extract.py
│   │       ├── test_health_check.py
│   │       ├── test_supported_languages.py
│   │       ├── test_pdf_extract.py
│   │       ├── test_multiformat_extract.py
│   │       └── test_services.py
│   └── media/                    # Uploaded files (created at runtime)
│       └── ocr_documents/        # Organized by date (YYYY/MM/DD/)
└── .gitignore
```

## Development

### Technology Stack

- **Backend Framework**: Django 5.0.1
- **API Framework**: Django REST Framework 3.14.0+
- **OCR Engine**: Tesseract OCR (via pytesseract)
- **Image Processing**: Pillow 10.0+
- **PDF Processing**: PyPDF2, pdf2image
- **Database**: SQLite (dev), PostgreSQL (recommended for production)
- **Testing**: Django TestCase, DRF APITestCase

### Code Organization

**Service Layer** (`ocr/services.py`)

- **OCRService**: Image OCR business logic

  - `process_image_extraction()`: Main image processing
  - `get_ocr_api_info()`: API metadata
  - `get_health_status()`: Service health check
  - `get_supported_languages()`: Language listing

- **PDFService**: PDF extraction business logic

  - `process_pdf_extraction()`: Main PDF processing
  - `validate_pdf_file()`: File validation
  - `get_pdf_api_info()`: API metadata

- **MultiFormatService**: Multi-format handling
  - `process_file()`: Auto-detect and process
  - `validate_file()`: File validation
  - `get_api_info()`: API metadata

**Utilities** (`ocr/utils.py`)

- **OCRProcessor**: Core Tesseract operations

  - `extract_text()`: Extract text from PIL Image
  - `get_confidence_scores()`: OCR confidence metrics
  - `get_image_info()`: Image metadata
  - `is_tesseract_installed()`: Check Tesseract availability
  - `get_supported_languages()`: Query installed languages

- **PDFProcessor**: Core PDF operations
  - `extract_text_from_pdf()`: PDF text extraction
  - `extract_specific_pages()`: Page selection
  - `is_text_based_pdf()`: Detect PDF type

### Design Principles

1. **Separation of Concerns**

   - Views: HTTP handling only
   - Services: Business logic
   - Utils: Core processing
   - Models: Data persistence

2. **Single Responsibility**

   - Each class has one clear purpose
   - Methods are focused and testable
   - Easy to maintain and extend

3. **DRY (Don't Repeat Yourself)**

   - Shared logic in service layer
   - Reusable utility functions
   - Consistent error handling

4. **Testability**
   - Service layer methods are pure functions
   - Easy to mock dependencies
   - Comprehensive test coverage

### Adding New Features

**Example: Add new image preprocessing option**

1. Add utility function in `utils.py`:

```python
class OCRProcessor:
    @staticmethod
    def preprocess_image_denoise(image):
        """Remove noise from image"""
        # Implementation
        return processed_image
```

2. Add service method in `services.py`:

```python
class OCRService:
    @staticmethod
    def process_with_denoise(image_file, language='eng'):
        image = Image.open(image_file)
        image = OCRProcessor.preprocess_image_denoise(image)
        return OCRProcessor.extract_text(image, language)
```

3. Add view endpoint in `views.py`:

```python
class OCRDenoiseView(APIView):
    def post(self, request):
        # Handle request
        result = OCRService.process_with_denoise(
            request.FILES['image'],
            request.data.get('language', 'eng')
        )
        return Response(result)
```

4. Add tests in `tests/ocr/test_denoise.py`:

```python
class DenoiseTests(APITestCase):
    def test_denoise_extraction(self):
        # Test implementation
        pass
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`python manage.py test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Supported Languages

The application supports 100+ languages through Tesseract. Common languages include:

- `eng` - English
- `ara` - Arabic
- `spa` - Spanish
- `fra` - French
- `deu` - German
- `rus` - Russian
- `chi_sim` - Chinese (Simplified)
- `chi_tra` - Chinese (Traditional)
- `jpn` - Japanese
- `kor` - Korean
- `hin` - Hindi
- `por` - Portuguese
- `ita` - Italian
- `tur` - Turkish
- `pol` - Polish

**Note**: Language packs must be installed separately. Use `GET /api/ocr/languages/` to see which languages are currently available on your system.

## Troubleshooting

### Tesseract Not Found

```bash
# Check if Tesseract is installed
tesseract --version

# If not found, install it
sudo apt-get install tesseract-ocr  # Ubuntu/Debian
brew install tesseract              # macOS
```

### Language Not Supported

```bash
# List installed languages
tesseract --list-langs

# Install additional language
sudo apt-get install tesseract-ocr-ara  # Arabic
```

### PDF Processing Errors

```bash
# Install PDF dependencies
pip install PyPDF2 pdf2image
sudo apt-get install poppler-utils  # Ubuntu/Debian
brew install poppler                # macOS
```

### Database Migration Issues

```bash
# Reset migrations (development only!)
python manage.py migrate ocr zero
python manage.py migrate

# Or start fresh
rm db.sqlite3
python manage.py migrate
```

### File Upload Size Issues

Check these settings in `settings.py`:

```python
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB
```

## Performance Optimization

### Caching Benefits

The SHA256-based caching system provides:

- **10-100x faster** responses for duplicate files
- **Zero CPU usage** for cached results
- **Reduced database load** through intelligent deduplication

### Recommended Production Settings

```python
# settings.py

# Use Redis for session/cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Use Celery for async processing (optional)
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Database connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'CONN_MAX_AGE': 600,  # Connection pooling
    }
}
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Quick Start for Contributors

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/fergani-ocr.git

# Install dev tools
pip install black flake8 isort coverage

# Set up pre-commit hook
cp pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Create feature branch
git checkout -b feature/awesome-feature

# Make changes, commit, and push
git commit -m "Add awesome feature"
git push origin feature/awesome-feature

# Open PR to 'develop' branch
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Code quality standards
- Testing guidelines
- PR process
- Branch strategy
- Commit message format

## License

MIT License

Copyright (c) 2026 Fergani OCR Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

**Built with ❤️ using Django, Tesseract OCR, and modern Python best practices.**
