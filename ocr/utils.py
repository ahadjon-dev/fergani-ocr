"""
Utility functions for OCR operations
"""
import pytesseract
from PIL import Image
import logging
import io
import os
import subprocess
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Configure Tesseract path for deployment
def find_tesseract_cmd():
    """Find tesseract executable using multiple methods"""
    
    # Method 1: Check Django settings (if available)
    try:
        from django.conf import settings
        if hasattr(settings, 'TESSERACT_CMD') and settings.TESSERACT_CMD:
            if os.path.exists(settings.TESSERACT_CMD):
                return settings.TESSERACT_CMD
    except Exception:
        pass  # Settings not configured yet
    
    # Method 2: Try to run 'which tesseract' command
    try:
        result = subprocess.run(
            ['which', 'tesseract'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0 and result.stdout.strip():
            cmd_path = result.stdout.strip()
            if os.path.exists(cmd_path):
                return cmd_path
    except Exception as e:
        logger.debug(f"'which' command failed: {e}")
    
    # Method 3: Check common installation paths
    common_paths = [
        '/usr/bin/tesseract',
        '/usr/local/bin/tesseract',
        '/bin/tesseract',
        '/opt/homebrew/bin/tesseract',
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    # Method 4: Try running tesseract directly (might work if it's in PATH)
    try:
        result = subprocess.run(
            ['tesseract', '--version'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            return 'tesseract'  # It's in PATH
    except Exception:
        pass
    
    return None

# Set tesseract command
tesseract_cmd = find_tesseract_cmd()
if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    logger.info(f"Tesseract configured at: {tesseract_cmd}")
else:
    logger.error("Tesseract executable not found! OCR functionality will not work.")

# Optional PDF support
try:
    import PyPDF2
    from pdf2image import convert_from_bytes
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    logger.warning("PDF support not available. Install PyPDF2 and pdf2image for PDF extraction.")


class OCRProcessor:
    """
    OCR Processing utility class
    """
    
    SUPPORTED_LANGUAGES = {
        'eng': 'English',
        'kor': 'Korean',
        'uzb': 'Uzbek (Latin)',
        'uzb_cyrl': 'Uzbek (Cyrillic)',
    }
    
    @staticmethod
    def extract_text(image, language='eng', config=''):
        """
        Extract text from image using Tesseract OCR
        
        Args:
            image: PIL Image object
            language: Language code for OCR
            config: Additional Tesseract configuration
            
        Returns:
            Extracted text as string
        """
        try:
            text = pytesseract.image_to_string(image, lang=language, config=config)
            return text
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            raise
    
    @staticmethod
    def get_image_info(image):
        """
        Get detailed information about the image
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary with image information
        """
        return {
            'width': image.width,
            'height': image.height,
            'format': image.format,
            'mode': image.mode,
            'size': image.size,
        }
    
    @staticmethod
    def preprocess_image(image, enhance=False):
        """
        Preprocess image for better OCR results
        
        Args:
            image: PIL Image object
            enhance: Whether to enhance image quality
            
        Returns:
            Preprocessed PIL Image object
        """
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        if enhance:
            from PIL import ImageEnhance
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
        
        return image
    
    @staticmethod
    def get_confidence_scores(image, language='eng'):
        """
        Get confidence scores for OCR detection
        
        Args:
            image: PIL Image object
            language: Language code for OCR
            
        Returns:
            Dictionary with confidence data
        """
        try:
            data = pytesseract.image_to_data(
                image, 
                lang=language, 
                output_type=pytesseract.Output.DICT
            )
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'average_confidence': round(avg_confidence, 2),
                'min_confidence': min(confidences) if confidences else 0,
                'max_confidence': max(confidences) if confidences else 0,
                'total_words': len(confidences)
            }
        except Exception as e:
            logger.warning(f"Could not get confidence scores: {str(e)}")
            return None
    
    @classmethod
    def get_supported_languages(cls):
        """
        Get list of supported languages
        
        Returns:
            Dictionary of language codes and names
        """
        return cls.SUPPORTED_LANGUAGES
    
    @staticmethod
    def is_tesseract_installed():
        """
        Check if Tesseract is installed and accessible
        
        Returns:
            Boolean indicating if Tesseract is available
        """
        try:
            pytesseract.get_tesseract_version()
            return True
        except pytesseract.TesseractNotFoundError:
            return False
    
    @staticmethod
    def is_pdf_support_available():
        """
        Check if PDF support libraries are installed
        
        Returns:
            Boolean indicating if PDF processing is available
        """
        return PDF_SUPPORT


class PDFProcessor:
    """
    PDF Processing utility class for text extraction
    """
    
    @staticmethod
    def extract_text_from_pdf(pdf_file, language='eng', use_ocr=True):
        """
        Extract text from PDF file
        
        Args:
            pdf_file: File object or bytes of PDF
            language: Language code for OCR (if use_ocr=True)
            use_ocr: Whether to use OCR for scanned PDFs
            
        Returns:
            Dictionary with extracted text and metadata
        """
        if not PDF_SUPPORT:
            raise ImportError(
                "PDF support not available. Install required packages:\n"
                "pip install PyPDF2 pdf2image\n"
                "Also install poppler-utils: sudo apt-get install poppler-utils"
            )
        
        results = {
            'text': '',
            'pages': [],
            'total_pages': 0,
            'method': 'text_extraction',
            'has_text': False
        }
        
        try:
            # Read PDF file
            pdf_bytes = pdf_file.read() if hasattr(pdf_file, 'read') else pdf_file
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            
            results['total_pages'] = len(pdf_reader.pages)
            
            # Try text extraction first
            all_text = []
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                all_text.append(text)
                results['pages'].append({
                    'page_number': page_num,
                    'text': text,
                    'method': 'text_extraction'
                })
            
            combined_text = '\n\n'.join(all_text)
            
            # If no text found and OCR is enabled, use OCR
            if use_ocr and len(combined_text.strip()) < 50:
                logger.info("PDF appears to be scanned. Using OCR...")
                results = PDFProcessor._extract_with_ocr(
                    pdf_bytes, 
                    language, 
                    results['total_pages']
                )
            else:
                results['text'] = combined_text
                results['has_text'] = True
            
            return results
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise
    
    @staticmethod
    def _extract_with_ocr(pdf_bytes, language, total_pages):
        """
        Extract text from PDF using OCR (for scanned PDFs)
        
        Args:
            pdf_bytes: PDF file as bytes
            language: Language code for OCR
            total_pages: Total number of pages
            
        Returns:
            Dictionary with OCR results
        """
        results = {
            'text': '',
            'pages': [],
            'total_pages': total_pages,
            'method': 'ocr',
            'has_text': True
        }
        
        try:
            # Convert PDF to images
            images = convert_from_bytes(pdf_bytes)
            
            all_text = []
            for page_num, image in enumerate(images, 1):
                # Extract text from image using OCR
                text = OCRProcessor.extract_text(image, language=language)
                all_text.append(text)
                
                results['pages'].append({
                    'page_number': page_num,
                    'text': text,
                    'method': 'ocr',
                    'image_size': image.size
                })
            
            results['text'] = '\n\n'.join(all_text)
            
        except Exception as e:
            logger.error(f"Error during OCR extraction: {str(e)}")
            raise
        
        return results
    
    @staticmethod
    def extract_specific_pages(pdf_file, page_numbers: List[int], language='eng', use_ocr=True):
        """
        Extract text from specific pages of a PDF
        
        Args:
            pdf_file: PDF file object or bytes
            page_numbers: List of page numbers to extract (1-indexed)
            language: Language code for OCR
            use_ocr: Whether to use OCR for scanned pages
            
        Returns:
            Dictionary with extracted text from specified pages
        """
        if not PDF_SUPPORT:
            raise ImportError("PDF support not available")
        
        pdf_bytes = pdf_file.read() if hasattr(pdf_file, 'read') else pdf_file
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        
        results = {
            'text': '',
            'pages': [],
            'total_pages': len(pdf_reader.pages),
            'requested_pages': page_numbers
        }
        
        all_text = []
        for page_num in page_numbers:
            if page_num < 1 or page_num > len(pdf_reader.pages):
                logger.warning(f"Page {page_num} out of range")
                continue
            
            page = pdf_reader.pages[page_num - 1]
            text = page.extract_text()
            
            # Use OCR if no text found
            if use_ocr and len(text.strip()) < 50:
                # Convert specific page to image and OCR
                images = convert_from_bytes(
                    pdf_bytes, 
                    first_page=page_num, 
                    last_page=page_num
                )
                if images:
                    text = OCRProcessor.extract_text(images[0], language=language)
            
            all_text.append(text)
            results['pages'].append({
                'page_number': page_num,
                'text': text
            })
        
        results['text'] = '\n\n'.join(all_text)
        return results
