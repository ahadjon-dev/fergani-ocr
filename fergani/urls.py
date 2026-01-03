"""
URL configuration for fergani project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from ocr import views as ocr_views


def railway_health(request):
    """Simple health check for Railway - returns 200 OK immediately"""
    return JsonResponse({"status": "ok", "service": "fergani-ocr"})


# Swagger/OpenAPI schema configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Fergani OCR API",
        default_version="v1",
        description="""
# Fergani OCR API Documentation

Advanced OCR (Optical Character Recognition) service with multiple extraction engines.

## Features
- **Traditional OCR**: Fast Tesseract-based text extraction
- **AI Vision Models**: Advanced LLM-powered OCR for complex layouts
- **Multi-format Support**: Images (PNG, JPEG, etc.) and PDF files
- **Multiple Languages**: English, Korean, Uzbek (Latin & Cyrillic)
- **Database Caching**: Optional result caching for faster repeated queries

## Authentication
Currently, no authentication is required. API keys may be added in future versions.

## Rate Limits
No rate limits currently enforced for traditional OCR. LLM OCR is subject to Hugging Face API limits.
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@fergani-ocr.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Swagger/OpenAPI Documentation
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("docs/", schema_view.with_ui("swagger", cache_timeout=0), name="api-docs"),
    # Simple health check for Railway (fast, no external dependencies)
    path("health/", railway_health, name="railway_health"),
    # Frontend
    path("", ocr_views.index, name="index"),
    # API v1 endpoints (primary API)
    path("api/v1/ocr/", include("ocr.urls")),
    path("api/v1/llm-ocr/", include("llm_ocr.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
