"""
Tests for OCR models
"""

from django.test import TestCase
from django.utils import timezone

from ocr.models import OCRDocument, OCRProcessingLog, OCRResult


class OCRDocumentTestCase(TestCase):
    """Test cases for OCRDocument model"""

    def test_calculate_file_hash(self):
        """Test file hash calculation"""
        content1 = b"test content"
        content2 = b"test content"
        content3 = b"different content"

        hash1 = OCRDocument.calculate_file_hash(content1)
        hash2 = OCRDocument.calculate_file_hash(content2)
        hash3 = OCRDocument.calculate_file_hash(content3)

        # Same content should produce same hash
        self.assertEqual(hash1, hash2)
        # Different content should produce different hash
        self.assertNotEqual(hash1, hash3)

    def test_soft_delete(self):
        """Test soft delete functionality"""
        document = OCRDocument.objects.create(file_name="test.png", file_size=1024, file_hash="test123")

        self.assertFalse(document.is_deleted)
        self.assertIsNone(document.deleted_at)

        document.soft_delete()
        document.refresh_from_db()

        self.assertTrue(document.is_deleted)
        self.assertIsNotNone(document.deleted_at)

    def test_archive(self):
        """Test archive functionality"""
        document = OCRDocument.objects.create(file_name="test.png", file_size=1024, file_hash="test123", status="completed")

        self.assertIsNone(document.archived_at)

        document.archive()
        document.refresh_from_db()

        self.assertEqual(document.status, "archived")
        self.assertIsNotNone(document.archived_at)

    def test_document_str_representation(self):
        """Test string representation of document"""
        document = OCRDocument.objects.create(
            file_name="test_image.png", file_size=2048, file_hash="hash456", status="completed"
        )

        str_repr = str(document)
        self.assertIn("test_image.png", str_repr)
        self.assertIn("Completed", str_repr)


class OCRResultTestCase(TestCase):
    """Test cases for OCRResult model"""

    def setUp(self):
        """Set up test fixtures"""
        self.document = OCRDocument.objects.create(file_name="test.png", file_size=1024, file_hash="testhash")

    def test_create_result(self):
        """Test creating OCR result"""
        result = OCRResult.objects.create(
            document=self.document,
            extracted_text="Hello World",
            language="eng",
            confidence_score=95.5,
        )

        self.assertEqual(result.document, self.document)
        self.assertEqual(result.extracted_text, "Hello World")
        self.assertEqual(result.language, "eng")
        self.assertEqual(result.confidence_score, 95.5)
        self.assertEqual(result.character_count, 11)  # "Hello World"
        self.assertEqual(result.word_count, 2)

    def test_result_str_representation(self):
        """Test string representation of result"""
        result = OCRResult.objects.create(document=self.document, extracted_text="Test text", language="eng")

        str_repr = str(result)
        self.assertIn("test.png", str_repr)

    def test_result_word_count(self):
        """Test word count calculation"""
        result = OCRResult.objects.create(
            document=self.document,
            extracted_text="This is a test sentence with multiple words",
            language="eng",
        )

        self.assertEqual(result.word_count, 8)

    def test_result_character_count(self):
        """Test character count"""
        result = OCRResult.objects.create(document=self.document, extracted_text="ABC123", language="eng")

        self.assertEqual(result.character_count, 6)


class OCRProcessingLogTestCase(TestCase):
    """Test cases for OCRProcessingLog model"""

    def setUp(self):
        """Set up test fixtures"""
        self.document = OCRDocument.objects.create(file_name="test.png", file_size=1024, file_hash="testhash")

    def test_create_log_entry(self):
        """Test creating log entry"""
        log = OCRProcessingLog.objects.create(
            document=self.document,
            level="info",
            message="Processing started",
            details={"step": "initialization"},
        )

        self.assertEqual(log.document, self.document)
        self.assertEqual(log.level, "info")
        self.assertEqual(log.message, "Processing started")
        self.assertEqual(log.details["step"], "initialization")

    def test_log_str_representation(self):
        """Test string representation of log"""
        log = OCRProcessingLog.objects.create(document=self.document, level="error", message="Processing failed")

        str_repr = str(log)
        self.assertIn("error", str_repr.lower())

    def test_log_levels(self):
        """Test different log levels"""
        levels = ["debug", "info", "warning", "error"]

        for level in levels:
            log = OCRProcessingLog.objects.create(document=self.document, level=level, message=f"Test {level} message")
            self.assertEqual(log.level, level)

    def test_log_with_details(self):
        """Test log with detailed information"""
        details = {"error_code": "OCR_001", "retry_count": 3, "last_attempt": "2024-01-01"}

        log = OCRProcessingLog.objects.create(
            document=self.document,
            level="error",
            message="OCR failed after retries",
            details=details,
        )

        self.assertEqual(log.details["error_code"], "OCR_001")
        self.assertEqual(log.details["retry_count"], 3)
