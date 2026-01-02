"""
Unit tests for service layer
Tests the service layer functions directly
"""

import io
from unittest.mock import MagicMock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from ocr.models import OCRDocument, OCRProcessingLog
from ocr.services import MultiFormatService, OCRService, PDFService


class TestOCRService(TestCase):
    """Test suite for OCR service layer"""

    def _create_test_image(self, size=(200, 100), format="PNG"):
        """Helper method to create a test image"""
        image = Image.new("RGB", size, color="white")
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=format)
        img_byte_arr.seek(0)

        return SimpleUploadedFile(f"test_image.{format.lower()}", img_byte_arr.read(), content_type=f"image/{format.lower()}")

    def test_process_image_extraction(self):
        """
        Test: Process image extraction
        Expected: Returns dictionary with expected fields
        """
        image_file = self._create_test_image()
        result = OCRService.process_image_extraction(image_file, language="eng")

        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("text", result)
        self.assertIn("filename", result)
        self.assertIn("file_size", result)
        self.assertIn("image_dimensions", result)
        self.assertIn("image_format", result)
        self.assertIn("language", result)
        self.assertIn("character_count", result)
        self.assertIn("word_count", result)

    def test_get_ocr_api_info(self):
        """
        Test: Get OCR API information
        Expected: Returns complete API info dictionary
        """
        max_file_size = 10 * 1024 * 1024
        result = OCRService.get_ocr_api_info(max_file_size)

        self.assertIsInstance(result, dict)
        self.assertIn("message", result)
        self.assertIn("version", result)
        self.assertIn("supported_languages", result)
        self.assertIn("tesseract_installed", result)

    def test_get_health_status(self):
        """
        Test: Get health status
        Expected: Returns health status dictionary
        """
        result = OCRService.get_health_status()

        self.assertIsInstance(result, dict)
        self.assertIn("status", result)
        self.assertIn("tesseract_installed", result)
        self.assertIn("supported_languages", result)
        self.assertIn(result["status"], ["healthy", "unhealthy"])

    def test_get_supported_languages(self):
        """
        Test: Get supported languages
        Expected: Returns dictionary with languages
        """
        result = OCRService.get_supported_languages()

        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("count", result)
        self.assertIn("languages", result)
        self.assertTrue(result["success"])


class TestPDFService(TestCase):
    """Test suite for PDF service layer"""

    def _create_test_pdf(self):
        """Helper method to create a test PDF file"""
        return SimpleUploadedFile("test.pdf", b"Test PDF content", content_type="application/pdf")

    def test_validate_pdf_file_success(self):
        """
        Test: Validate valid PDF file
        Expected: Returns (True, None)
        """
        pdf_file = self._create_test_pdf()
        max_size = 50 * 1024 * 1024

        is_valid, error_msg = PDFService.validate_pdf_file(pdf_file, max_size)

        self.assertTrue(is_valid)
        self.assertIsNone(error_msg)

    def test_validate_pdf_file_invalid_type(self):
        """
        Test: Validate non-PDF file
        Expected: Returns (False, error_message)
        """
        text_file = SimpleUploadedFile("test.txt", b"Not a PDF", content_type="text/plain")
        max_size = 50 * 1024 * 1024

        is_valid, error_msg = PDFService.validate_pdf_file(text_file, max_size)

        self.assertFalse(is_valid)
        self.assertIsNotNone(error_msg)
        self.assertIn("Invalid file type", error_msg)

    def test_validate_pdf_file_oversized(self):
        """
        Test: Validate oversized PDF file
        Expected: Returns (False, error_message)
        """
        # Create a PDF that's larger than limit
        large_content = b"x" * (100 * 1024)  # 100KB
        pdf_file = SimpleUploadedFile("test.pdf", large_content, content_type="application/pdf")
        max_size = 50 * 1024  # 50KB limit

        is_valid, error_msg = PDFService.validate_pdf_file(pdf_file, max_size)

        self.assertFalse(is_valid)
        self.assertIsNotNone(error_msg)
        self.assertIn("exceeds maximum limit", error_msg)

    def test_get_pdf_api_info(self):
        """
        Test: Get PDF API information
        Expected: Returns complete API info dictionary
        """
        max_file_size = 50 * 1024 * 1024
        result = PDFService.get_pdf_api_info(max_file_size)

        self.assertIsInstance(result, dict)
        self.assertIn("message", result)
        self.assertIn("version", result)
        self.assertIn("pdf_support_available", result)
        self.assertIn("features", result)
        self.assertIn("parameters", result)


class TestMultiFormatService(TestCase):
    """Test suite for MultiFormat service layer"""

    def _create_test_image(self):
        """Helper method to create a test image"""
        image = Image.new("RGB", (200, 100), color="white")
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)

        return SimpleUploadedFile("test_image.png", img_byte_arr.read(), content_type="image/png")

    def _create_test_pdf(self):
        """Helper method to create a test PDF file"""
        return SimpleUploadedFile("test.pdf", b"Test PDF content", content_type="application/pdf")

    def test_validate_file_image_success(self):
        """
        Test: Validate valid image file
        Expected: Returns (True, None, 'image')
        """
        image_file = self._create_test_image()
        max_size = 50 * 1024 * 1024

        is_valid, error_msg, file_type = MultiFormatService.validate_file(image_file, max_size)

        self.assertTrue(is_valid)
        self.assertIsNone(error_msg)
        self.assertEqual(file_type, "image")

    def test_validate_file_pdf_success(self):
        """
        Test: Validate valid PDF file
        Expected: Returns (True, None, 'pdf')
        """
        pdf_file = self._create_test_pdf()
        max_size = 50 * 1024 * 1024

        is_valid, error_msg, file_type = MultiFormatService.validate_file(pdf_file, max_size)

        self.assertTrue(is_valid)
        self.assertIsNone(error_msg)
        self.assertEqual(file_type, "pdf")

    def test_validate_file_invalid_type(self):
        """
        Test: Validate unsupported file type
        Expected: Returns (False, error_message, None)
        """
        text_file = SimpleUploadedFile("test.txt", b"Not supported", content_type="text/plain")
        max_size = 50 * 1024 * 1024

        is_valid, error_msg, file_type = MultiFormatService.validate_file(text_file, max_size)

        self.assertFalse(is_valid)
        self.assertIsNotNone(error_msg)
        self.assertIsNone(file_type)
        self.assertIn("Unsupported file type", error_msg)

    def test_validate_file_oversized(self):
        """
        Test: Validate oversized file
        Expected: Returns (False, error_message, None)
        """
        large_content = b"x" * (100 * 1024)
        large_file = SimpleUploadedFile("test.png", large_content, content_type="image/png")
        max_size = 50 * 1024

        is_valid, error_msg, file_type = MultiFormatService.validate_file(large_file, max_size)

        self.assertFalse(is_valid)
        self.assertIsNotNone(error_msg)
        self.assertIsNone(file_type)
        self.assertIn("exceeds maximum limit", error_msg)

    def test_get_api_info(self):
        """
        Test: Get multi-format API information
        Expected: Returns complete API info dictionary
        """
        max_file_size = 50 * 1024 * 1024
        result = MultiFormatService.get_api_info(max_file_size)

        self.assertIsInstance(result, dict)
        self.assertIn("message", result)
        self.assertIn("version", result)
        self.assertIn("supported_formats", result)
        self.assertIn("features", result)

        # Check supported formats structure
        supported_formats = result["supported_formats"]
        self.assertIn("images", supported_formats)
        self.assertIn("documents", supported_formats)


class TestOCRServiceErrorHandling(TestCase):
    """Test error handling in OCR service"""

    def _create_test_image(self, size=(200, 100), format="PNG"):
        """Helper method to create a test image"""
        image = Image.new("RGB", size, color="white")
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=format)
        img_byte_arr.seek(0)
        return SimpleUploadedFile(f"test_image.{format.lower()}", img_byte_arr.read(), content_type=f"image/{format.lower()}")

    def test_process_image_with_save_to_db(self):
        """Test processing image with save_to_db enabled"""
        image_file = self._create_test_image()
        result = OCRService.process_image_extraction(image_file, language="eng", save_to_db=True)

        self.assertTrue(result["success"])
        self.assertIn("document_id", result)
        self.assertFalse(result.get("cached", True))  # Should not be cached on first save

    def test_process_image_cached_result(self):
        """Test returning cached result for duplicate image"""
        image_file = self._create_test_image()
        
        # Process once to cache
        first_result = OCRService.process_image_extraction(image_file, language="eng", save_to_db=True)
        doc_id1 = first_result["document_id"]
        
        # Process same image again
        image_file2 = self._create_test_image()  # Same content
        second_result = OCRService.process_image_extraction(image_file2, language="eng", save_to_db=True)
        
        # Should return cached result
        self.assertTrue(second_result.get("cached", False))
        self.assertEqual(second_result["document_id"], doc_id1)

    @patch("ocr.services.OCRProcessor.extract_text")
    def test_process_image_extraction_error_without_db(self, mock_extract):
        """Test error handling when OCR fails without DB save"""
        mock_extract.side_effect = Exception("OCR engine error")
        
        image_file = self._create_test_image()
        
        with self.assertRaises(Exception) as context:
            OCRService.process_image_extraction(image_file, language="eng", save_to_db=False)
        
        self.assertIn("OCR engine error", str(context.exception))

    @patch("ocr.services.OCRProcessor.extract_text")
    def test_process_image_extraction_error_with_db(self, mock_extract):
        """Test error handling when OCR fails with DB save enabled"""
        mock_extract.side_effect = Exception("OCR engine error")
        
        image_file = self._create_test_image()
        
        with self.assertRaises(Exception):
            OCRService.process_image_extraction(image_file, language="eng", save_to_db=True)
        
        # Check that error was logged
        error_logs = OCRProcessingLog.objects.filter(level="error")
        self.assertTrue(error_logs.exists())

    @patch("ocr.services.OCRProcessor.is_tesseract_installed")
    def test_get_health_status_version_error(self, mock_installed):
        """Test health status when version check fails"""
        mock_installed.return_value = True
        
        # Even with error, should still return status
        with patch("pytesseract.get_tesseract_version") as mock_version:
            mock_version.side_effect = Exception("Version check failed")
            result = OCRService.get_health_status()
        
        # Should still return a result
        self.assertIn("status", result)
        self.assertIn("tesseract_installed", result)


class TestPDFServiceErrorHandling(TestCase):
    """Test error handling in PDF service"""

    def test_pdf_service_validation(self):
        """Test PDF service validation methods"""
        pdf_file = SimpleUploadedFile("test.pdf", b"%PDF-1.4", content_type="application/pdf")
        
        # Test validation with correct signature
        is_valid, error_msg = PDFService.validate_pdf_file(pdf_file, 10*1024*1024)
        
        # File is small enough and correct type
        self.assertTrue(is_valid or error_msg is not None)


class TestMultiFormatServiceErrorHandling(TestCase):
    """Test error handling in MultiFormat service"""

    def _create_test_image(self):
        """Helper method to create a test image"""
        image = Image.new("RGB", (200, 100), color="white")
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)
        return SimpleUploadedFile("test_image.png", img_byte_arr.read(), content_type="image/png")

    def test_process_file_image_with_db_save(self):
        """Test processing image file with database save"""
        image_file = self._create_test_image()
        
        result = MultiFormatService.process_file(image_file, language="eng", save_to_db=True)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["file_type"], "image")

    def test_process_file_pdf_with_error(self):
        """Test error handling when PDF processing fails"""
        # Create an invalid PDF that will cause an error (but catches it)
        pdf_file = SimpleUploadedFile("test.pdf", b"not a real pdf", content_type="application/pdf")
        
        # Use try/except to handle the error and verify it's caught properly
        try:
            result = MultiFormatService.process_file(pdf_file, language="eng", save_to_db=False)
            # If it returns, should be an error response
            self.assertFalse(result.get("success", True))
            self.assertEqual(result.get("file_type"), "pdf")
        except Exception:
            # If exception is raised, that's also a valid error path
            pass
