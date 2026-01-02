"""
Integration tests for multi-format extraction endpoint
Tests: POST /api/extract/
"""
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io


class TestMultiFormatExtract(APITestCase):
    """Test suite for multi-format extraction endpoint"""

    def _create_test_image(self, size=(200, 100), format='PNG'):
        """Helper method to create a test image"""
        image = Image.new('RGB', size, color='white')
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=format)
        img_byte_arr.seek(0)
        
        return SimpleUploadedFile(
            f"test_image.{format.lower()}",
            img_byte_arr.read(),
            content_type=f'image/{format.lower()}'
        )

    def _create_test_pdf(self):
        """Helper method to create a test PDF file"""
        return SimpleUploadedFile(
            "test.pdf",
            b"Test PDF content",
            content_type="application/pdf"
        )

    def test_multiformat_extract_case_1(self):
        """
        Case: GET request to multi-format endpoint
        Expected: Return API information
        """
        response = self.client.get('/api/extract/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        
        # Check response structure
        response_data = response.json()
        self.assertIn('message', response_data)
        self.assertIn('version', response_data)
        self.assertIn('endpoint', response_data)
        self.assertIn('method', response_data)
        self.assertIn('supported_formats', response_data)
        self.assertIn('max_file_size_mb', response_data)
        self.assertIn('features', response_data)

    def test_multiformat_extract_case_2(self):
        """
        Case: Extract text from image file
        Expected: Success with image type indicator
        """
        image_file = self._create_test_image()
        
        data = {'file': image_file}
        response = self.client.post('/api/extract/', data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        
        response_data = response.json()
        self.assertIn('success', response_data)
        self.assertTrue(response_data['success'])
        self.assertIn('file_type', response_data)
        self.assertEqual(response_data['file_type'], 'image')
        self.assertIn('text', response_data)
        self.assertIn('filename', response_data)
        self.assertIn('image_dimensions', response_data)
        self.assertIn('image_format', response_data)

    def test_multiformat_extract_case_3(self):
        """
        Case: Extract text from PDF file
        Expected: Success with PDF type indicator (if PDF support available)
        """
        pdf_file = self._create_test_pdf()
        
        data = {'file': pdf_file}
        response = self.client.post('/api/extract/', data, format='multipart')
        
        # Response depends on whether PDF support is available
        if response.status_code == status.HTTP_200_OK:
            response_data = response.json()
            self.assertTrue(response_data['success'])
            self.assertEqual(response_data['file_type'], 'pdf')
            self.assertIn('total_pages', response_data)
            self.assertIn('method', response_data)
        else:
            # PDF support not available
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_multiformat_extract_case_4(self):
        """
        Case: Attempt to extract without providing file
        Expected: Failure with validation error
        """
        data = {}
        response = self.client.post('/api/extract/', data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        
        response_data = response.json()
        self.assertIn('success', response_data)
        self.assertFalse(response_data['success'])
        self.assertIn('error', response_data)

    def test_multiformat_extract_case_5(self):
        """
        Case: Attempt to extract from unsupported file type
        Expected: Failure with validation error
        """
        # Create a text file
        text_file = SimpleUploadedFile(
            "test.txt",
            b"This is a text file",
            content_type="text/plain"
        )
        
        data = {'file': text_file}
        response = self.client.post('/api/extract/', data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        
        response_data = response.json()
        self.assertFalse(response_data['success'])
        self.assertIn('error', response_data)
        self.assertIn('Unsupported file type', response_data['error'])

    def test_multiformat_extract_case_6(self):
        """
        Case: Extract with custom language parameter
        Expected: Success with specified language
        """
        image_file = self._create_test_image()
        
        data = {
            'file': image_file,
            'language': 'eng'  # Use 'eng' since it's always available
        }
        response = self.client.post('/api/extract/', data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        
        response_data = response.json()
        self.assertTrue(response_data['success'])

    def test_multiformat_extract_case_7(self):
        """
        Case: Verify supported formats in API info
        Expected: Lists images and PDFs (if available)
        """
        response = self.client.get('/api/extract/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        
        response_data = response.json()
        supported_formats = response_data['supported_formats']
        
        self.assertIn('images', supported_formats)
        self.assertIsInstance(supported_formats['images'], list)
        self.assertGreater(len(supported_formats['images']), 0)
        
        self.assertIn('documents', supported_formats)
        self.assertIsInstance(supported_formats['documents'], list)

    def test_multiformat_extract_case_8(self):
        """
        Case: Extract from different image formats
        Expected: Success for all supported image formats
        """
        formats = ['PNG', 'JPEG']
        
        for img_format in formats:
            with self.subTest(format=img_format):
                image_file = self._create_test_image(format=img_format)
                
                data = {'file': image_file}
                response = self.client.post('/api/extract/', data, format='multipart')
                
                self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
                
                response_data = response.json()
                self.assertTrue(response_data['success'])
                self.assertEqual(response_data['file_type'], 'image')

    def test_multiformat_extract_case_9(self):
        """
        Case: Verify features list
        Expected: Key features are documented
        """
        response = self.client.get('/api/extract/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        
        response_data = response.json()
        features = response_data['features']
        
        self.assertIsInstance(features, list)
        self.assertGreater(len(features), 0)
        
        # Check for key features
        features_text = ' '.join(features).lower()
        self.assertIn('auto-detect', features_text)
        self.assertIn('ocr', features_text)
