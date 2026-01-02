"""
Integration tests for PDF text extraction endpoint
Tests: POST /api/pdf/extract/
"""

import io
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase


class TestPDFExtractText(APITestCase):
    """Test suite for PDF text extraction endpoint"""

    def _create_test_pdf(self, content=b"Test PDF content"):
        """
        Helper method to create a test PDF file

        Note: This creates a mock PDF for testing purposes.
        For real PDF tests, you would use a library like reportlab or pypdf2
        """
        return SimpleUploadedFile("test.pdf", content, content_type="application/pdf")

    def test_pdf_extract_case_1(self):
        """
        Case: GET request to PDF extract endpoint
        Expected: Return API information
        """
        response = self.client.get("/api/pdf/extract/")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        # Check response structure
        response_data = response.json()
        self.assertIn("message", response_data)
        self.assertIn("version", response_data)
        self.assertIn("endpoint", response_data)
        self.assertIn("method", response_data)
        self.assertIn("pdf_support_available", response_data)
        self.assertIn("supported_languages", response_data)
        self.assertIn("max_file_size_mb", response_data)
        self.assertIn("features", response_data)
        self.assertIn("parameters", response_data)

    def test_pdf_extract_case_2(self):
        """
        Case: Attempt to extract without providing file
        Expected: Failure with validation error
        """
        data = {}
        response = self.client.post("/api/pdf/extract/", data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

        response_data = response.json()
        self.assertIn("success", response_data)
        self.assertFalse(response_data["success"])
        self.assertIn("error", response_data)

    def test_pdf_extract_case_3(self):
        """
        Case: Attempt to extract from invalid file type
        Expected: Failure with validation error
        """
        # Create a text file instead of PDF
        text_file = SimpleUploadedFile("test.txt", b"This is not a PDF", content_type="text/plain")

        data = {"file": text_file}
        response = self.client.post("/api/pdf/extract/", data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

        response_data = response.json()
        self.assertFalse(response_data["success"])
        self.assertIn("error", response_data)

    def test_pdf_extract_case_4(self):
        """
        Case: Check PDF support availability
        Expected: Response indicates if PDF libraries are installed
        """
        response = self.client.get("/api/pdf/extract/")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        response_data = response.json()
        self.assertIsInstance(response_data["pdf_support_available"], bool)

    def test_pdf_extract_case_5(self):
        """
        Case: Verify parameters documentation
        Expected: All required parameters are documented
        """
        response = self.client.get("/api/pdf/extract/")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        response_data = response.json()
        parameters = response_data["parameters"]

        self.assertIn("file", parameters)
        self.assertIn("language", parameters)
        self.assertIn("use_ocr", parameters)
        self.assertIn("pages", parameters)

    def test_pdf_extract_case_6(self):
        """
        Case: Verify features are listed
        Expected: Feature list includes key capabilities
        """
        response = self.client.get("/api/pdf/extract/")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        response_data = response.json()
        features = response_data["features"]

        self.assertIsInstance(features, list)
        self.assertGreater(len(features), 0)


class TestPDFExtractErrorHandling(APITestCase):
    """Test error handling in PDF extraction endpoint"""

    def _create_test_pdf(self, content=b"Test PDF content"):
        """Helper to create test PDF"""
        return SimpleUploadedFile("test.pdf", content, content_type="application/pdf")

    @patch("ocr.pdf_views.OCRProcessor.is_pdf_support_available")
    def test_pdf_support_not_available(self, mock_support):
        """Test error when PDF support is not available"""
        mock_support.return_value = False

        pdf_file = self._create_test_pdf()
        data = {"file": pdf_file}
        response = self.client.post("/api/pdf/extract/", data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        response_data = response.json()
        self.assertFalse(response_data["success"])
        self.assertIn("PDF support not available", response_data["error"])

    @patch("ocr.pdf_views.OCRProcessor.is_pdf_support_available")
    @patch("ocr.pdf_views.PDFService.process_pdf_extraction")
    def test_import_error_handling(self, mock_process, mock_support):
        """Test handling of ImportError during processing"""
        mock_support.return_value = True
        mock_process.side_effect = ImportError("Missing library")

        pdf_file = self._create_test_pdf()
        data = {"file": pdf_file}
        response = self.client.post("/api/pdf/extract/", data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        response_data = response.json()
        self.assertFalse(response_data["success"])

    @patch("ocr.pdf_views.OCRProcessor.is_pdf_support_available")
    @patch("ocr.pdf_views.PDFService.process_pdf_extraction")
    def test_generic_processing_error(self, mock_process, mock_support):
        """Test handling of generic processing errors"""
        mock_support.return_value = True
        mock_process.side_effect = Exception("Processing failed")

        pdf_file = self._create_test_pdf()
        data = {"file": pdf_file}
        response = self.client.post("/api/pdf/extract/", data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        response_data = response.json()
        self.assertFalse(response_data["success"])
        self.assertIn("Error processing PDF", response_data["error"])
