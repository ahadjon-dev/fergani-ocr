#!/usr/bin/env python3
"""
Quick test script to verify LLM OCR API key is working
"""
import os
import sys

# Setup Django
sys.path.insert(0, "/home/ahadjon/work/fergani/fergani-ocr/fergani")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fergani.settings")

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402

from llm_ocr.services import HuggingFaceOCRClient, LLMOCRService  # noqa: E402

print("=" * 60)
print("LLM OCR Configuration Test")
print("=" * 60)

# Check API key
api_key = settings.HUGGINGFACE_API_KEY
if api_key:
    print(f"✅ API Key loaded: {api_key[:10]}...{api_key[-4:]}")
    print(f"   Length: {len(api_key)} characters")
else:
    print("❌ API Key NOT loaded!")
    sys.exit(1)

# Check available models
models = LLMOCRService.get_available_models()
print(f"\n✅ Available models: {len(models)}")
for alias, model_id in models.items():
    print(f"   - {alias}: {model_id}")

# Test client initialization
try:
    client = HuggingFaceOCRClient(api_key=api_key)
    print("\n✅ HuggingFaceOCRClient initialized successfully")
    print(f"   Model: {client.model}")
except Exception as e:
    print(f"\n❌ Client initialization failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All checks passed! LLM OCR is ready to use.")
print("=" * 60)
