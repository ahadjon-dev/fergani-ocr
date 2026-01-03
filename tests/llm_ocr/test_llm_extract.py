"""
Unit tests for LLM OCR Extract API
Tests: LLMOCRExtractView endpoint
"""

import io
from unittest.mock import patch

from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase


class TestLLMOCRExtractView(APITestCase):
    """Test suite for LLM OCR Extract endpoint"""

    def setUp(self):
        """Set up test fixtures"""
        self.url = "/api/v1/llm-ocr/extract/"

    def _create_test_image(self, width=100, height=100, color="white", format="PNG"):
        """Helper to create test image"""
        image = Image.new("RGB", (width, height), color=color)
        image_io = io.BytesIO()
        image.save(image_io, format=format)
        image_io.name = f"test.{format.lower()}"
        image_io.seek(0)
        return image_io

    @patch("llm_ocr.services.LLMOCRService.process_image")
    def test_extract_basic_case_png(self, mock_process):
        """Test basic extraction with PNG image"""
        # Mock service response
        mock_process.return_value = {
            "success": True,
            "text": "Sample extracted text",
            "model": "deepseek-ai/deepseek-vl-7b-chat",
            "language": "eng",
        }

        image = self._create_test_image()
        data = {"image": image, "model": "deepseek-vision", "language": "eng"}

        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["success"], True)
        self.assertEqual(response.data["text"], "Sample extracted text")
        self.assertIn("processing_time", response.data)

    @patch("llm_ocr.services.LLMOCRService.process_image")
    def test_extract_basic_case_jpg(self, mock_process):
        """Test basic extraction with JPG image"""
        mock_process.return_value = {"success": True, "text": "JPG text", "model": "deepseek-vision", "language": "eng"}

        image = self._create_test_image(format="JPEG")
        data = {"image": image, "model": "deepseek-vision"}

        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["success"], True)

    @patch("llm_ocr.services.LLMOCRService.process_image")
    def test_extract_with_all_models(self, mock_process):
        """Test extraction with all available models"""
        mock_process.return_value = {"success": True, "text": "Model test", "model": "test-model", "language": "eng"}

        models = ["deepseek-vision", "qwen-vision", "llava", "microsoft-phi"]

        for model in models:
            image = self._create_test_image()
            data = {"image": image, "model": model, "language": "eng"}

            response = self.client.post(self.url, data, format="multipart")

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["success"], True)

    @patch("llm_ocr.services.LLMOCRService.process_image")
    def test_extract_with_all_languages(self, mock_process):
        """Test extraction with all supported languages"""
        mock_process.return_value = {"success": True, "text": "Language test", "model": "deepseek-vision", "language": "test"}

        languages = ["eng", "kor", "uzb", "uzb_cyrl"]

        for lang in languages:
            image = self._create_test_image()
            data = {"image": image, "language": lang}

            response = self.client.post(self.url, data, format="multipart")

            self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("llm_ocr.services.LLMOCRService.process_image")
    def test_extract_with_custom_prompt(self, mock_process):
        """Test extraction with custom prompt"""
        mock_process.return_value = {
            "success": True,
            "text": "Custom extraction",
            "model": "deepseek-vision",
            "language": "eng",
        }

        image = self._create_test_image()
        data = {"image": image, "custom_prompt": "Extract all dates and amounts"}

        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify custom prompt was passed to service
        mock_process.assert_called_once()
        call_kwargs = mock_process.call_args[1]
        self.assertEqual(call_kwargs["custom_prompt"], "Extract all dates and amounts")

    def test_extract_missing_image(self):
        """Test extraction without image - should fail"""
        data = {"model": "deepseek-vision"}

        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_extract_invalid_image_format(self):
        """Test extraction with invalid image format"""
        # Create a non-image file
        file_io = io.BytesIO(b"Not an image")
        file_io.name = "test.txt"
        file_io.seek(0)

        data = {"image": file_io}

        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_extract_invalid_model(self):
        """Test extraction with invalid model name"""
        image = self._create_test_image()
        data = {"image": image, "model": "invalid-model-xyz"}

        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_extract_invalid_language(self):
        """Test extraction with invalid language code"""
        image = self._create_test_image()
        data = {"image": image, "language": "invalid-lang"}

        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("llm_ocr.services.LLMOCRService.process_image")
    def test_extract_service_error(self, mock_process):
        """Test handling of service errors"""
        mock_process.return_value = {"success": False, "error": "API key not configured"}

        image = self._create_test_image()
        data = {"image": image}

        response = self.client.post(self.url, data, format="multipart")

        # The view returns HTTP 200 even for service errors, includes success=False in response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["success"], False)
        self.assertIn("error", response.data)

    @patch("llm_ocr.services.LLMOCRService.process_image")
    def test_extract_exception_handling(self, mock_process):
        """Test handling of unexpected exceptions"""
        mock_process.side_effect = Exception("Unexpected error")

        image = self._create_test_image()
        data = {"image": image}

        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch("llm_ocr.services.LLMOCRService.process_image")
    def test_extract_large_image(self, mock_process):
        """Test extraction with large image"""
        mock_process.return_value = {
            "success": True,
            "text": "Large image text",
            "model": "deepseek-vision",
            "language": "eng",
        }

        # Create larger image
        image = self._create_test_image(width=2000, height=2000)
        data = {"image": image}

        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_extract_get_method_not_allowed(self):
        """Test that GET method is not allowed"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_extract_put_method_not_allowed(self):
        """Test that PUT method is not allowed"""
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @patch("llm_ocr.services.LLMOCRService.process_image")
    def test_extract_default_values(self, mock_process):
        """Test extraction with default model and language"""
        mock_process.return_value = {
            "success": True,
            "text": "Default values test",
            "model": "deepseek-ai/deepseek-vl-7b-chat",
            "language": "eng",
        }

        image = self._create_test_image()
        data = {"image": image}  # No model or language specified

        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify defaults were used
        call_kwargs = mock_process.call_args[1]
        self.assertEqual(call_kwargs["model"], "deepseek-vision")
        self.assertEqual(call_kwargs["language"], "eng")

    @patch("llm_ocr.services.LLMOCRService.process_image")
    def test_extract_response_structure(self, mock_process):
        """Test response structure contains all expected fields"""
        mock_process.return_value = {
            "success": True,
            "text": "Test",
            "model": "deepseek-vision",
            "language": "eng",
            "confidence": 0.95,
        }

        image = self._create_test_image()
        data = {"image": image}

        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("success", response.data)
        self.assertIn("text", response.data)
        self.assertIn("model", response.data)
        self.assertIn("language", response.data)
        self.assertIn("processing_time", response.data)

    @patch("llm_ocr.services.LLMOCRService.process_image")
    def test_extract_empty_response(self, mock_process):
        """Test extraction with empty text result"""
        mock_process.return_value = {"success": True, "text": "", "model": "deepseek-vision", "language": "eng"}

        image = self._create_test_image()
        data = {"image": image}

        response = self.client.post(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], "")
