"""
Example: How to extend OCR views for custom functionality

This file demonstrates how to extend the class-based views
to add custom features like batch processing, image enhancement,
and custom OCR configurations.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from PIL import Image
from .utils import OCRProcessor
from .serializers import OCRImageUploadSerializer


class EnhancedOCRView(APIView):
    """
    Extended OCR view with image enhancement
    
    This view preprocesses images to improve OCR accuracy
    """
    
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, *args, **kwargs):
        """
        Process image with enhancement before OCR
        """
        serializer = OCRImageUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        image_file = validated_data['image']
        language = validated_data.get('language', 'eng')
        
        # Open and enhance image
        image = Image.open(image_file)
        enhanced_image = OCRProcessor.preprocess_image(image, enhance=True)
        
        # Extract text
        text = OCRProcessor.extract_text(enhanced_image, language=language)
        
        return Response({
            'success': True,
            'text': text,
            'enhanced': True,
            'filename': image_file.name
        })


class BatchOCRView(APIView):
    """
    Process multiple images in a single request
    
    Example of extending for batch operations
    """
    
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, *args, **kwargs):
        """
        Process multiple images at once
        """
        # Get all uploaded files
        images = request.FILES.getlist('images')
        
        if not images:
            return Response({
                'success': False,
                'error': 'No images provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        results = []
        language = request.data.get('language', 'eng')
        
        for image_file in images:
            try:
                image = Image.open(image_file)
                text = OCRProcessor.extract_text(image, language=language)
                
                results.append({
                    'filename': image_file.name,
                    'success': True,
                    'text': text,
                    'word_count': len(text.strip().split())
                })
            except Exception as e:
                results.append({
                    'filename': image_file.name,
                    'success': False,
                    'error': str(e)
                })
        
        return Response({
            'success': True,
            'total_images': len(images),
            'results': results
        })


class CustomConfigOCRView(APIView):
    """
    OCR with custom Tesseract configuration
    
    Example of using custom OCR parameters
    """
    
    parser_classes = [MultiPartParser, FormParser]
    
    # Custom Tesseract configurations
    CONFIGS = {
        'digits_only': '--psm 6 -c tessedit_char_whitelist=0123456789',
        'single_block': '--psm 6',
        'single_line': '--psm 7',
        'single_word': '--psm 8',
        'sparse_text': '--psm 11',
    }
    
    def post(self, request, *args, **kwargs):
        """
        Process image with custom Tesseract config
        """
        serializer = OCRImageUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        image_file = validated_data['image']
        language = validated_data.get('language', 'eng')
        
        # Get config type from request
        config_type = request.data.get('config', 'single_block')
        config = self.CONFIGS.get(config_type, self.CONFIGS['single_block'])
        
        # Open image
        image = Image.open(image_file)
        
        # Extract text with custom config
        text = OCRProcessor.extract_text(image, language=language, config=config)
        
        return Response({
            'success': True,
            'text': text,
            'config_used': config_type,
            'filename': image_file.name
        })


class OCRWithConfidenceView(APIView):
    """
    OCR that returns confidence scores
    
    Useful for filtering low-quality results
    """
    
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, *args, **kwargs):
        """
        Extract text and return confidence metrics
        """
        serializer = OCRImageUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        image_file = validated_data['image']
        language = validated_data.get('language', 'eng')
        min_confidence = float(request.data.get('min_confidence', 0))
        
        # Open image
        image = Image.open(image_file)
        
        # Extract text
        text = OCRProcessor.extract_text(image, language=language)
        
        # Get confidence scores
        confidence_data = OCRProcessor.get_confidence_scores(image, language=language)
        
        # Check if confidence meets minimum threshold
        meets_threshold = (
            confidence_data and 
            confidence_data['average_confidence'] >= min_confidence
        )
        
        return Response({
            'success': True,
            'text': text,
            'confidence': confidence_data,
            'meets_threshold': meets_threshold,
            'min_confidence_required': min_confidence,
            'filename': image_file.name
        })


# To use these extended views, add them to your urls.py:
"""
from ocr.examples import (
    EnhancedOCRView, 
    BatchOCRView, 
    CustomConfigOCRView,
    OCRWithConfidenceView
)

urlpatterns = [
    ...
    path('api/ocr/enhanced/', EnhancedOCRView.as_view(), name='ocr_enhanced'),
    path('api/ocr/batch/', BatchOCRView.as_view(), name='ocr_batch'),
    path('api/ocr/custom-config/', CustomConfigOCRView.as_view(), name='ocr_custom'),
    path('api/ocr/with-confidence/', OCRWithConfidenceView.as_view(), name='ocr_confidence'),
]
"""
