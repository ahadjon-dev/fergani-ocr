"""
Additional tests for edge cases in LLM OCR services
"""

import unittest
from unittest.mock import MagicMock, patch

from PIL import Image

from llm_ocr.services import HuggingFaceOCRClient


class TestHuggingFaceOCRClientEdgeCases(unittest.TestCase):
    """Test edge cases and alternative code paths"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key_12345"
        self.test_image = Image.new("RGB", (100, 100), color="white")

    @patch("requests.post")
    def test_parse_response_with_answer_field(self, mock_post):
        """Test response parsing with 'answer' field"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"answer": "Extracted answer text"}
        mock_post.return_value = mock_response

        client = HuggingFaceOCRClient(api_key=self.api_key)
        result = client.extract_text(self.test_image)

        self.assertEqual(result["success"], True)
        self.assertEqual(result["text"], "Extracted answer text")

    @patch("requests.post")
    def test_parse_response_with_text_field(self, mock_post):
        """Test response parsing with 'text' field"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"text": "Direct text response"}
        mock_post.return_value = mock_response

        client = HuggingFaceOCRClient(api_key=self.api_key)
        result = client.extract_text(self.test_image)

        self.assertEqual(result["success"], True)
        self.assertEqual(result["text"], "Direct text response")

    @patch("requests.post")
    def test_parse_response_list_with_generated_text(self, mock_post):
        """Test response parsing with list containing generated_text"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"generated_text": "List response text"}]
        mock_post.return_value = mock_response

        client = HuggingFaceOCRClient(api_key=self.api_key)
        result = client.extract_text(self.test_image)

        self.assertEqual(result["success"], True)
        self.assertEqual(result["text"], "List response text")

    @patch("requests.post")
    def test_parse_response_list_with_answer(self, mock_post):
        """Test response parsing with list containing answer"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"answer": "List answer response"}]
        mock_post.return_value = mock_response

        client = HuggingFaceOCRClient(api_key=self.api_key)
        result = client.extract_text(self.test_image)

        self.assertEqual(result["success"], True)
        self.assertEqual(result["text"], "List answer response")

    @patch("requests.post")
    def test_parse_response_fallback_to_string(self, mock_post):
        """Test response parsing fallback to string conversion"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = 12345  # Non-dict, non-list response
        mock_post.return_value = mock_response

        client = HuggingFaceOCRClient(api_key=self.api_key)
        result = client.extract_text(self.test_image)

        self.assertEqual(result["success"], True)
        self.assertEqual(result["text"], "12345")

    @patch("requests.post")
    def test_extract_structured_data_success_with_json_parsing(self, mock_post):
        """Test structured data extraction with successful JSON parsing"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"generated_text": 'Some text before {"name": "John", "age": 30} some text after'}
        mock_post.return_value = mock_response

        client = HuggingFaceOCRClient(api_key=self.api_key)
        result = client.extract_structured_data(self.test_image, fields=["name", "age"])

        self.assertEqual(result["success"], True)
        self.assertIn("structured_data", result)
        self.assertEqual(result["structured_data"]["name"], "John")
        self.assertEqual(result["structured_data"]["age"], 30)

    @patch("requests.post")
    def test_extract_structured_data_no_json_in_response(self, mock_post):
        """Test structured data extraction when no JSON in response"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"generated_text": "Just plain text without JSON"}
        mock_post.return_value = mock_response

        client = HuggingFaceOCRClient(api_key=self.api_key)
        result = client.extract_structured_data(self.test_image, fields=["name"])

        # Should still succeed but without structured_data field
        self.assertEqual(result["success"], True)
        self.assertNotIn("structured_data", result)


if __name__ == "__main__":
    unittest.main()
