"""
Unit tests for LLM OCR Health Check and Models endpoints
"""

from rest_framework import status
from rest_framework.test import APITestCase


class TestLLMOCRHealthView(APITestCase):
    """Test suite for LLM OCR Health Check endpoint"""

    def setUp(self):
        """Set up test fixtures"""
        self.url = "/api/v1/llm-ocr/health/"

    def test_health_check_success(self):
        """Test health check returns 200 OK"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Status can be 'healthy' or 'not_configured' depending on API key
        self.assertIn(response.data["status"], ["healthy", "not_configured"])

    def test_health_check_structure(self):
        """Test health check response structure"""
        response = self.client.get(self.url)

        self.assertIn("status", response.data)
        self.assertIn("configured", response.data)
        self.assertIn("available_models", response.data)

    def test_health_check_configured_field(self):
        """Test health check includes configured boolean"""
        response = self.client.get(self.url)

        configured = response.data.get("configured")
        self.assertIsNotNone(configured)
        self.assertIsInstance(configured, bool)

    def test_health_check_post_not_allowed(self):
        """Test POST method is not allowed"""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_health_check_put_not_allowed(self):
        """Test PUT method is not allowed"""
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_health_check_delete_not_allowed(self):
        """Test DELETE method is not allowed"""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class TestAvailableModelsView(APITestCase):
    """Test suite for Available Models endpoint"""

    def setUp(self):
        """Set up test fixtures"""
        self.url = "/api/v1/llm-ocr/models/"

    def test_models_list_success(self):
        """Test models list returns 200 OK"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("models", response.data)

    def test_models_list_structure(self):
        """Test models list response structure"""
        response = self.client.get(self.url)

        models = response.data["models"]
        self.assertIsInstance(models, dict)

        # Check all expected models are present
        expected_models = ["deepseek-vision", "qwen-vision", "llava", "microsoft-phi"]
        for model in expected_models:
            self.assertIn(model, models)
            # Models dict maps aliases to model IDs (strings)
            self.assertIsInstance(models[model], str)

    def test_models_list_deepseek_details(self):
        """Test DeepSeek model ID"""
        response = self.client.get(self.url)

        deepseek_id = response.data["models"]["deepseek-vision"]
        self.assertEqual(deepseek_id, "deepseek-ai/deepseek-vl-7b-chat")

    def test_models_list_qwen_details(self):
        """Test Qwen model ID"""
        response = self.client.get(self.url)

        qwen_id = response.data["models"]["qwen-vision"]
        self.assertEqual(qwen_id, "Qwen/Qwen2-VL-7B-Instruct")

    def test_models_list_llava_details(self):
        """Test LLaVA model ID"""
        response = self.client.get(self.url)

        llava_id = response.data["models"]["llava"]
        self.assertEqual(llava_id, "llava-hf/llava-1.5-7b-hf")

    def test_models_list_phi_details(self):
        """Test Microsoft Phi model ID"""
        response = self.client.get(self.url)

        phi_id = response.data["models"]["microsoft-phi"]
        self.assertEqual(phi_id, "microsoft/Phi-3-vision-128k-instruct")

    def test_models_list_count(self):
        """Test correct number of models returned"""
        response = self.client.get(self.url)

        models = response.data["models"]
        self.assertEqual(len(models), 4)

    def test_models_list_post_not_allowed(self):
        """Test POST method is not allowed"""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_models_list_put_not_allowed(self):
        """Test PUT method is not allowed"""
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_models_list_delete_not_allowed(self):
        """Test DELETE method is not allowed"""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_models_all_have_required_fields(self):
        """Test all models are valid model IDs"""
        response = self.client.get(self.url)

        models = response.data["models"]

        for model_key, model_id in models.items():
            # Model ID should be a non-empty string
            self.assertIsInstance(model_id, str)
            self.assertTrue(len(model_id) > 0, f"Model {model_key} has empty ID")

    def test_models_description_not_empty(self):
        """Test all models have non-empty IDs"""
        response = self.client.get(self.url)

        models = response.data["models"]
        for model_key, model_id in models.items():
            self.assertTrue(len(model_id) > 0, f"Model {model_key} has empty ID")
