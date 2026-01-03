"""
LLM-based OCR service using Hugging Face Inference API
Supports vision language models like DeepSeek for advanced document understanding
"""

import base64
import io
import logging
from typing import Any, Dict, List, Optional

import requests
from django.conf import settings
from PIL import Image

logger = logging.getLogger(__name__)


class HuggingFaceOCRClient:
    """
    Client for Hugging Face Inference API for vision-language models
    """

    # Recommended OCR models
    DEFAULT_MODELS = {
        "deepseek-vision": "deepseek-ai/deepseek-vl-7b-chat",
        "qwen-vision": "Qwen/Qwen2-VL-7B-Instruct",
        "llava": "llava-hf/llava-1.5-7b-hf",
        "microsoft-phi": "microsoft/Phi-3-vision-128k-instruct",
    }

    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-vision"):
        """
        Initialize the Hugging Face OCR client

        Args:
            api_key: Hugging Face API token
            model: Model identifier or alias
        """
        self.api_key = api_key or getattr(settings, "HUGGINGFACE_API_KEY", None)
        if not self.api_key:
            raise ValueError("Hugging Face API key is required. Set HUGGINGFACE_API_KEY in settings.")

        # Get the actual model ID
        self.model = self.DEFAULT_MODELS.get(model, model)
        # Updated to new Hugging Face router endpoint (api-inference.huggingface.co deprecated)
        self.api_url = f"https://router.huggingface.co/models/{self.model}"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

        logger.info(f"Initialized HuggingFace OCR client with model: {self.model}")

    def _encode_image(self, image: Image.Image) -> str:
        """
        Encode PIL Image to base64 string

        Args:
            image: PIL Image object

        Returns:
            Base64 encoded string
        """
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        return base64.b64encode(img_bytes).decode("utf-8")

    def extract_text(
        self, image: Image.Image, prompt: Optional[str] = None, language: str = "eng", **kwargs
    ) -> Dict[str, Any]:
        """
        Extract text from image using vision-language model

        Args:
            image: PIL Image object
            prompt: Custom prompt for the model (optional)
            language: Target language for extraction
            **kwargs: Additional parameters

        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            # Default prompt for OCR
            if not prompt:
                lang_names = {
                    "eng": "English",
                    "kor": "Korean",
                    "uzb": "Uzbek (Latin)",
                    "uzb_cyrl": "Uzbek (Cyrillic)",
                }
                lang_name = lang_names.get(language, language)
                prompt = f"Extract all text from this image in {lang_name}. Provide only the extracted text without any additional explanation."

            # Encode image
            image_base64 = self._encode_image(image)

            # Prepare payload
            payload = {"inputs": {"image": image_base64, "question": prompt}, "parameters": kwargs}

            # Make API request
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()

                # Extract text from response (format varies by model)
                extracted_text = self._parse_response(result)

                return {
                    "success": True,
                    "text": extracted_text,
                    "model": self.model,
                    "language": language,
                    "raw_response": result,
                }
            else:
                error_msg = f"API request failed with status {response.status_code}: {response.text}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg, "model": self.model}

        except Exception as e:
            logger.exception(f"Error during LLM OCR extraction: {str(e)}")
            return {"success": False, "error": str(e), "model": self.model}

    def _parse_response(self, response: Any) -> str:
        """
        Parse the API response to extract text

        Args:
            response: API response object

        Returns:
            Extracted text string
        """
        # Handle different response formats
        if isinstance(response, dict):
            # Check common response fields
            if "generated_text" in response:
                return response["generated_text"]
            elif "answer" in response:
                return response["answer"]
            elif "text" in response:
                return response["text"]

        elif isinstance(response, list) and len(response) > 0:
            first_item = response[0]
            if isinstance(first_item, dict):
                if "generated_text" in first_item:
                    return first_item["generated_text"]
                elif "answer" in first_item:
                    return first_item["answer"]

        # Fallback: convert to string
        return str(response)

    def extract_structured_data(self, image: Image.Image, fields: List[str], language: str = "eng") -> Dict[str, Any]:
        """
        Extract structured data from document image

        Args:
            image: PIL Image object
            fields: List of fields to extract (e.g., ['name', 'date', 'amount'])
            language: Target language

        Returns:
            Dictionary with extracted structured data
        """
        fields_str = ", ".join(fields)
        prompt = f"Extract the following information from this document: {fields_str}. Return the result as JSON."

        result = self.extract_text(image, prompt=prompt, language=language)

        if result["success"]:
            # Try to parse structured data from response
            try:
                import json

                text = result["text"]
                # Attempt to extract JSON from the response
                # This is a simple approach - might need refinement based on model behavior
                if "{" in text and "}" in text:
                    json_start = text.index("{")
                    json_end = text.rindex("}") + 1
                    json_str = text[json_start:json_end]
                    structured_data = json.loads(json_str)
                    result["structured_data"] = structured_data
            except Exception as e:
                logger.warning(f"Could not parse structured data: {e}")

        return result


class LLMOCRService:
    """
    Service layer for LLM-based OCR operations
    """

    @staticmethod
    def process_image(
        image: Image.Image,
        model: str = "deepseek-vision",
        language: str = "eng",
        custom_prompt: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Process image using LLM-based OCR

        Args:
            image: PIL Image object
            model: Model to use
            language: Target language
            custom_prompt: Custom extraction prompt
            **kwargs: Additional parameters

        Returns:
            Dictionary with extraction results
        """
        try:
            client = HuggingFaceOCRClient(model=model)
            result = client.extract_text(image=image, prompt=custom_prompt, language=language, **kwargs)
            return result

        except Exception as e:
            logger.exception(f"Error in LLM OCR service: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_available_models() -> Dict[str, str]:
        """
        Get list of available OCR models

        Returns:
            Dictionary of model aliases and their IDs
        """
        return HuggingFaceOCRClient.DEFAULT_MODELS.copy()
