"""
Serializers for LLM OCR API
"""

from rest_framework import serializers


class LLMOCRExtractSerializer(serializers.Serializer):
    """
    Serializer for LLM OCR extraction request
    """

    image = serializers.FileField(required=True, help_text="Image or PDF file to extract text from (PNG, JPG, JPEG, PDF)")
    model = serializers.ChoiceField(
        choices=["deepseek-vision", "qwen-vision", "llava", "microsoft-phi"],
        default="deepseek-vision",
        help_text="Vision-language model to use for OCR",
    )
    language = serializers.ChoiceField(
        choices=["eng", "kor", "uzb", "uzb_cyrl"], default="eng", help_text="Target language for text extraction"
    )
    custom_prompt = serializers.CharField(
        required=False, allow_blank=True, help_text="Custom prompt for extraction (optional)"
    )
    save_to_db = serializers.BooleanField(default=False, help_text="Whether to save the result to database")


class LLMOCRResponseSerializer(serializers.Serializer):
    """
    Serializer for LLM OCR extraction response
    """

    success = serializers.BooleanField()
    text = serializers.CharField(required=False)
    model = serializers.CharField()
    language = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
    document_id = serializers.UUIDField(required=False)
    processing_time = serializers.FloatField(required=False)


class ModelListSerializer(serializers.Serializer):
    """
    Serializer for available models list
    """

    models = serializers.DictField(child=serializers.CharField(), help_text="Dictionary of available models")
