"""
Unit tests for LLM OCR Serializers
"""

import io

from django.test import TestCase
from PIL import Image

from llm_ocr.serializers import LLMOCRExtractSerializer, LLMOCRResponseSerializer, ModelListSerializer


class TestLLMOCRExtractSerializer(TestCase):
    """Test suite for LLMOCRExtractSerializer"""

    def _create_test_image(self, format="PNG"):
        """Helper to create test image file"""
        image = Image.new("RGB", (100, 100), color="white")
        image_io = io.BytesIO()
        image.save(image_io, format=format)
        image_io.name = f"test.{format.lower()}"
        image_io.seek(0)
        return image_io

    def test_serializer_valid_data(self):
        """Test serializer with valid data"""
        from django.core.files.uploadedfile import SimpleUploadedFile

        image = self._create_test_image()
        uploaded_file = SimpleUploadedFile(name="test.png", content=image.read(), content_type="image/png")

        data = {"image": uploaded_file, "model": "deepseek-vision", "language": "eng"}

        serializer = LLMOCRExtractSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_valid_jpg(self):
        """Test serializer with JPG image"""
        from django.core.files.uploadedfile import SimpleUploadedFile

        image = self._create_test_image(format="JPEG")
        uploaded_file = SimpleUploadedFile(name="test.jpg", content=image.read(), content_type="image/jpeg")

        data = {"image": uploaded_file}
        serializer = LLMOCRExtractSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_missing_image(self):
        """Test serializer without image - should fail"""
        data = {"model": "deepseek-vision"}
        serializer = LLMOCRExtractSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("image", serializer.errors)

    def test_serializer_invalid_model(self):
        """Test serializer with invalid model"""
        from django.core.files.uploadedfile import SimpleUploadedFile

        image = self._create_test_image()
        uploaded_file = SimpleUploadedFile(name="test.png", content=image.read(), content_type="image/png")

        data = {"image": uploaded_file, "model": "invalid-model-xyz"}

        serializer = LLMOCRExtractSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("model", serializer.errors)

    def test_serializer_invalid_language(self):
        """Test serializer with invalid language"""
        from django.core.files.uploadedfile import SimpleUploadedFile

        image = self._create_test_image()
        uploaded_file = SimpleUploadedFile(name="test.png", content=image.read(), content_type="image/png")

        data = {"image": uploaded_file, "language": "invalid-lang"}

        serializer = LLMOCRExtractSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("language", serializer.errors)

    def test_serializer_all_valid_models(self):
        """Test serializer with all valid model choices"""
        from django.core.files.uploadedfile import SimpleUploadedFile

        valid_models = ["deepseek-vision", "qwen-vision", "llava", "microsoft-phi"]

        for model in valid_models:
            image = self._create_test_image()
            uploaded_file = SimpleUploadedFile(name="test.png", content=image.read(), content_type="image/png")

            data = {"image": uploaded_file, "model": model}
            serializer = LLMOCRExtractSerializer(data=data)
            self.assertTrue(serializer.is_valid(), f"Model {model} should be valid")

    def test_serializer_all_valid_languages(self):
        """Test serializer with all valid language choices"""
        from django.core.files.uploadedfile import SimpleUploadedFile

        valid_languages = ["eng", "kor", "uzb", "uzb_cyrl"]

        for lang in valid_languages:
            image = self._create_test_image()
            uploaded_file = SimpleUploadedFile(name="test.png", content=image.read(), content_type="image/png")

            data = {"image": uploaded_file, "language": lang}
            serializer = LLMOCRExtractSerializer(data=data)
            self.assertTrue(serializer.is_valid(), f"Language {lang} should be valid")

    def test_serializer_custom_prompt(self):
        """Test serializer with custom prompt"""
        from django.core.files.uploadedfile import SimpleUploadedFile

        image = self._create_test_image()
        uploaded_file = SimpleUploadedFile(name="test.png", content=image.read(), content_type="image/png")

        data = {"image": uploaded_file, "custom_prompt": "Extract all dates and amounts"}

        serializer = LLMOCRExtractSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["custom_prompt"], "Extract all dates and amounts")

    def test_serializer_default_values(self):
        """Test serializer uses default values"""
        from django.core.files.uploadedfile import SimpleUploadedFile

        image = self._create_test_image()
        uploaded_file = SimpleUploadedFile(name="test.png", content=image.read(), content_type="image/png")

        data = {"image": uploaded_file}
        serializer = LLMOCRExtractSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["model"], "deepseek-vision")
        self.assertEqual(serializer.validated_data["language"], "eng")


class TestLLMOCRResponseSerializer(TestCase):
    """Test suite for LLMOCRResponseSerializer"""

    def test_response_serializer_success(self):
        """Test response serializer with successful data"""
        data = {"success": True, "text": "Sample text", "model": "deepseek-vision", "language": "eng", "processing_time": 1.23}

        serializer = LLMOCRResponseSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_response_serializer_error(self):
        """Test response serializer with error data"""
        data = {"success": False, "error": "API key not configured", "model": "deepseek-vision"}

        serializer = LLMOCRResponseSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_response_serializer_minimal(self):
        """Test response serializer with minimal required fields"""
        data = {"success": True, "model": "deepseek-vision"}
        serializer = LLMOCRResponseSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class TestModelListSerializer(TestCase):
    """Test suite for ModelListSerializer"""

    def test_model_list_serializer(self):
        """Test model list serializer"""
        data = {"models": {"deepseek-vision": "deepseek-ai/deepseek-vl-7b-chat", "qwen-vision": "Qwen/Qwen2-VL-7B-Instruct"}}

        serializer = ModelListSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_model_list_serializer_multiple_models(self):
        """Test model list serializer with multiple models"""
        from llm_ocr.services import LLMOCRService

        models = LLMOCRService.get_available_models()
        data = {"models": models}

        serializer = ModelListSerializer(data=data)
        self.assertTrue(serializer.is_valid())
