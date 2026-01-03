"""
Serializers for OCR app
"""

from rest_framework import serializers


class OCRImageUploadSerializer(serializers.Serializer):
    """
    Serializer for validating OCR image uploads
    """

    image = serializers.ImageField(required=True, help_text="Image file to extract text from")
    language = serializers.CharField(
        required=False, default="eng", max_length=20, help_text="Tesseract language code (e.g., 'eng', 'ara', 'spa')"
    )

    def validate_image(self, value):
        """
        Validate uploaded image
        """
        # Maximum file size (10MB)
        max_size = 10 * 1024 * 1024

        if value.size > max_size:
            raise serializers.ValidationError(f"Image file size cannot exceed {max_size / (1024 * 1024)}MB")

        # Validate image format
        allowed_formats = ["PNG", "JPEG", "JPG", "TIFF", "BMP", "GIF", "WEBP"]
        if value.content_type:
            file_extension = value.content_type.split("/")[-1].upper()
            if file_extension not in allowed_formats:
                raise serializers.ValidationError(f"Invalid image format. Allowed formats: {', '.join(allowed_formats)}")

        return value

    def validate_language(self, value):
        """
        Validate and sanitize language code
        """
        # Remove any potentially harmful characters
        sanitized = "".join(c for c in value if c.isalnum() or c == "_")

        if not sanitized:
            return "eng"

        return sanitized


class OCRResultSerializer(serializers.Serializer):
    """
    Serializer for OCR extraction results
    """

    success = serializers.BooleanField()
    text = serializers.CharField()
    filename = serializers.CharField()
    file_size = serializers.IntegerField()
    image_dimensions = serializers.CharField()
    image_format = serializers.CharField()
    language = serializers.CharField()
    character_count = serializers.IntegerField()
    word_count = serializers.IntegerField()
