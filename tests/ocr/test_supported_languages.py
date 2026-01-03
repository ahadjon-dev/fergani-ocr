"""
Integration tests for supported languages endpoint
Tests: GET /api/ocr/languages/
"""

from rest_framework import status
from rest_framework.test import APITestCase


class TestSupportedLanguages(APITestCase):
    """Test suite for supported languages endpoint"""

    def test_supported_languages_case_1(self):
        """
        Case: Get list of supported OCR languages
        Expected: Success with language list
        """
        response = self.client.get("/api/ocr/languages/")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        # Check response structure
        response_data = response.json()
        self.assertIn("success", response_data)
        self.assertTrue(response_data["success"])
        self.assertIn("count", response_data)
        self.assertIn("languages", response_data)

    def test_supported_languages_case_2(self):
        """
        Case: Verify language list contains expected languages
        Expected: Common languages like English, Spanish, etc. are present
        """
        response = self.client.get("/api/ocr/languages/")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        response_data = response.json()
        languages = response_data["languages"]

        # Check that dictionary is not empty
        self.assertGreater(len(languages), 0)

        # Check for common languages
        expected_languages = ["eng", "spa", "fra", "deu"]
        for lang_code in expected_languages:
            self.assertIn(lang_code, languages, f"Language {lang_code} should be supported")

    def test_supported_languages_case_3(self):
        """
        Case: Verify count matches actual number of languages
        Expected: Count field equals length of languages dictionary
        """
        response = self.client.get("/api/ocr/languages/")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        response_data = response.json()
        self.assertEqual(response_data["count"], len(response_data["languages"]))

    def test_supported_languages_case_4(self):
        """
        Case: Verify each language has a name
        Expected: All language codes map to language names
        """
        response = self.client.get("/api/ocr/languages/")

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        response_data = response.json()
        languages = response_data["languages"]

        for code, name in languages.items():
            self.assertIsInstance(code, str)
            self.assertIsInstance(name, str)
            self.assertGreater(len(name), 0)

    def test_supported_languages_case_5(self):
        """
        Case: POST request to languages endpoint
        Expected: Method not allowed
        """
        response = self.client.post("/api/ocr/languages/")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
