"""
Quick Start Guide: Using Class-Based Views in Fergani OCR
==========================================================

This file provides quick examples of how to use and extend the OCR views.
"""

# ============================================================================
# 1. BASIC USAGE - Using the existing views
# ============================================================================

"""
The OCR API is now running with class-based views. Here's how to use it:

# Test the main extraction endpoint
curl -X POST http://127.0.0.1:8001/api/ocr/extract/ \
  -F "image=@image.png" \
  -F "language=eng"

# Get API information
curl http://127.0.0.1:8001/api/ocr/extract/

# Check service health
curl http://127.0.0.1:8001/api/ocr/health/

# List supported languages
curl http://127.0.0.1:8001/api/ocr/languages/
"""


# ============================================================================
# 2. CREATING A CUSTOM VIEW - Simplest Example
# ============================================================================

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from PIL import Image
from .utils import OCRProcessor


class SimpleCustomOCRView(APIView):
    """
    The simplest custom OCR view
    """
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        if 'image' not in request.FILES:
            return Response({
                'error': 'No image provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Open image
        image_file = request.FILES['image']
        image = Image.open(image_file)
        
        # Extract text
        text = OCRProcessor.extract_text(image)
        
        # Return result
        return Response({
            'text': text,
            'filename': image_file.name
        })


# ============================================================================
# 3. EXTENDING THE BASE VIEW - Recommended Approach
# ============================================================================

from .views import OCRExtractTextView


class MyCustomOCRView(OCRExtractTextView):
    """
    Extend the base OCR view to add custom functionality
    """
    
    # Override class attributes
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB instead of 10MB
    
    def post(self, request, *args, **kwargs):
        """
        Override POST to add custom logic before/after processing
        """
        # Custom logic before processing
        print(f"Processing request from {request.META.get('REMOTE_ADDR')}")
        
        # Call parent method
        response = super().post(request, *args, **kwargs)
        
        # Custom logic after processing
        if response.status_code == 200:
            print(f"Successfully processed {response.data.get('filename')}")
        
        return response
    
    def _process_image(self, image_file, language):
        """
        Override to customize image processing
        """
        # Get default result
        result = super()._process_image(image_file, language)
        
        # Add custom fields
        result['custom_field'] = 'custom_value'
        result['processed_by'] = 'MyCustomOCRView'
        
        return result


# ============================================================================
# 4. ADDING AUTHENTICATION - Production Ready
# ============================================================================

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


class AuthenticatedOCRView(OCRExtractTextView):
    """
    OCR view that requires authentication
    
    Setup:
    1. Add 'rest_framework.authtoken' to INSTALLED_APPS
    2. Run: python manage.py migrate
    3. Create token: python manage.py drf_create_token <username>
    
    Usage:
    curl -X POST http://127.0.0.1:8001/api/ocr/authenticated/ \
      -H "Authorization: Token <your-token>" \
      -F "image=@image.png"
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def _process_image(self, image_file, language):
        result = super()._process_image(image_file, language)
        
        # Add user info to result
        result['processed_by_user'] = self.request.user.username
        
        return result


# ============================================================================
# 5. ADDING RATE LIMITING - Prevent Abuse
# ============================================================================

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class CustomThrottle(UserRateThrottle):
    rate = '10/min'  # 10 requests per minute


class ThrottledOCRView(OCRExtractTextView):
    """
    OCR view with rate limiting
    
    Configure in settings.py:
    REST_FRAMEWORK = {
        'DEFAULT_THROTTLE_RATES': {
            'user': '100/hour',
            'anon': '20/hour',
        }
    }
    """
    throttle_classes = [CustomThrottle]


# ============================================================================
# 6. IMAGE ENHANCEMENT - Better OCR Results
# ============================================================================

class EnhancedOCRView(OCRExtractTextView):
    """
    OCR view with automatic image enhancement
    """
    
    def _process_image(self, image_file, language):
        # Open image
        image = Image.open(image_file)
        
        # Enhance image before OCR
        enhanced_image = OCRProcessor.preprocess_image(image, enhance=True)
        
        # Extract text from enhanced image
        text = OCRProcessor.extract_text(enhanced_image, language=language)
        
        # Get image info
        image_info = OCRProcessor.get_image_info(enhanced_image)
        
        return {
            'success': True,
            'text': text,
            'enhanced': True,
            'filename': image_file.name,
            'file_size': image_file.size,
            'image_dimensions': f"{image_info['width']}x{image_info['height']}",
            'character_count': len(text.strip()),
            'word_count': len(text.strip().split())
        }


# ============================================================================
# 7. BATCH PROCESSING - Multiple Images
# ============================================================================

class BatchOCRView(APIView):
    """
    Process multiple images in one request
    
    Usage:
    curl -X POST http://127.0.0.1:8001/api/ocr/batch/ \
      -F "images=@image1.png" \
      -F "images=@image2.png" \
      -F "images=@image3.png" \
      -F "language=eng"
    """
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
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
            'processed': len([r for r in results if r['success']]),
            'failed': len([r for r in results if not r['success']]),
            'results': results
        })


# ============================================================================
# 8. CUSTOM TESSERACT CONFIG - Advanced OCR
# ============================================================================

class DigitsOnlyOCRView(OCRExtractTextView):
    """
    OCR optimized for extracting only numbers
    
    Useful for invoices, receipts, ID numbers, etc.
    """
    
    def _process_image(self, image_file, language):
        image = Image.open(image_file)
        
        # Custom Tesseract config for digits only
        config = '--psm 6 -c tessedit_char_whitelist=0123456789'
        
        text = OCRProcessor.extract_text(
            image, 
            language=language,
            config=config
        )
        
        return {
            'success': True,
            'text': text,
            'mode': 'digits_only',
            'filename': image_file.name
        }


# ============================================================================
# 9. REGISTERING CUSTOM VIEWS IN URLS.PY
# ============================================================================

"""
# Add to fergani/urls.py:

from ocr.quick_start import (
    SimpleCustomOCRView,
    MyCustomOCRView,
    AuthenticatedOCRView,
    ThrottledOCRView,
    EnhancedOCRView,
    BatchOCRView,
    DigitsOnlyOCRView
)

urlpatterns = [
    ...
    
    # Custom views
    path('api/ocr/simple/', SimpleCustomOCRView.as_view(), name='simple_ocr'),
    path('api/ocr/custom/', MyCustomOCRView.as_view(), name='custom_ocr'),
    path('api/ocr/authenticated/', AuthenticatedOCRView.as_view(), name='auth_ocr'),
    path('api/ocr/throttled/', ThrottledOCRView.as_view(), name='throttled_ocr'),
    path('api/ocr/enhanced/', EnhancedOCRView.as_view(), name='enhanced_ocr'),
    path('api/ocr/batch/', BatchOCRView.as_view(), name='batch_ocr'),
    path('api/ocr/digits/', DigitsOnlyOCRView.as_view(), name='digits_ocr'),
]
"""


# ============================================================================
# 10. TESTING YOUR CUSTOM VIEWS
# ============================================================================

"""
# Test in Python:

import requests

# Test simple custom view
url = 'http://127.0.0.1:8001/api/ocr/custom/'
files = {'image': open('image.png', 'rb')}
data = {'language': 'eng'}

response = requests.post(url, files=files, data=data)
print(response.json())


# Test batch processing
url = 'http://127.0.0.1:8001/api/ocr/batch/'
files = [
    ('images', open('image1.png', 'rb')),
    ('images', open('image2.png', 'rb')),
    ('images', open('image3.png', 'rb'))
]
data = {'language': 'eng'}

response = requests.post(url, files=files, data=data)
print(response.json())


# Test authenticated view
url = 'http://127.0.0.1:8001/api/ocr/authenticated/'
headers = {'Authorization': 'Token YOUR_TOKEN_HERE'}
files = {'image': open('image.png', 'rb')}

response = requests.post(url, files=files, headers=headers)
print(response.json())
"""


# ============================================================================
# SUMMARY
# ============================================================================

"""
Key Benefits of Class-Based Views:

✅ Inheritance: Easily extend functionality
✅ Mixins: Reusable components  
✅ Built-in Features: Auth, permissions, throttling
✅ Better Organization: Separate GET, POST, PUT, DELETE
✅ Type Safety: Better IDE support
✅ DRY: Don't Repeat Yourself

Next Steps:

1. Choose a custom view example above
2. Copy it to a new file or add to views.py
3. Register it in urls.py
4. Test with curl or Python requests
5. Customize further based on your needs

For more examples, see:
- ocr/examples.py - Basic extensions
- ocr/advanced_examples.py - Production features
- CLASS_BASED_VIEWS_GUIDE.md - Comprehensive guide
"""
