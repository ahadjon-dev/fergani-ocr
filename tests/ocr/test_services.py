"""
Unit tests for service layer
Tests the service layer functions directly
"""

import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

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
