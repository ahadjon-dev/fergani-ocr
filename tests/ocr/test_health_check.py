"""
Integration tests for OCR health check endpoint
Tests: GET /api/ocr/health/
"""

from rest_framework import status
from rest_framework.test import APITestCase


class TestOCRHealthCheck(APITestCase):
    """Test suite for OCR health check endpoint"""

    def test_health_check_case_1(self):
        """
        Case: Check OCR service health status
        Expected: Success with health information
        """
        response = self.client.get("/api/ocr/health/")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        # Check response structure
        response_data = response.json()
        self.assertIn("status", response_data)
        self.assertIn("tesseract_installed", response_data)
        self.assertIn("tesseract_version", response_data)
        self.assertIn("supported_languages", response_data)

        # Status should be either 'healthy' or 'unhealthy'
        self.assertIn(response_data["status"], ["healthy", "unhealthy"])

    def test_health_check_case_2(self):
        """
        Case: Verify health status reflects Tesseract installation
        Expected: Consistent health status and installation flag
        """
        response = self.client.get("/api/ocr/health/")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        response_data = response.json()

        # If tesseract is installed, status should be healthy
        if response_data["tesseract_installed"]:
            self.assertEqual(response_data["status"], "healthy")
            self.assertIsNotNone(response_data["tesseract_version"])
        else:
            self.assertEqual(response_data["status"], "unhealthy")

    def test_health_check_case_3(self):
        """
        Case: Verify supported languages count is reasonable
        Expected: At least 1 language supported
        """
        response = self.client.get("/api/ocr/health/")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        response_data = response.json()
        self.assertGreaterEqual(response_data["supported_languages"], 1)

    def test_health_check_case_4(self):
        """
        Case: POST request to health check endpoint
        Expected: Method not allowed
        """
        response = self.client.post("/api/ocr/health/")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
