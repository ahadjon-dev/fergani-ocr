"""
URL configuration for OCR app (v1 API)
"""

from django.urls import path

from . import pdf_views, views

app_name = "ocr"

urlpatterns = [
    # Unified multi-format endpoint (images and PDFs - auto-detects file type)
    path("extract/", pdf_views.MultiFormatExtractView.as_view(), name="extract"),
    # Utility endpoints
    path("health/", views.OCRHealthCheckView.as_view(), name="health"),
    path("languages/", views.SupportedLanguagesView.as_view(), name="languages"),
]
