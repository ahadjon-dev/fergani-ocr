"""
PDF OCR Views for text extraction from PDF files
"""
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .services import PDFService, MultiFormatService
from .utils import OCRProcessor
import logging

logger = logging.getLogger(__name__)


class PDFExtractTextView(APIView):
    """
    API View for extracting text from PDF files
    
    Supports both text-based PDFs and scanned PDFs (using OCR)
    
    Usage:
        POST /api/pdf/extract/
        Body: 
            - file: PDF file (required)
            - language: Language code (optional, default: 'eng')
            - use_ocr: Whether to use OCR for scanned PDFs (optional, default: true)
            - pages: Comma-separated page numbers to extract (optional, e.g., "1,3,5")
            - save_to_db: Save to database (optional, default: true, accepts: true/false/1/0/yes/no)
    
    Response:
        {
            "success": true,
            "text": "Extracted text...",
            "filename": "document.pdf",
            "total_pages": 10,
            "method": "text_extraction" or "ocr",
            "pages": [
                {
                    "page_number": 1,
                    "text": "Page 1 text..."
                }
            ]
        }
    """
    
    parser_classes = [MultiPartParser, FormParser]
    
    # Maximum file size (50MB for PDFs)
    MAX_FILE_SIZE = 50 * 1024 * 1024
    
    def post(self, request, *args, **kwargs):
        """
        Handle POST request to extract text from PDF
        """
        # Check if PDF support is available
        if not OCRProcessor.is_pdf_support_available():
            return Response({
                'success': False,
                'error': 'PDF support not available',
                'help': 'Install required packages: pip install PyPDF2 pdf2image poppler-utils'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Validate file presence
        if 'file' not in request.FILES:
            return self._error_response(
                'No PDF file provided',
                status.HTTP_400_BAD_REQUEST
            )
        
        pdf_file = request.FILES['file']
        
        # Validate file using service layer
        is_valid, error_message = PDFService.validate_pdf_file(pdf_file, self.MAX_FILE_SIZE)
        if not is_valid:
            return self._error_response(error_message, status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get parameters
            language = request.data.get('language', 'eng')
            use_ocr = request.data.get('use_ocr', 'true').lower() == 'true'
            pages_param = request.data.get('pages', None)
            save_to_db = request.data.get('save_to_db', 'true').lower() in ['true', '1', 'yes']
            
            # Process PDF using service layer
            response_data = PDFService.process_pdf_extraction(
                pdf_file,
                language=language,
                use_ocr=use_ocr,
                pages_param=pages_param,
                save_to_db=save_to_db
            )
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except ImportError as e:
            return self._error_response(
                str(e),
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            return self._error_response(
                f'Error processing PDF: {str(e)}',
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET request - return API information
        """
        api_info = PDFService.get_pdf_api_info(self.MAX_FILE_SIZE)
        return Response(api_info)
    
    def _error_response(self, error_message, status_code):
        """
        Create standardized error response
        """
        return Response({
            'success': False,
            'error': error_message
        }, status=status_code)


# Add AUTH logic here
class MultiFormatExtractView(APIView):
    """
    Unified view for extracting text from multiple file formats
    
    Supports: Images (PNG, JPEG, etc.) and PDFs
    
    Usage:
        POST /api/extract/
        Body:
            - file: Image or PDF file (required)
            - language: Language code (optional, default: 'eng')
            - save_to_db: Save to database (optional, default: true, accepts: true/false/1/0/yes/no)
    """
    
    parser_classes = [MultiPartParser, FormParser]
    MAX_FILE_SIZE = 50 * 1024 * 1024
    
    def post(self, request, *args, **kwargs):
        """
        Handle POST request - auto-detect file type and extract text
        """
        if 'file' not in request.FILES:
            return self._error_response(
                'No file provided',
                status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        language = request.data.get('language', 'eng')
        save_to_db = request.data.get('save_to_db', 'true').lower() in ['true', '1', 'yes']
        
        # Validate file using service layer
        is_valid, error_message, file_type = MultiFormatService.validate_file(
            file, 
            self.MAX_FILE_SIZE
        )
        
        if not is_valid:
            return self._error_response(error_message, status.HTTP_400_BAD_REQUEST)
        
        try:
            # Process file using service layer
            result = MultiFormatService.process_file(file, language, save_to_db)
            return Response(result, status=status.HTTP_200_OK)
        
        except ImportError:
            return self._error_response(
                'PDF support not available',
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return self._error_response(
                f'Error processing file: {str(e)}',
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request, *args, **kwargs):
        """
        Return API information
        """
        api_info = MultiFormatService.get_api_info(self.MAX_FILE_SIZE)
        return Response(api_info)
    
    def _error_response(self, error_message, status_code):
        """Create error response"""
        return Response({
            'success': False,
            'error': error_message
        }, status=status_code)
