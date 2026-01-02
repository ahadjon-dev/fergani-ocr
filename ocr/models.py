import hashlib
import uuid

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone


class OCRDocument(models.Model):
    """
    Stores uploaded documents (images/PDFs) for OCR processing

    Best Practices:
    - Store file hash to detect duplicates
    - Track file metadata for analytics
    - Soft delete for data retention
    - Use UUID for public IDs to prevent enumeration
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("archived", "Archived"),
    ]

    FILE_TYPE_CHOICES = [
        ("image", "Image"),
        ("pdf", "PDF"),
    ]

    # Primary identification
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False)

    # File information
    file = models.FileField(
        upload_to="ocr/documents/%Y/%m/%d/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "png", "jpg", "jpeg", "tiff", "bmp", "gif", "webp"])],
    )
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    file_hash = models.CharField(max_length=64, db_index=True, help_text="SHA256 hash of file content for duplicate detection")
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)

    # Processing information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)
    language = models.CharField(max_length=10, default="eng", help_text="OCR language code")

    # Metadata
    uploaded_at = models.DateTimeField(auto_now_add=True, db_index=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    # Soft delete and archiving
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True, help_text="When document was archived")

    class Meta:
        db_table = "ocr_document"
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["-uploaded_at"]),
            models.Index(fields=["file_hash", "is_deleted"]),
            models.Index(fields=["status", "is_deleted"]),
        ]
        verbose_name = "OCR Document"
        verbose_name_plural = "OCR Documents"

    def __str__(self):
        return f"{self.file_name} ({self.get_status_display()})"

    @staticmethod
    def calculate_file_hash(file_content):
        """Calculate SHA256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()

    def soft_delete(self):
        """Soft delete the document"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def archive(self):
        """Archive the document"""
        self.status = "archived"
        self.archived_at = timezone.now()
        self.save(update_fields=["status", "archived_at"])


class OCRResult(models.Model):
    """
    Stores OCR extraction results

    Best Practices:
    - Separate results from documents for better query performance
    - Store both raw and processed text
    - Keep metadata for analytics
    - Allow multiple results per document (e.g., reprocessing with different settings)
    """

    EXTRACTION_METHOD_CHOICES = [
        ("text_extraction", "Text Extraction"),
        ("ocr", "OCR"),
        ("hybrid", "Hybrid"),
    ]

    # Primary identification
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False)

    # Relationship
    document = models.ForeignKey(OCRDocument, on_delete=models.CASCADE, related_name="results")

    # Extraction results
    extracted_text = models.TextField(help_text="Full extracted text")
    word_count = models.PositiveIntegerField(default=0)
    character_count = models.PositiveIntegerField(default=0)

    # Processing details
    extraction_method = models.CharField(
        max_length=20, choices=EXTRACTION_METHOD_CHOICES, help_text="Method used for text extraction"
    )
    language = models.CharField(max_length=10, help_text="Language used for extraction")

    # Performance metrics
    processing_time_ms = models.PositiveIntegerField(null=True, blank=True, help_text="Processing time in milliseconds")

    # Quality metrics (for images/OCR)
    confidence_score = models.FloatField(null=True, blank=True, help_text="Average OCR confidence score (0-100)")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "ocr_result"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["document", "-created_at"]),
        ]
        verbose_name = "OCR Result"
        verbose_name_plural = "OCR Results"

    def __str__(self):
        return f"Result for {self.document.file_name} ({self.extraction_method})"

    def save(self, *args, **kwargs):
        """Auto-calculate word and character counts"""
        if self.extracted_text:
            self.word_count = len(self.extracted_text.strip().split())
            self.character_count = len(self.extracted_text.strip())
        super().save(*args, **kwargs)


class PDFPageResult(models.Model):
    """
    Stores per-page results for PDF documents

    Best Practices:
    - Allow granular access to specific pages
    - Support partial reprocessing
    - Enable page-level analytics
    """

    # Primary identification
    id = models.BigAutoField(primary_key=True)

    # Relationship
    result = models.ForeignKey(OCRResult, on_delete=models.CASCADE, related_name="pages")

    # Page information
    page_number = models.PositiveIntegerField()
    extracted_text = models.TextField()
    word_count = models.PositiveIntegerField(default=0)
    character_count = models.PositiveIntegerField(default=0)

    # Page-specific metrics
    extraction_method = models.CharField(max_length=20)
    confidence_score = models.FloatField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ocr_pdf_page_result"
        ordering = ["result", "page_number"]
        unique_together = [["result", "page_number"]]
        indexes = [
            models.Index(fields=["result", "page_number"]),
        ]
        verbose_name = "PDF Page Result"
        verbose_name_plural = "PDF Page Results"

    def __str__(self):
        return f"Page {self.page_number} of {self.result}"

    def save(self, *args, **kwargs):
        """Auto-calculate word and character counts"""
        if self.extracted_text:
            self.word_count = len(self.extracted_text.strip().split())
            self.character_count = len(self.extracted_text.strip())
        super().save(*args, **kwargs)


class OCRProcessingLog(models.Model):
    """
    Audit log for OCR processing events

    Best Practices:
    - Track all processing events for debugging
    - Store error messages for troubleshooting
    - Enable performance monitoring
    """

    LEVEL_CHOICES = [
        ("info", "Info"),
        ("warning", "Warning"),
        ("error", "Error"),
    ]

    # Primary identification
    id = models.BigAutoField(primary_key=True)

    # Relationship
    document = models.ForeignKey(OCRDocument, on_delete=models.CASCADE, related_name="logs")

    # Log information
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, db_index=True)
    message = models.TextField()
    details = models.JSONField(null=True, blank=True, help_text="Additional structured data")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "ocr_processing_log"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["document", "-created_at"]),
            models.Index(fields=["level", "-created_at"]),
        ]
        verbose_name = "OCR Processing Log"
        verbose_name_plural = "OCR Processing Logs"

    def __str__(self):
        return f"{self.get_level_display()}: {self.message[:50]}"
