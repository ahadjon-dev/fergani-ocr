"""
Service layer for OCR and PDF text extraction
Contains business logic separated from view layer for better maintainability
"""

import logging
import time
from typing import Any, Dict, Optional

from django.core.files.base import ContentFile
from django.utils import timezone
from PIL import Image

from .models import OCRDocument, OCRProcessingLog, OCRResult, PDFPageResult
from .utils import OCRProcessor, PDFProcessor

logger = logging.getLogger(__name__)


class OCRService:
    """
    Service class for handling OCR-related business logic
    """

    @staticmethod
    def process_image_extraction(image_file, language: str = "eng", save_to_db: bool = True) -> Dict[str, Any]:
        """
        Process image file and extract text using OCR

        Args:
            image_file: Uploaded image file
            language: Language code for OCR
            save_to_db: Whether to save the document and result to database

        Returns:
            Dictionary with extraction results including text, metadata, and confidence scores

        Raises:
            Exception: If image processing fails
        """
        start_time = time.time()
        document = None

        try:
            # Create document record if saving to DB
            if save_to_db:
                # Read file content for hash calculation
                file_content = image_file.read()
                image_file.seek(0)  # Reset file pointer

                file_hash = OCRDocument.calculate_file_hash(file_content)

                # Check for duplicate
                existing_doc = OCRDocument.objects.filter(file_hash=file_hash, is_deleted=False).first()

                if existing_doc and existing_doc.results.exists():
                    # Return cached result
                    latest_result = existing_doc.results.first()
                    logger.info(f"Returning cached result for document: {existing_doc.file_name}")

                    return {
                        "success": True,
                        "text": latest_result.extracted_text,
                        "filename": existing_doc.file_name,
                        "file_size": existing_doc.file_size,
                        "image_dimensions": f"{Image.open(image_file).width}x{Image.open(image_file).height}",
                        "image_format": Image.open(image_file).format or "Unknown",
                        "language": latest_result.language,
                        "character_count": latest_result.character_count,
                        "word_count": latest_result.word_count,
                        "confidence": (
                            {"average_confidence": latest_result.confidence_score} if latest_result.confidence_score else None
                        ),
                        "cached": True,
                        "document_id": str(existing_doc.uuid),
                    }

                # Create new document
                document = OCRDocument.objects.create(
                    file_name=image_file.name,
                    file_size=image_file.size,
                    file_hash=file_hash,
                    file_type="image",
                    language=language,
                    status="processing",
                )
                document.file.save(image_file.name, ContentFile(file_content), save=True)

                # Log start of processing
                OCRProcessingLog.objects.create(
                    document=document,
                    level="info",
                    message=f"Started OCR processing for {image_file.name}",
                    details={"language": language},
                )

            # Open image using PIL
            image = Image.open(image_file)

            # Get image info
            image_info = OCRProcessor.get_image_info(image)

            # Extract text using OCR processor
            extracted_text = OCRProcessor.extract_text(image, language=language)

            # Get confidence scores (optional)
            confidence_data = OCRProcessor.get_confidence_scores(image, language=language)

            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)

            # Save result to database
            if save_to_db and document:
                result = OCRResult.objects.create(
                    document=document,
                    extracted_text=extracted_text,
                    extraction_method="ocr",
                    language=language,
                    processing_time_ms=processing_time_ms,
                    confidence_score=confidence_data["average_confidence"] if confidence_data else None,
                )

                # Update document status
                document.status = "completed"
                document.processed_at = timezone.now()
                document.save(update_fields=["status", "processed_at"])

                # Log success
                OCRProcessingLog.objects.create(
                    document=document,
                    level="info",
                    message=f"Successfully extracted text from {image_file.name}",
                    details={
                        "word_count": result.word_count,
                        "character_count": result.character_count,
                        "processing_time_ms": processing_time_ms,
                    },
                )

            # Prepare response data
            result_data = {
                "success": True,
                "text": extracted_text,
                "filename": image_file.name,
                "file_size": image_file.size,
                "image_dimensions": f"{image_info['width']}x{image_info['height']}",
                "image_format": image_info["format"] or "Unknown",
                "language": language,
                "character_count": len(extracted_text.strip()),
                "word_count": len(extracted_text.strip().split()),
                "processing_time_ms": processing_time_ms,
            }

            # Add confidence data if available
            if confidence_data:
                result_data["confidence"] = confidence_data

            # Add document ID if saved to DB
            if save_to_db and document:
                result_data["document_id"] = str(document.uuid)
                result_data["cached"] = False

            return result_data

        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")

            # Log error to database
            if save_to_db and document:
                document.status = "failed"
                document.save(update_fields=["status"])

                OCRProcessingLog.objects.create(
                    document=document, level="error", message=f"Failed to process {image_file.name}", details={"error": str(e)}
                )

            raise

    @staticmethod
    def get_ocr_api_info(max_file_size: int) -> Dict[str, Any]:
        """
        Get OCR API information and capabilities

        Args:
            max_file_size: Maximum allowed file size in bytes

        Returns:
            Dictionary with API information
        """
        return {
            "message": "OCR Text Extraction API",
            "version": "1.0",
            "endpoint": "/api/ocr/extract/",
            "method": "POST",
            "supported_languages": OCRProcessor.get_supported_languages(),
            "max_file_size_mb": max_file_size / (1024 * 1024),
            "supported_formats": ["PNG", "JPEG", "TIFF", "BMP", "GIF", "WebP"],
            "tesseract_installed": OCRProcessor.is_tesseract_installed(),
        }

    @staticmethod
    def get_health_status() -> Dict[str, Any]:
        """
        Check OCR service health status

        Returns:
            Dictionary with health check information
        """
        tesseract_installed = OCRProcessor.is_tesseract_installed()

        tesseract_version = None
        if tesseract_installed:
            try:
                import pytesseract

                version = pytesseract.get_tesseract_version()
                # Convert Version object to string for JSON serialization
                tesseract_version = str(version) if version else None
            except Exception as e:
                logger.warning(f"Could not get Tesseract version: {e}")

        return {
            "status": "healthy" if tesseract_installed else "unhealthy",
            "tesseract_installed": tesseract_installed,
            "tesseract_version": tesseract_version,
            "supported_languages": len(OCRProcessor.get_supported_languages()),
        }

    @staticmethod
    def get_supported_languages() -> Dict[str, Any]:
        """
        Get list of supported OCR languages

        Returns:
            Dictionary with language information
        """
        languages = OCRProcessor.get_supported_languages()

        return {"success": True, "count": len(languages), "languages": languages}


class PDFService:
    """
    Service class for handling PDF-related business logic
    """

    @staticmethod
    def validate_pdf_file(file, max_file_size: int) -> tuple[bool, Optional[str]]:
        """
        Validate PDF file type and size

        Args:
            file: Uploaded file object
            max_file_size: Maximum allowed file size in bytes

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check content type
        is_pdf = file.content_type == "application/pdf" or file.name.lower().endswith(".pdf")

        if not is_pdf:
            return False, "Invalid file type. Please upload a PDF file."

        # Check file size
        if file.size > max_file_size:
            max_mb = max_file_size / (1024 * 1024)
            return False, f"File size exceeds maximum limit of {max_mb}MB"

        return True, None

    @staticmethod
    def process_pdf_extraction(
        pdf_file, language: str = "eng", use_ocr: bool = True, pages_param: Optional[str] = None, save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Process PDF file and extract text

        Args:
            pdf_file: Uploaded PDF file
            language: Language code for OCR
            use_ocr: Whether to use OCR for scanned PDFs
            pages_param: Comma-separated page numbers (e.g., "1,3,5")
            save_to_db: Whether to save the document and result to database

        Returns:
            Dictionary with extraction results

        Raises:
            ImportError: If PDF support libraries are not available
            Exception: If PDF processing fails
        """
        start_time = time.time()
        document = None

        try:
            # Create document record if saving to DB
            if save_to_db:
                # Read file content for hash calculation
                file_content = pdf_file.read()
                pdf_file.seek(0)  # Reset file pointer

                file_hash = OCRDocument.calculate_file_hash(file_content)

                # Check for duplicate
                existing_doc = OCRDocument.objects.filter(file_hash=file_hash, is_deleted=False, language=language).first()

                if existing_doc and existing_doc.results.exists():
                    # Return cached result
                    latest_result = existing_doc.results.first()
                    logger.info(f"Returning cached result for PDF: {existing_doc.file_name}")

                    # Get page results if available
                    page_results = []
                    for page in latest_result.pages.all():
                        page_results.append(
                            {
                                "page_number": page.page_number,
                                "text": page.extracted_text,
                                "word_count": page.word_count,
                                "character_count": page.character_count,
                                "method": page.extraction_method,
                            }
                        )

                    return {
                        "success": True,
                        "text": latest_result.extracted_text,
                        "filename": existing_doc.file_name,
                        "file_size": existing_doc.file_size,
                        "total_pages": len(page_results) if page_results else 0,
                        "method": latest_result.extraction_method,
                        "pages_extracted": len(page_results),
                        "character_count": latest_result.character_count,
                        "word_count": latest_result.word_count,
                        "language": latest_result.language,
                        "pages": page_results,
                        "cached": True,
                        "document_id": str(existing_doc.uuid),
                    }

                # Create new document
                document = OCRDocument.objects.create(
                    file_name=pdf_file.name,
                    file_size=pdf_file.size,
                    file_hash=file_hash,
                    file_type="pdf",
                    language=language,
                    status="processing",
                )
                document.file.save(pdf_file.name, ContentFile(file_content), save=True)

                # Log start of processing
                OCRProcessingLog.objects.create(
                    document=document,
                    level="info",
                    message=f"Started PDF processing for {pdf_file.name}",
                    details={"language": language, "use_ocr": use_ocr, "pages": pages_param},
                )

            # Extract text based on page selection
            if pages_param:
                # Extract specific pages
                page_numbers = [int(p.strip()) for p in pages_param.split(",")]
                result = PDFProcessor.extract_specific_pages(
                    pdf_file, page_numbers=page_numbers, language=language, use_ocr=use_ocr
                )
            else:
                # Extract all pages
                result = PDFProcessor.extract_text_from_pdf(pdf_file, language=language, use_ocr=use_ocr)

            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)

            # Save result to database
            if save_to_db and document:
                ocr_result = OCRResult.objects.create(
                    document=document,
                    extracted_text=result["text"],
                    extraction_method=result["method"],
                    language=language,
                    processing_time_ms=processing_time_ms,
                )

                # Save individual page results
                for page_data in result.get("pages", []):
                    PDFPageResult.objects.create(
                        result=ocr_result,
                        page_number=page_data["page_number"],
                        extracted_text=page_data["text"],
                        extraction_method=page_data.get("method", result["method"]),
                    )

                # Update document status
                document.status = "completed"
                document.processed_at = timezone.now()
                document.save(update_fields=["status", "processed_at"])

                # Log success
                OCRProcessingLog.objects.create(
                    document=document,
                    level="info",
                    message=f"Successfully extracted text from PDF {pdf_file.name}",
                    details={
                        "total_pages": result["total_pages"],
                        "method": result["method"],
                        "word_count": ocr_result.word_count,
                        "processing_time_ms": processing_time_ms,
                    },
                )

            # Prepare response data
            response_data = {
                "success": True,
                "text": result["text"],
                "filename": pdf_file.name,
                "file_size": pdf_file.size,
                "total_pages": result["total_pages"],
                "method": result["method"],
                "pages_extracted": len(result["pages"]),
                "character_count": len(result["text"].strip()),
                "word_count": len(result["text"].strip().split()),
                "language": language,
                "pages": result["pages"],
                "processing_time_ms": processing_time_ms,
            }

            # Add document ID if saved to DB
            if save_to_db and document:
                response_data["document_id"] = str(document.uuid)
                response_data["cached"] = False

            return response_data

        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")

            # Log error to database
            if save_to_db and document:
                document.status = "failed"
                document.save(update_fields=["status"])

                OCRProcessingLog.objects.create(
                    document=document,
                    level="error",
                    message=f"Failed to process PDF {pdf_file.name}",
                    details={"error": str(e)},
                )

            raise

    @staticmethod
    def get_pdf_api_info(max_file_size: int) -> Dict[str, Any]:
        """
        Get PDF API information and capabilities

        Args:
            max_file_size: Maximum allowed file size in bytes

        Returns:
            Dictionary with API information
        """
        return {
            "message": "PDF Text Extraction API",
            "version": "1.0",
            "endpoint": "/api/pdf/extract/",
            "method": "POST",
            "pdf_support_available": OCRProcessor.is_pdf_support_available(),
            "supported_languages": OCRProcessor.get_supported_languages(),
            "max_file_size_mb": max_file_size / (1024 * 1024),
            "features": [
                "Text extraction from text-based PDFs",
                "OCR for scanned PDFs",
                "Specific page extraction",
                "Multi-language support",
            ],
            "parameters": {
                "file": "PDF file (required)",
                "language": "Language code (optional, default: eng)",
                "use_ocr": "Use OCR for scanned PDFs (optional, default: true)",
                "pages": 'Comma-separated page numbers (optional, e.g., "1,3,5")',
            },
        }


class MultiFormatService:
    """
    Service class for handling multi-format file extraction
    """

    SUPPORTED_IMAGE_TYPES = ["image/png", "image/jpeg", "image/jpg", "image/tiff", "image/bmp", "image/gif", "image/webp"]

    @staticmethod
    def validate_file(file, max_file_size: int) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Validate file and determine its type

        Args:
            file: Uploaded file object
            max_file_size: Maximum allowed file size in bytes

        Returns:
            Tuple of (is_valid, error_message, file_type)
            file_type can be: 'pdf', 'image', or None if invalid
        """
        # Check file size
        if file.size > max_file_size:
            max_mb = max_file_size / (1024 * 1024)
            return False, f"File size exceeds maximum limit of {max_mb}MB", None

        # Determine file type
        if MultiFormatService._is_pdf(file):
            return True, None, "pdf"
        elif MultiFormatService._is_image(file):
            return True, None, "image"
        else:
            return False, "Unsupported file type. Supported formats: PDF, PNG, JPEG, TIFF, BMP, GIF, WebP", None

    @staticmethod
    def _is_pdf(file) -> bool:
        """Check if file is PDF"""
        return file.content_type == "application/pdf" or file.name.lower().endswith(".pdf")

    @staticmethod
    def _is_image(file) -> bool:
        """Check if file is an image"""
        return file.content_type in MultiFormatService.SUPPORTED_IMAGE_TYPES

    @staticmethod
    def process_file(file, language: str = "eng", save_to_db: bool = True) -> Dict[str, Any]:
        """
        Process file (PDF or image) and extract text

        Args:
            file: Uploaded file object
            language: Language code for OCR
            save_to_db: Whether to save the document and result to database

        Returns:
            Dictionary with extraction results

        Raises:
            ValueError: If file type is unsupported
            Exception: If processing fails
        """
        try:
            if MultiFormatService._is_pdf(file):
                # Use PDFService which handles DB saving
                return PDFService.process_pdf_extraction(
                    file, language=language, use_ocr=True, pages_param=None, save_to_db=save_to_db
                )
            elif MultiFormatService._is_image(file):
                # Use OCRService which handles DB saving
                return OCRService.process_image_extraction(file, language=language, save_to_db=save_to_db)
            else:
                raise ValueError("Unsupported file type")

        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            raise

    @staticmethod
    def get_api_info(max_file_size: int) -> Dict[str, Any]:
        """
        Get multi-format API information

        Args:
            max_file_size: Maximum allowed file size in bytes

        Returns:
            Dictionary with API information
        """
        return {
            "message": "Multi-Format Text Extraction API",
            "version": "1.0",
            "endpoint": "/api/extract/",
            "method": "POST",
            "supported_formats": {
                "images": ["PNG", "JPEG", "TIFF", "BMP", "GIF", "WebP"],
                "documents": ["PDF"] if OCRProcessor.is_pdf_support_available() else [],
            },
            "max_file_size_mb": max_file_size / (1024 * 1024),
            "features": [
                "Auto-detect file type",
                "OCR for images",
                "Text extraction and OCR for PDFs",
                "Multi-language support",
            ],
        }
