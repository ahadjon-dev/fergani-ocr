# Database Architecture for OCR Application

## Overview

The OCR application uses a well-structured database schema to store documents, extraction results, and processing logs. This architecture follows Django and database best practices for scalability, performance, and maintainability.

## Database Schema

### Models Overview

```
OCRDocument (Main document storage)
    ├── OCRResult (Extraction results)
    │   └── PDFPageResult (Per-page results for PDFs)
    └── OCRProcessingLog (Audit trail)
```

## Model Details

### 1. OCRDocument

**Purpose**: Stores uploaded documents (images/PDFs) with metadata and processing status.

**Key Features**:

- ✅ **UUID for public access** - Prevents enumeration attacks
- ✅ **File hash (SHA256)** - Detects duplicates and enables caching
- ✅ **Soft delete** - Preserve data for compliance/audit
- ✅ **Archive status** - Mark old documents without deleting
- ✅ **Indexed fields** - Fast queries on common filters

**Fields**:

```python
# Identification
id (BigAutoField)                    # Internal primary key
uuid (UUID)                          # Public identifier

# File Information
file (FileField)                     # Actual file storage
file_name (CharField)                # Original filename
file_size (PositiveIntegerField)     # Size in bytes
file_hash (CharField)                # SHA256 hash
file_type (CharField)                # 'image' or 'pdf'

# Processing
status (CharField)                   # pending/processing/completed/failed/archived
language (CharField)                 # OCR language code

# Timestamps
uploaded_at (DateTimeField)          # Upload time
processed_at (DateTimeField)         # Processing completion time
archived_at (DateTimeField)          # Archival time
is_deleted (BooleanField)            # Soft delete flag
deleted_at (DateTimeField)           # Deletion time
```

**Indexes**:

- `uploaded_at` (DESC) - Recent documents
- `file_hash + is_deleted` - Duplicate detection
- `status + is_deleted` - Processing queue queries
- `uuid` - Public API lookups

**Best Practices Implemented**:

1. **Duplicate Detection**: Check `file_hash` before processing to avoid redundant work
2. **Soft Delete**: Never hard-delete; set `is_deleted=True` for data retention
3. **Status Tracking**: Monitor processing pipeline with status field
4. **Archival**: Move old documents to `archived` status instead of deleting

### 2. OCRResult

**Purpose**: Stores extraction results separately from documents for better query performance.

**Key Features**:

- ✅ **Separate from document** - Optimized for different query patterns
- ✅ **Multiple results per document** - Support reprocessing
- ✅ **Auto-calculated metrics** - Word/character counts via model save()
- ✅ **Performance tracking** - Processing time and confidence scores

**Fields**:

```python
# Identification
id (BigAutoField)
uuid (UUID)
document (ForeignKey)                # Link to OCRDocument

# Results
extracted_text (TextField)           # Full extracted text
word_count (PositiveIntegerField)    # Auto-calculated
character_count (PositiveIntegerField) # Auto-calculated

# Processing Details
extraction_method (CharField)        # text_extraction/ocr/hybrid
language (CharField)
processing_time_ms (PositiveIntegerField)
confidence_score (FloatField)        # OCR confidence (0-100)

# Metadata
created_at (DateTimeField)
```

**Indexes**:

- `document + created_at` (DESC) - Latest result per document

**Best Practices Implemented**:

1. **Separation of Concerns**: Results separate from documents
2. **Reprocessing Support**: Multiple results allowed per document
3. **Auto-calculation**: Counts calculated in `save()` method
4. **Performance Metrics**: Track processing time for optimization

### 3. PDFPageResult

**Purpose**: Stores per-page results for PDF documents enabling granular access.

**Key Features**:

- ✅ **Page-level granularity** - Access specific pages
- ✅ **Partial reprocessing** - Reprocess individual pages
- ✅ **Page-specific metrics** - Per-page confidence scores

**Fields**:

```python
id (BigAutoField)
result (ForeignKey)                  # Link to OCRResult
page_number (PositiveIntegerField)
extracted_text (TextField)
word_count (PositiveIntegerField)
character_count (PositiveIntegerField)
extraction_method (CharField)
confidence_score (FloatField)
created_at (DateTimeField)
```

**Constraints**:

- `UNIQUE (result, page_number)` - One entry per page

**Indexes**:

- `result + page_number` - Fast page lookup

### 4. OCRProcessingLog

**Purpose**: Audit trail for all processing events.

**Key Features**:

- ✅ **Complete audit trail** - Track all processing events
- ✅ **Structured logging** - JSON details field for additional data
- ✅ **Error tracking** - Capture failures for debugging
- ✅ **Read-only in admin** - Logs are immutable

**Fields**:

```python
id (BigAutoField)
document (ForeignKey)
level (CharField)                    # info/warning/error
message (TextField)
details (JSONField)                  # Structured additional data
created_at (DateTimeField)
```

**Indexes**:

- `document + created_at` (DESC) - Document timeline
- `level + created_at` (DESC) - Error queries

## Database Best Practices Implemented

### 1. Indexing Strategy

**Composite Indexes**:

```python
# For queries like: "Find recent documents that aren't deleted"
Index(fields=['is_deleted', '-uploaded_at'])

# For queries like: "Get latest result for a document"
Index(fields=['document', '-created_at'])
```

**Single Column Indexes**:

- Primary keys (automatic)
- Foreign keys (automatic)
- UUID fields (for public API)
- Status fields (for filtering)
- Timestamp fields (for sorting)

### 2. Query Optimization

**Avoid N+1 Queries**:

```python
# Bad
documents = OCRDocument.objects.all()
for doc in documents:
    print(doc.results.count())  # N+1 query

# Good
documents = OCRDocument.objects.annotate(
    result_count=Count('results')
)
```

**Use select_related and prefetch_related**:

```python
# For ForeignKey
results = OCRResult.objects.select_related('document').all()

# For reverse ForeignKey
documents = OCRDocument.objects.prefetch_related('results').all()
```

### 3. Data Integrity

**Soft Delete Pattern**:

```python
# Never do this
document.delete()  # Hard delete

# Always do this
document.soft_delete()  # Soft delete
```

**Unique Constraints**:

```python
# Prevent duplicate pages
unique_together = [['result', 'page_number']]
```

### 4. Storage Optimization

**File Organization**:

```python
# Files organized by date
upload_to='ocr/documents/%Y/%m/%d/'
# Example: ocr/documents/2026/01/02/file.pdf
```

**Benefits**:

- Prevents too many files in one directory
- Easy to archive old files
- Better file system performance

### 5. Caching Strategy

**Duplicate Detection**:

```python
# Check hash before processing
existing = OCRDocument.objects.filter(
    file_hash=file_hash,
    is_deleted=False
).first()

if existing and existing.results.exists():
    return existing.results.first()  # Return cached
```

### 6. Archival Strategy

**Automatic Archival** (implement with Celery task):

```python
from datetime import timedelta
from django.utils import timezone

# Archive documents older than 90 days
old_date = timezone.now() - timedelta(days=90)
OCRDocument.objects.filter(
    uploaded_at__lt=old_date,
    status='completed'
).update(
    status='archived',
    archived_at=timezone.now()
)
```

## Performance Considerations

### 1. Database Connection Pooling

Configure in `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

### 2. Bulk Operations

For bulk inserts:

```python
# Create many page results at once
PDFPageResult.objects.bulk_create([
    PDFPageResult(result=result, page_number=1, ...),
    PDFPageResult(result=result, page_number=2, ...),
    # ...
])
```

### 3. Query Analysis

Use Django Debug Toolbar in development:

```python
# settings.py
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

### 4. Database Monitoring

Monitor slow queries:

```python
# settings.py (development)
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',  # Log all queries
        }
    }
}
```

## Backup and Recovery

### Regular Backups

**PostgreSQL**:

```bash
# Backup
pg_dump fergani_ocr > backup_$(date +%Y%m%d).sql

# Restore
psql fergani_ocr < backup_20260102.sql
```

**SQLite** (development):

```bash
# Backup
cp db.sqlite3 db.backup_$(date +%Y%m%d).sqlite3
```

### Media Files

```bash
# Backup uploaded files
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/
```

## Migration Best Practices

### 1. Always Review Migrations

```bash
python manage.py makemigrations --dry-run --verbosity 3
```

### 2. Test Migrations

```bash
# Test on copy of production database
python manage.py migrate --fake-initial
```

### 3. Rollback Plan

```bash
# Rollback last migration
python manage.py migrate ocr <previous_migration_number>
```

## Security Considerations

### 1. File Upload Validation

```python
# Validate file extensions
FileExtensionValidator(
    allowed_extensions=['pdf', 'png', 'jpg', 'jpeg', 'tiff']
)
```

### 2. File Size Limits

```python
# In view or service
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
if file.size > MAX_FILE_SIZE:
    raise ValidationError('File too large')
```

### 3. UUID Instead of Sequential IDs

```python
# Use UUID for public APIs
/api/documents/{uuid}/  # Good
/api/documents/{id}/    # Bad (enumeration attack)
```

## Monitoring and Analytics

### Useful Queries

```python
# Documents processed today
from django.utils import timezone
today = timezone.now().date()
OCRDocument.objects.filter(
    processed_at__date=today,
    status='completed'
).count()

# Average processing time
from django.db.models import Avg
OCRResult.objects.aggregate(Avg('processing_time_ms'))

# Error rate
total = OCRDocument.objects.count()
failed = OCRDocument.objects.filter(status='failed').count()
error_rate = (failed / total) * 100 if total > 0 else 0

# Popular languages
from django.db.models import Count
OCRDocument.objects.values('language').annotate(
    count=Count('id')
).order_by('-count')
```

## Future Enhancements

1. **User Association**: Add `user` ForeignKey to track who uploaded documents
2. **Sharing**: Add `is_public` and `shared_with` fields for collaboration
3. **Versioning**: Keep history of reprocessing attempts
4. **Tags/Categories**: Add tagging system for organization
5. **Batch Processing**: Add `Batch` model for processing multiple documents together
6. **API Rate Limiting**: Track usage per user/API key

## Conclusion

This database architecture provides:

- ✅ Scalability through proper indexing
- ✅ Performance through caching and optimization
- ✅ Data integrity through constraints and soft deletes
- ✅ Auditability through comprehensive logging
- ✅ Security through validation and UUIDs
- ✅ Maintainability through separation of concerns
