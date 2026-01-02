"""
Advanced Examples: Authentication, Permissions, and Throttling

This file shows how to add authentication, permissions, and rate limiting
to your class-based OCR views.
"""

from PIL import Image
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView

from .serializers import OCRImageUploadSerializer
from .utils import OCRProcessor


class OCRThrottle(UserRateThrottle):
    """
    Custom throttle: 10 requests per minute for authenticated users
    """

    rate = "10/min"


class AnonOCRThrottle(AnonRateThrottle):
    """
    Custom throttle: 3 requests per minute for anonymous users
    """

    rate = "3/min"


class AuthenticatedOCRView(APIView):
    """
    OCR view that requires authentication
    
    Only authenticated users can access this endpoint.
    This is useful for production environments where you want to
    control access and track usage.
    
    Setup required:
    1. Add 'rest_framework.authtoken' to INSTALLED_APPS
    2. Run: python manage.py migrate
    3. Create tokens for users: python manage.py drf_create_token <username>
    
    Usage:
    curl -X POST http://127.0.0.1:8001/api/ocr/authenticated/ \
      -H "Authorization: Token <your-token>" \
      -F "image=@image.png"
    """

    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    throttle_classes = [OCRThrottle]

    def post(self, request, *args, **kwargs):
        """
        Process OCR for authenticated users only
        """
        serializer = OCRImageUploadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        image_file = validated_data["image"]
        language = validated_data.get("language", "eng")

        # Open image
        image = Image.open(image_file)

        # Extract text
        text = OCRProcessor.extract_text(image, language=language)

        return Response(
            {
                "success": True,
                "text": text,
                "user": request.user.username,  # Track who made the request
                "filename": image_file.name,
                "language": language,
            }
        )


class PublicThrottledOCRView(APIView):
    """
    Public OCR view with rate limiting

    No authentication required but rate limited to prevent abuse.
    Perfect for public APIs with usage limits.
    """

    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    throttle_classes = [AnonOCRThrottle]

    def post(self, request, *args, **kwargs):
        """
        Process OCR with rate limiting
        """
        serializer = OCRImageUploadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        image_file = validated_data["image"]
        language = validated_data.get("language", "eng")

        # Open image
        image = Image.open(image_file)

        # Extract text
        text = OCRProcessor.extract_text(image, language=language)

        return Response(
            {
                "success": True,
                "text": text,
                "filename": image_file.name,
                "rate_limit_info": {
                    "limit": "3 requests per minute",
                    "note": "Upgrade to authenticated access for higher limits",
                },
            }
        )


class CustomPermissionOCRView(APIView):
    """
    OCR view with custom permission logic

    Example: Only allow OCR for images smaller than 5MB for free users,
    but allow larger images for premium users.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    FREE_USER_MAX_SIZE = 5 * 1024 * 1024  # 5MB
    PREMIUM_USER_MAX_SIZE = 50 * 1024 * 1024  # 50MB

    def post(self, request, *args, **kwargs):
        """
        Process OCR with tier-based limits
        """
        serializer = OCRImageUploadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        image_file = validated_data["image"]
        language = validated_data.get("language", "eng")

        # Check user tier (you'd have this in your User model)
        is_premium = getattr(request.user, "is_premium", False)
        max_size = self.PREMIUM_USER_MAX_SIZE if is_premium else self.FREE_USER_MAX_SIZE

        # Validate file size based on user tier
        if image_file.size > max_size:
            tier = "premium" if is_premium else "free"
            return Response(
                {
                    "success": False,
                    "error": f"File size exceeds {tier} tier limit of {max_size / (1024*1024)}MB",
                    "upgrade_message": "Upgrade to premium for larger files" if not is_premium else None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Open image
        image = Image.open(image_file)

        # Extract text
        text = OCRProcessor.extract_text(image, language=language)

        return Response(
            {"success": True, "text": text, "user_tier": "premium" if is_premium else "free", "filename": image_file.name}
        )


# Configuration for settings.py:
"""
# Add to settings.py for authentication and throttling:

INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework.authtoken',  # For token authentication
    'corsheaders',
    'ocr',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Default to allow any
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '100/hour',  # Authenticated users
        'anon': '20/hour',   # Anonymous users
    },
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.JSONParser',
    ],
}
"""

# URL configuration:
"""
from ocr.advanced_examples import (
    AuthenticatedOCRView,
    PublicThrottledOCRView,
    CustomPermissionOCRView
)

urlpatterns = [
    ...
    path('api/ocr/authenticated/', AuthenticatedOCRView.as_view(), name='ocr_authenticated'),
    path('api/ocr/public/', PublicThrottledOCRView.as_view(), name='ocr_public'),
    path('api/ocr/premium/', CustomPermissionOCRView.as_view(), name='ocr_premium'),
]
"""

# Create tokens for users:
"""
python manage.py migrate
python manage.py createsuperuser
python manage.py drf_create_token <username>
"""
