"""
URL configuration for LLM OCR app
"""

from django.urls import path

from .views import AvailableModelsView, LLMOCRExtractView, LLMOCRHealthView

app_name = "llm_ocr"

urlpatterns = [
    path("extract/", LLMOCRExtractView.as_view(), name="llm_extract"),
    path("models/", AvailableModelsView.as_view(), name="available_models"),
    path("health/", LLMOCRHealthView.as_view(), name="health"),
]
