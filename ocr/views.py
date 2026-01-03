import pytesseract
from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import OCRImageUploadSerializer
from .services import OCRService

# Create your views here.


def index(request):
    """Render the main page"""
    return render(request, "ocr/index.html")


class OCRExtractTextView(APIView):
    """
    API View for extracting text from images using OCR

    Accepts: POST requests with multipart/form-data
    Returns: JSON response with extracted text and metadata

    Usage:
        POST /api/ocr/extract/
        Body:
            - image: Image file (required)
            - language: Language code (optional, default: 'eng')
            - save_to_db: Save to database (optional, default: true, accepts: true/false/1/0/yes/no)

    Response:
        {
            "success": true,
            "text": "Extracted text...",
            "filename": "image.png",
            "file_size": 12345,
            "image_dimensions": "800x600",
            "image_format": "PNG",
            "language": "eng",
            "character_count": 150,
            "word_count": 25
        }
    """

    parser_classes = [MultiPartParser, FormParser]
    serializer_class = OCRImageUploadSerializer

    # Maximum file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    @swagger_auto_schema(
        operation_description="Extract text from an image using Tesseract OCR",
        operation_summary="OCR Image Extraction",
        manual_parameters=[
            openapi.Parameter(
                "image",
                openapi.IN_FORM,
                description="Image file to extract text from (PNG, JPEG, etc.)",
                type=openapi.TYPE_FILE,
                required=True,
            ),
            openapi.Parameter(
                "language",
                openapi.IN_FORM,
                description="Language code for OCR",
                type=openapi.TYPE_STRING,
                default="eng",
                enum=["eng", "kor", "uzb", "uzb_cyrl"],
            ),
            openapi.Parameter(
                "save_to_db",
                openapi.IN_FORM,
                description="Save extraction results to database for caching",
                type=openapi.TYPE_BOOLEAN,
                default=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Text extracted successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "text": openapi.Schema(type=openapi.TYPE_STRING, description="Extracted text"),
                        "filename": openapi.Schema(type=openapi.TYPE_STRING),
                        "file_size": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "image_dimensions": openapi.Schema(type=openapi.TYPE_STRING),
                        "image_format": openapi.Schema(type=openapi.TYPE_STRING),
                        "language": openapi.Schema(type=openapi.TYPE_STRING),
                        "character_count": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "word_count": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
            400: openapi.Response(description="Invalid input"),
            500: openapi.Response(description="Server error"),
        },
        tags=["Traditional OCR"],
    )
    def post(self, request, *args, **kwargs):
        """
        Handle POST request to extract text from uploaded image
        """
        # Validate input data
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return self._error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        image_file = validated_data["image"]
        language = validated_data.get("language", "eng")

        # Get save_to_db parameter (default: True)
        save_to_db = request.data.get("save_to_db", "true").lower() in ["true", "1", "yes"]

        try:
            # Process the image using service layer
            result = OCRService.process_image_extraction(image_file, language, save_to_db=save_to_db)
            return Response(result, status=status.HTTP_200_OK)

        except pytesseract.TesseractNotFoundError:
            return self._error_response("Tesseract OCR is not installed or not in PATH", status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return self._error_response(f"Error processing image: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, *args, **kwargs):
        """
        Handle GET request - return API information
        """
        api_info = OCRService.get_ocr_api_info(self.MAX_FILE_SIZE)
        return Response(api_info)

    def _error_response(self, error_message, status_code):
        """
        Create standardized error response

        Args:
            error_message: Error message string or dict
            status_code: HTTP status code

        Returns:
            Response object with error details
        """
        return Response({"success": False, "error": error_message}, status=status_code)


class OCRHealthCheckView(APIView):
    """
    API View for checking OCR service health
    """

    @swagger_auto_schema(
        operation_description="Check if Tesseract OCR service is properly configured and working",
        operation_summary="OCR Health Check",
        responses={
            200: openapi.Response(
                description="Health status",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_STRING),
                        "tesseract_version": openapi.Schema(type=openapi.TYPE_STRING),
                        "available_languages": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            )
        },
        tags=["Traditional OCR"],
    )
    def get(self, request, *args, **kwargs):
        """
        Check if OCR service is working properly
        """
        health_status = OCRService.get_health_status()
        return Response(health_status)


class SupportedLanguagesView(APIView):
    """
    API View for listing supported OCR languages
    """

    @swagger_auto_schema(
        operation_description="Get list of languages supported by the OCR engine",
        operation_summary="List Supported Languages",
        responses={
            200: openapi.Response(
                description="List of supported languages",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "languages": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "code": openapi.Schema(type=openapi.TYPE_STRING),
                                    "name": openapi.Schema(type=openapi.TYPE_STRING),
                                },
                            ),
                        ),
                        "total": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            )
        },
        tags=["Traditional OCR"],
    )
    def get(self, request, *args, **kwargs):
        """
        Get list of supported languages
        """
        languages_info = OCRService.get_supported_languages()
        return Response(languages_info)
