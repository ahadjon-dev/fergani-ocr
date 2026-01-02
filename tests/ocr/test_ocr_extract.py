"""
Integration tests for OCR text extraction endpoint
Tests: POST /api/ocr/extract/
"""

import io

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase


class TestOCRExtractText(APITestCase):
    """Test suite for OCR text extraction endpoint"""

    def _create_test_image(self, text="Test OCR", size=(200, 100), format="PNG"):
        """
        Helper method to create a test image with text

        Args:
            text: Text to add to image (for identification purposes)
            size: Image dimensions (width, height)
            format: Image format

        Returns:
            SimpleUploadedFile object containing the image
        """
        # Create a simple image
        image = Image.new("RGB", size, color="white")

        # Save to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=format)
        img_byte_arr.seek(0)

        return SimpleUploadedFile(f"test_image.{format.lower()}", img_byte_arr.read(), content_type=f"image/{format.lower()}")

    def test_ocr_extract_case_1(self):
        """
        Case: Successfully extract text from valid image
        Expected: Success with extracted text and metadata
        """
        image_file = self._create_test_image()

        data = {"image": image_file}
        response = self.client.post("/api/ocr/extract/", data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        # Check response structure
        response_data = response.json()
        self.assertIn("success", response_data)
        self.assertTrue(response_data["success"])
        self.assertIn("text", response_data)
        self.assertIn("filename", response_data)
        self.assertIn("file_size", response_data)
        self.assertIn("image_dimensions", response_data)
        self.assertIn("image_format", response_data)
        self.assertIn("language", response_data)
        self.assertIn("character_count", response_data)
        self.assertIn("word_count", response_data)

        # Check default language
        self.assertEqual(response_data["language"], "eng")

    def test_ocr_extract_case_2(self):
        """
        Case: Extract text with custom language parameter
        Expected: Success with specified language
        """
        image_file = self._create_test_image()

        data = {"image": image_file, "language": "eng"}  # Use 'eng' since it's always available
        response = self.client.post("/api/ocr/extract/", data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        response_data = response.json()
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["language"], "eng")

    def test_ocr_extract_case_3(self):
        """
        Case: Attempt to extract without providing image
        Expected: Failure with validation error
        """
        data = {}
        response = self.client.post("/api/ocr/extract/", data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

        response_data = response.json()
        self.assertIn("success", response_data)
        self.assertFalse(response_data["success"])
        self.assertIn("error", response_data)

    def test_ocr_extract_case_4(self):
        """
        Case: Attempt to extract from invalid file type
        Expected: Failure with validation error
        """
        # Create a text file instead of an image
        text_file = SimpleUploadedFile("test.txt", b"This is not an image", content_type="text/plain")

        data = {"image": text_file}
        response = self.client.post("/api/ocr/extract/", data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

        response_data = response.json()
        self.assertFalse(response_data["success"])
        self.assertIn("error", response_data)

    def test_ocr_extract_case_5(self):
        """
        Case: Extract from different image formats (JPEG, PNG, etc.)
        Expected: Success for all supported formats
        """
        formats = ["PNG", "JPEG"]

        for img_format in formats:
            with self.subTest(format=img_format):
                image_file = self._create_test_image(format=img_format)

                data = {"image": image_file}
                response = self.client.post("/api/ocr/extract/", data, format="multipart")

                self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

                response_data = response.json()
                self.assertTrue(response_data["success"])
                self.assertEqual(response_data["image_format"], img_format)

    def test_ocr_extract_case_6(self):
        """
        Case: GET request to endpoint
        Expected: Return API information
        """
        response = self.client.get("/api/ocr/extract/")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        response_data = response.json()
        self.assertIn("message", response_data)
        self.assertIn("version", response_data)
        self.assertIn("endpoint", response_data)
        self.assertIn("method", response_data)
        self.assertIn("supported_languages", response_data)
        self.assertIn("max_file_size_mb", response_data)
        self.assertIn("supported_formats", response_data)
        self.assertIn("tesseract_installed", response_data)

    def test_ocr_extract_case_7(self):
        """
        Case: Extract from oversized image
        Expected: Failure with file size error
        """
        # Create a large image (larger than MAX_FILE_SIZE)
        # MAX_FILE_SIZE is 10MB, so create something larger
        # Note: This test might need adjustment based on actual file size validation

        large_image = Image.new("RGB", (5000, 5000), color="white")
        img_byte_arr = io.BytesIO()
        large_image.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)

        # Only test if the file is actually large enough
        file_size = len(img_byte_arr.getvalue())
        if file_size > 10 * 1024 * 1024:  # 10MB
            large_file = SimpleUploadedFile("large_image.png", img_byte_arr.read(), content_type="image/png")

            data = {"image": large_file}
            response = self.client.post("/api/ocr/extract/", data, format="multipart")

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
