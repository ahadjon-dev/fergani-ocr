from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
import pytesseract

from .serializers import OCRImageUploadSerializer
from .services import OCRService

# Create your views here.

def index(request):
    """Render the main page"""
    return render(request, 'ocr/index.html')


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
    
    def post(self, request, *args, **kwargs):
        """
        Handle POST request to extract text from uploaded image
        """
        # Validate input data
        serializer = self.serializer_class(data=request.data)
        
        if not serializer.is_valid():
            return self._error_response(
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
            )
        
        validated_data = serializer.validated_data
        image_file = validated_data['image']
        language = validated_data.get('language', 'eng')
        
        # Get save_to_db parameter (default: True)
        save_to_db = request.data.get('save_to_db', 'true').lower() in ['true', '1', 'yes']
        
        try:
            # Process the image using service layer
            result = OCRService.process_image_extraction(image_file, language, save_to_db=save_to_db)
            return Response(result, status=status.HTTP_200_OK)
            
        except pytesseract.TesseractNotFoundError:
            return self._error_response(
                'Tesseract OCR is not installed or not in PATH',
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        except Exception as e:
            return self._error_response(
                f'Error processing image: {str(e)}',
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
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
        return Response({
            'success': False,
            'error': error_message
        }, status=status_code)


class OCRHealthCheckView(APIView):
    """
    API View for checking OCR service health
    """
    
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
    
    def get(self, request, *args, **kwargs):
        """
        Get list of supported languages
        """
        languages_info = OCRService.get_supported_languages()
        return Response(languages_info)
