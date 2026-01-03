"""
Unit tests for LLM OCR Services
Tests: HuggingFaceOCRClient and LLMOCRService
"""

import base64
import unittest
from unittest.mock import MagicMock, patch

from PIL import Image

from llm_ocr.services import HuggingFaceOCRClient, LLMOCRService


class TestHuggingFaceOCRClient(unittest.TestCase):
    """Test suite for HuggingFaceOCRClient"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key_12345"
        self.test_image = Image.new("RGB", (100, 100), color="white")

    def test_init_with_api_key(self):
        """Test client initialization with API key"""
        client = HuggingFaceOCRClient(api_key=self.api_key)
        self.assertEqual(client.api_key, self.api_key)
        self.assertEqual(client.model, "deepseek-ai/deepseek-vl-7b-chat")

    def test_init_without_api_key_raises_error(self):
        """Test client initialization without API key raises ValueError"""
        # Patch settings to ensure no API key
        with patch("llm_ocr.services.settings") as mock_settings:
            mock_settings.HUGGINGFACE_API_KEY = ""
            with self.assertRaises(ValueError) as context:
                HuggingFaceOCRClient(api_key=None)
            self.assertIn("API key is required", str(context.exception))

    def test_init_with_custom_model(self):
        """Test client initialization with custom model alias"""
        client = HuggingFaceOCRClient(api_key=self.api_key, model="qwen-vision")
        self.assertEqual(client.model, "Qwen/Qwen2-VL-7B-Instruct")

    def test_init_with_full_model_id(self):
        """Test client initialization with full model ID"""
        custom_model = "custom-org/custom-model"
        client = HuggingFaceOCRClient(api_key=self.api_key, model=custom_model)
        self.assertEqual(client.model, custom_model)

    def test_encode_image(self):
        """Test image encoding to base64"""
        client = HuggingFaceOCRClient(api_key=self.api_key)
        encoded = client._encode_image(self.test_image)

        # Verify it's a valid base64 string
        self.assertIsInstance(encoded, str)
        # Verify it can be decoded
        decoded = base64.b64decode(encoded)
        self.assertIsInstance(decoded, bytes)

    @patch("requests.post")
    def test_extract_text_success(self, mock_post):
        """Test successful text extraction"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"generated_text": "Extracted text from image"}
        mock_post.return_value = mock_response

        client = HuggingFaceOCRClient(api_key=self.api_key)
        result = client.extract_text(self.test_image, language="eng")

        self.assertEqual(result["success"], True)
        self.assertEqual(result["text"], "Extracted text from image")
        self.assertEqual(result["model"], "deepseek-ai/deepseek-vl-7b-chat")
        self.assertEqual(result["language"], "eng")

    @patch("requests.post")
    def test_extract_text_with_custom_prompt(self, mock_post):
        """Test text extraction with custom prompt"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"generated_text": "Custom extraction result"}
        mock_post.return_value = mock_response

        client = HuggingFaceOCRClient(api_key=self.api_key)
        result = client.extract_text(self.test_image, prompt="Extract all dates", language="eng")

        # Verify custom prompt was used
        call_args = mock_post.call_args
        self.assertIn("Extract all dates", str(call_args))
        self.assertEqual(result["success"], True)

    @patch("requests.post")
    def test_extract_text_api_error(self, mock_post):
        """Test handling of API errors"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal server error"}
        mock_post.return_value = mock_response

        client = HuggingFaceOCRClient(api_key=self.api_key)
        result = client.extract_text(self.test_image)

        self.assertEqual(result["success"], False)
        self.assertIn("error", result)

    @patch("requests.post")
    def test_extract_text_network_error(self, mock_post):
        """Test handling of network errors"""
        mock_post.side_effect = Exception("Network error")

        client = HuggingFaceOCRClient(api_key=self.api_key)
        result = client.extract_text(self.test_image)

        self.assertEqual(result["success"], False)
        self.assertIn("Network error", result["error"])

    @patch("requests.post")
    def test_extract_text_all_languages(self, mock_post):
        """Test text extraction with different languages"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"generated_text": "Text"}
        mock_post.return_value = mock_response

        client = HuggingFaceOCRClient(api_key=self.api_key)

        languages = ["eng", "kor", "uzb", "uzb_cyrl"]
        for lang in languages:
            result = client.extract_text(self.test_image, language=lang)
            self.assertEqual(result["success"], True)
            self.assertEqual(result["language"], lang)

    @patch("requests.post")
    def test_extract_structured_data(self, mock_post):
        """Test structured data extraction"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"generated_text": '{"name": "John", "date": "2024-01-01"}'}
        mock_post.return_value = mock_response

        client = HuggingFaceOCRClient(api_key=self.api_key)
        result = client.extract_structured_data(self.test_image, fields=["name", "date"])

        self.assertEqual(result["success"], True)
        self.assertIn("structured_data", result)

    def test_get_available_models(self):
        """Test getting available models list"""
        models = LLMOCRService.get_available_models()

        self.assertIsInstance(models, dict)
        self.assertIn("deepseek-vision", models)
        self.assertIn("qwen-vision", models)
        self.assertIn("llava", models)
        self.assertIn("microsoft-phi", models)
        self.assertEqual(len(models), 4)
        # Verify values are model IDs
        self.assertEqual(models["deepseek-vision"], "deepseek-ai/deepseek-vl-7b-chat")


class TestLLMOCRService(unittest.TestCase):
    """Test suite for LLMOCRService"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_image = Image.new("RGB", (100, 100), color="white")

    @patch("llm_ocr.services.HuggingFaceOCRClient")
    def test_process_image_success(self, mock_client_class):
        """Test successful image processing"""
        # Mock the client
        mock_client = MagicMock()
        mock_client.extract_text.return_value = {
            "success": True,
            "text": "Test text",
            "model": "deepseek-vision",
            "language": "eng",
        }
        mock_client_class.return_value = mock_client

        result = LLMOCRService.process_image(self.test_image, model="deepseek-vision", language="eng")

        self.assertEqual(result["success"], True)
        self.assertEqual(result["text"], "Test text")
        mock_client.extract_text.assert_called_once()

    @patch.dict("os.environ", {}, clear=True)
    def test_process_image_no_api_key(self):
        """Test processing without API key"""
        from django.conf import settings

        settings.HUGGINGFACE_API_KEY = ""

        result = LLMOCRService.process_image(self.test_image, model="deepseek-vision")

        self.assertEqual(result["success"], False)
        self.assertIn("API key", result["error"])

    @patch("llm_ocr.services.HuggingFaceOCRClient")
    def test_process_image_with_custom_prompt(self, mock_client_class):
        """Test processing with custom prompt"""
        mock_client = MagicMock()
        mock_client.extract_text.return_value = {"success": True, "text": "Custom result"}
        mock_client_class.return_value = mock_client

        LLMOCRService.process_image(self.test_image, custom_prompt="Extract dates")  # noqa: F841

        # Verify custom prompt was passed
        call_args = mock_client.extract_text.call_args
        self.assertEqual(call_args[1]["prompt"], "Extract dates")

    @patch("llm_ocr.services.HuggingFaceOCRClient")
    def test_process_image_exception_handling(self, mock_client_class):
        """Test exception handling during processing"""
        mock_client = MagicMock()
        mock_client.extract_text.side_effect = Exception("Processing error")
        mock_client_class.return_value = mock_client

        result = LLMOCRService.process_image(self.test_image)

        self.assertEqual(result["success"], False)
        self.assertIn("Processing error", result["error"])

    # extract_from_file_path method doesn't exist in current implementation
    # Removing these tests as they test non-existent functionality


if __name__ == "__main__":
    unittest.main()
