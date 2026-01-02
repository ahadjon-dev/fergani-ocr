# OCR Application Tests

This directory contains comprehensive tests for the Fergani OCR application.

## Test Structure

```
tests/
├── __init__.py
└── ocr/
    ├── __init__.py
    ├── fixtures/              # Test fixtures (JSON files for models when needed)
    ├── test_ocr_extract.py    # Tests for /api/ocr/extract/ endpoint
    ├── test_health_check.py   # Tests for /api/ocr/health/ endpoint
    ├── test_supported_languages.py  # Tests for /api/ocr/languages/ endpoint
    ├── test_pdf_extract.py    # Tests for /api/pdf/extract/ endpoint
    ├── test_multiformat_extract.py  # Tests for /api/extract/ endpoint
    └── test_services.py       # Unit tests for service layer
```

## Test Types

### Integration Tests
Tests that verify the entire request-response cycle including:
- URL routing
- View layer
- Service layer
- Response formatting

Located in:
- `test_ocr_extract.py`
- `test_health_check.py`
- `test_supported_languages.py`
- `test_pdf_extract.py`
- `test_multiformat_extract.py`

### Unit Tests
Tests that verify individual service layer functions in isolation.

Located in:
- `test_services.py`

## Running Tests

### Run All Tests
```bash
cd fergani
python manage.py test tests
```

### Run Specific Test File
```bash
# Test OCR extraction endpoint
python manage.py test tests.ocr.test_ocr_extract

# Test health check endpoint
python manage.py test tests.ocr.test_health_check

# Test service layer
python manage.py test tests.ocr.test_services
```

### Run Specific Test Class
```bash
python manage.py test tests.ocr.test_ocr_extract.TestOCRExtractText
```

### Run Specific Test Case
```bash
python manage.py test tests.ocr.test_ocr_extract.TestOCRExtractText.test_ocr_extract_case_1
```

### Run with Verbose Output
```bash
python manage.py test tests --verbosity=2
```

### Run with Coverage
```bash
# Install coverage if not already installed
pip install coverage

# Run tests with coverage
coverage run --source='ocr' manage.py test tests
coverage report
coverage html  # Generate HTML report in htmlcov/
```

## Test Coverage

### OCR Extract Endpoint (`/api/ocr/extract/`)
- ✅ Successful text extraction from images
- ✅ Custom language parameter
- ✅ Missing file validation
- ✅ Invalid file type validation
- ✅ Multiple image format support
- ✅ GET request for API info
- ✅ File size validation

### Health Check Endpoint (`/api/ocr/health/`)
- ✅ Health status check
- ✅ Tesseract installation verification
- ✅ Language support count
- ✅ Method not allowed (POST)

### Supported Languages Endpoint (`/api/ocr/languages/`)
- ✅ Language list retrieval
- ✅ Expected languages verification
- ✅ Count accuracy
- ✅ Language name validation
- ✅ Method not allowed (POST)

### PDF Extract Endpoint (`/api/pdf/extract/`)
- ✅ API information retrieval
- ✅ Missing file validation
- ✅ Invalid file type validation
- ✅ PDF support availability check
- ✅ Parameters documentation
- ✅ Features listing

### Multi-Format Extract Endpoint (`/api/extract/`)
- ✅ API information retrieval
- ✅ Image file extraction
- ✅ PDF file extraction
- ✅ Missing file validation
- ✅ Unsupported file type validation
- ✅ Custom language parameter
- ✅ Format support verification
- ✅ Multiple image formats
- ✅ Features documentation

### Service Layer
- ✅ OCRService: image processing, API info, health status, language support
- ✅ PDFService: file validation, API info
- ✅ MultiFormatService: file validation, file type detection, API info

## Test Patterns

### Basic Test Structure
```python
from rest_framework.test import APITestCase
from rest_framework import status

class TestEndpoint(APITestCase):
    
    def test_case_1(self):
        """
        Case: Description of what is being tested
        Expected: Expected outcome
        """
        # Arrange
        data = {...}
        
        # Act
        response = self.client.post('/api/endpoint/', data)
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('key', response.json())
```

### Helper Methods
Each test class includes helper methods for creating test data:
```python
def _create_test_image(self, size=(200, 100), format='PNG'):
    """Create a test image for OCR testing"""
    ...

def _create_test_pdf(self):
    """Create a test PDF file"""
    ...
```

## Writing New Tests

When adding new features, follow this pattern:

1. **Create test file** in `tests/ocr/` named `test_<feature>.py`
2. **Import required modules**:
   ```python
   from rest_framework.test import APITestCase
   from rest_framework import status
   ```
3. **Create test class** inheriting from `APITestCase`
4. **Add helper methods** for test data creation
5. **Write test cases** following the naming convention: `test_<feature>_case_<number>`
6. **Document each test** with docstring explaining case and expected outcome

### Test Case Template
```python
def test_feature_case_1(self):
    """
    Case: [What is being tested]
    Expected: [Expected outcome]
    """
    # Arrange - Set up test data
    data = {...}
    
    # Act - Execute the action
    response = self.client.post('/api/endpoint/', data)
    
    # Assert - Verify the results
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertIn('expected_key', response.json())
```

## Fixtures

When models are added to the application, create fixtures in `tests/ocr/fixtures/`:

```
fixtures/
├── test_feature_name/
│   ├── users.json
│   ├── models.json
│   └── ...
```

Load fixtures in test class:
```python
class TestFeature(APITestCase):
    fixtures = [
        "tests/ocr/fixtures/test_feature/users.json",
        "tests/ocr/fixtures/test_feature/models.json",
    ]
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    cd fergani
    python manage.py test tests --verbosity=2
```

## Notes

- Tests use `SimpleUploadedFile` to create mock files
- Image tests use PIL to generate test images
- PDF tests use mock PDF content (real PDF testing requires PyPDF2)
- All tests are isolated and don't depend on external state
- Tests clean up after themselves automatically

## Troubleshooting

### Import Errors
If you see import errors, ensure you're running tests from the `fergani/` directory:
```bash
cd fergani
python manage.py test tests
```

### Tesseract Not Found
Some tests may fail if Tesseract OCR is not installed. Install it:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract
```

### PDF Support Errors
PDF-related tests may be skipped if PDF libraries are not installed:
```bash
pip install PyPDF2 pdf2image
sudo apt-get install poppler-utils  # For pdf2image
```
