"""
Views for LLM OCR API
"""

import logging
import time

from PIL import Image
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# Optional swagger support
try:
    from drf_yasg import openapi
    from drf_yasg.utils import swagger_auto_schema

    HAS_SWAGGER = True
except ImportError:
    HAS_SWAGGER = False

    # Create a no-op decorator when swagger is not available
    def swagger_auto_schema(*args, **kwargs):
        def decorator(func):
            return func

        return decorator


from ocr.utils import PDFProcessor  # Import shared PDF utility

from .serializers import LLMOCRExtractSerializer, LLMOCRResponseSerializer, ModelListSerializer
from .services import LLMOCRService

logger = logging.getLogger(__name__)


class LLMOCRExtractView(APIView):
    """
    API endpoint for LLM-based OCR text extraction
    """

    @swagger_auto_schema(
        operation_description="Extract text from image or PDF using vision-language models (DeepSeek, Qwen, LLaVA, Phi-3). Supports PNG, JPG, JPEG, and PDF files.",
        request_body=LLMOCRExtractSerializer,
        responses={200: LLMOCRResponseSerializer, 400: "Bad Request - Invalid input", 500: "Internal Server Error"},
        tags=["LLM OCR"],
    )
    def post(self, request):
        """
        Extract text from uploaded image or PDF using LLM
        """
        start_time = time.time()

        # Validate request data
        serializer = LLMOCRExtractSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": "Invalid input", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get validated data
            file = serializer.validated_data["image"]
            model = serializer.validated_data.get("model", "deepseek-vision")
            language = serializer.validated_data.get("language", "eng")
            custom_prompt = serializer.validated_data.get("custom_prompt")
            save_to_db = serializer.validated_data.get("save_to_db", False)  # noqa: F841

            # Check if it's a PDF
            file_name = file.name.lower() if hasattr(file, "name") else ""
            is_pdf = file_name.endswith(".pdf")

            if is_pdf:
                # Handle PDF - convert first page to image using shared utility
                try:
                    image = PDFProcessor.convert_pdf_to_image(file, page_number=1)
                except ImportError:
                    return Response(
                        {"error": "PDF support not available. Install pdf2image and poppler-utils."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                except Exception as e:
                    return Response({"error": f"Failed to process PDF: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Open as image
                try:
                    image = Image.open(file)
                except Exception as e:
                    return Response({"error": f"Invalid image file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            # Convert to RGB if necessary
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Process with LLM OCR
            result = LLMOCRService.process_image(image=image, model=model, language=language, custom_prompt=custom_prompt)

            # Add processing time and file type
            result["processing_time"] = time.time() - start_time
            result["file_type"] = "pdf" if is_pdf else "image"

            # TODO: Add database saving logic if save_to_db is True
            # This would integrate with the existing OCR app's models

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"Error processing LLM OCR request: {str(e)}")
            return Response(
                {"success": False, "error": str(e), "processing_time": time.time() - start_time},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AvailableModelsView(APIView):
    """
    API endpoint to list available LLM OCR models
    """

    @swagger_auto_schema(
        operation_description="Get list of available vision-language models for OCR",
        responses={
            200: ModelListSerializer,
        },
        tags=["LLM OCR"],
    )
    def get(self, request):
        """
        Get available models
        """
        models = LLMOCRService.get_available_models()
        return Response({"models": models}, status=status.HTTP_200_OK)


class LLMOCRHealthView(APIView):
    """
    Health check endpoint for LLM OCR service
    """

    if HAS_SWAGGER:

        @swagger_auto_schema(
            operation_description="Check if LLM OCR service is properly configured",
            responses={
                200: openapi.Response(
                    description="Service health status",
                    schema=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "status": openapi.Schema(type=openapi.TYPE_STRING),
                            "configured": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "available_models": openapi.Schema(type=openapi.TYPE_INTEGER),
                        },
                    ),
                )
            },
            tags=["LLM OCR"],
        )
        def get(self, request):
            """
            Check health status
            """
            from django.conf import settings

            api_key_configured = hasattr(settings, "HUGGINGFACE_API_KEY") and bool(settings.HUGGINGFACE_API_KEY)
            models = LLMOCRService.get_available_models()

            return Response(
                {
                    "status": "healthy" if api_key_configured else "not_configured",
                    "configured": api_key_configured,
                    "available_models": len(models),
                },
                status=status.HTTP_200_OK,
            )

    else:

        def get(self, request):
            """
            Check health status
            """
            from django.conf import settings

            api_key_configured = hasattr(settings, "HUGGINGFACE_API_KEY") and bool(settings.HUGGINGFACE_API_KEY)
            models = LLMOCRService.get_available_models()

            return Response(
                {
                    "status": "healthy" if api_key_configured else "not_configured",
                    "configured": api_key_configured,
                    "available_models": len(models),
                    "models": list(models.keys()),
                },
                status=status.HTTP_200_OK,
            )
