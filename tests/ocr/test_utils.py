"""
Tests for OCR utility functions
"""

import io
from unittest.mock import MagicMock, patch

import pytesseract
from django.test import TestCase
from PIL import Image

from ocr.utils import OCRProcessor, PDFProcessor


class OCRProcessorTestCase(TestCase):
    """Test cases for OCRProcessor utility class"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a simple test image
        self.test_image = Image.new("RGB", (100, 100), color="white")

    def test_extract_text_success(self):
        """Test successful text extraction from image"""
        with patch("pytesseract.image_to_string") as mock_ocr:
            mock_ocr.return_value = "Test text"

            result = OCRProcessor.extract_text(self.test_image, language="eng")

            self.assertEqual(result, "Test text")
            mock_ocr.assert_called_once_with(self.test_image, lang="eng", config="")

    def test_extract_text_with_config(self):
        """Test text extraction with custom config"""
        with patch("pytesseract.image_to_string") as mock_ocr:
            mock_ocr.return_value = "Test text"

            result = OCRProcessor.extract_text(self.test_image, language="ara", config="--psm 6")

            self.assertEqual(result, "Test text")
            mock_ocr.assert_called_once_with(self.test_image, lang="ara", config="--psm 6")

    def test_extract_text_error(self):
        """Test error handling in text extraction"""
        with patch("pytesseract.image_to_string") as mock_ocr:
            mock_ocr.side_effect = Exception("OCR failed")

            with self.assertRaises(Exception):
                OCRProcessor.extract_text(self.test_image)

    def test_get_image_info(self):
        """Test getting image information"""
        info = OCRProcessor.get_image_info(self.test_image)

        self.assertEqual(info["width"], 100)
        self.assertEqual(info["height"], 100)
        self.assertEqual(info["size"], (100, 100))
        self.assertEqual(info["mode"], "RGB")

    def test_preprocess_image_no_enhancement(self):
        """Test image preprocessing without enhancement"""
        # Create image in different mode
        grayscale_image = Image.new("L", (100, 100), color=128)

        result = OCRProcessor.preprocess_image(grayscale_image, enhance=False)

        self.assertEqual(result.mode, "RGB")
        self.assertEqual(result.size, (100, 100))

    def test_preprocess_image_with_enhancement(self):
        """Test image preprocessing with enhancement"""
        result = OCRProcessor.preprocess_image(self.test_image, enhance=True)

        self.assertEqual(result.mode, "RGB")
        self.assertEqual(result.size, (100, 100))

    def test_preprocess_image_already_rgb(self):
        """Test preprocessing image that's already RGB"""
        result = OCRProcessor.preprocess_image(self.test_image, enhance=False)

        self.assertEqual(result.mode, "RGB")

    def test_get_confidence_scores_success(self):
        """Test getting confidence scores from OCR"""
        mock_data = {"conf": ["95", "87", "92", "88", "-1", "90"], "text": ["Hello", "World", "Test", "OCR", "", "Data"]}

        with patch("pytesseract.image_to_data") as mock_ocr:
            mock_ocr.return_value = mock_data

            result = OCRProcessor.get_confidence_scores(self.test_image, language="eng")

            self.assertIsNotNone(result)
            self.assertIn("average_confidence", result)
            self.assertIn("min_confidence", result)
            self.assertIn("max_confidence", result)
            self.assertIn("total_words", result)

            # Average of 95, 87, 92, 88, 90 = 90.4
            self.assertAlmostEqual(result["average_confidence"], 90.4, places=1)
            self.assertEqual(result["min_confidence"], 87)
            self.assertEqual(result["max_confidence"], 95)
            self.assertEqual(result["total_words"], 5)

    def test_get_confidence_scores_empty(self):
        """Test confidence scores with no valid data"""
        mock_data = {"conf": ["-1", "-1", "-1"], "text": ["", "", ""]}

        with patch("pytesseract.image_to_data") as mock_ocr:
            mock_ocr.return_value = mock_data

            result = OCRProcessor.get_confidence_scores(self.test_image)

            self.assertIsNotNone(result)
            self.assertEqual(result["average_confidence"], 0)
            self.assertEqual(result["total_words"], 0)

    def test_get_confidence_scores_error(self):
        """Test confidence score error handling"""
        with patch("pytesseract.image_to_data") as mock_ocr:
            mock_ocr.side_effect = Exception("OCR failed")

            result = OCRProcessor.get_confidence_scores(self.test_image)

            self.assertIsNone(result)

    def test_get_supported_languages(self):
        """Test getting supported languages"""
        languages = OCRProcessor.get_supported_languages()

        self.assertIsInstance(languages, dict)
        self.assertIn("eng", languages)
        self.assertIn("ara", languages)
        self.assertEqual(languages["eng"], "English")
        self.assertEqual(languages["ara"], "Arabic")

    def test_is_tesseract_installed_true(self):
        """Test tesseract installation check when installed"""
        with patch("pytesseract.get_tesseract_version") as mock_version:
            mock_version.return_value = "5.0.0"

            result = OCRProcessor.is_tesseract_installed()

            self.assertTrue(result)

    def test_is_tesseract_installed_false(self):
        """Test tesseract installation check when not installed"""
        with patch("pytesseract.get_tesseract_version") as mock_version:
            mock_version.side_effect = pytesseract.TesseractNotFoundError()

            result = OCRProcessor.is_tesseract_installed()

            self.assertFalse(result)

    def test_is_pdf_support_available(self):
        """Test PDF support availability check"""
        # This will return True if libraries are installed, False otherwise
        result = OCRProcessor.is_pdf_support_available()

        self.assertIsInstance(result, bool)


class PDFProcessorTestCase(TestCase):
    """Test cases for PDFProcessor utility class"""

    def test_extract_text_from_pdf_no_support(self):
        """Test PDF extraction when PDF support is not available"""
        with patch("ocr.utils.PDF_SUPPORT", False):
            pdf_file = io.BytesIO(b"fake pdf content")

            with self.assertRaises(ImportError) as context:
                PDFProcessor.extract_text_from_pdf(pdf_file)

            self.assertIn("PDF support not available", str(context.exception))

    @patch("ocr.utils.PDF_SUPPORT", True)
    def test_extract_text_from_pdf_with_text(self):
        """Test PDF extraction when PDF contains extractable text"""
        # Mock PDF with text
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "This is extracted text from PDF page."

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]

        with patch("PyPDF2.PdfReader", return_value=mock_reader):
            pdf_content = b"%PDF-1.4 fake pdf"
            pdf_file = io.BytesIO(pdf_content)

            result = PDFProcessor.extract_text_from_pdf(pdf_file, use_ocr=False)

            self.assertTrue(result["has_text"])
            self.assertEqual(result["total_pages"], 1)
            self.assertEqual(result["method"], "text_extraction")
            self.assertIn("This is extracted text", result["text"])

    @patch("ocr.utils.PDF_SUPPORT", True)
    def test_extract_text_from_pdf_scanned(self):
        """Test PDF extraction when PDF is scanned (no extractable text)"""
        # Mock PDF with no text (scanned)
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "   "  # Whitespace only

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]

        mock_image = Image.new("RGB", (100, 100), color="white")

        with (
            patch("PyPDF2.PdfReader", return_value=mock_reader),
            patch("ocr.utils.convert_from_bytes", return_value=[mock_image]),
            patch.object(OCRProcessor, "extract_text", return_value="OCR extracted text"),
        ):

            pdf_content = b"%PDF-1.4 fake scanned pdf"
            pdf_file = io.BytesIO(pdf_content)

            result = PDFProcessor.extract_text_from_pdf(pdf_file, language="eng", use_ocr=True)

            self.assertTrue(result["has_text"])
            self.assertEqual(result["method"], "ocr")
            self.assertIn("OCR extracted text", result["text"])

    @patch("ocr.utils.PDF_SUPPORT", True)
    def test_extract_text_from_pdf_error(self):
        """Test PDF extraction error handling"""
        with patch("PyPDF2.PdfReader") as mock_reader:
            mock_reader.side_effect = Exception("Invalid PDF")

            pdf_file = io.BytesIO(b"invalid pdf")

            with self.assertRaises(Exception):
                PDFProcessor.extract_text_from_pdf(pdf_file)

    @patch("ocr.utils.PDF_SUPPORT", True)
    def test_extract_with_ocr_success(self):
        """Test OCR extraction from PDF"""
        mock_image = Image.new("RGB", (100, 100), color="white")

        with (
            patch("ocr.utils.convert_from_bytes", return_value=[mock_image]),
            patch.object(OCRProcessor, "extract_text", return_value="OCR text"),
        ):

            result = PDFProcessor._extract_with_ocr(b"pdf bytes", "eng", 1)

            self.assertEqual(result["method"], "ocr")
            self.assertTrue(result["has_text"])
            self.assertEqual(result["total_pages"], 1)
            self.assertIn("OCR text", result["text"])

    @patch("ocr.utils.PDF_SUPPORT", True)
    def test_extract_with_ocr_error(self):
        """Test OCR extraction error handling"""
        with patch("ocr.utils.convert_from_bytes") as mock_convert:
            mock_convert.side_effect = Exception("Conversion failed")

            with self.assertRaises(Exception):
                PDFProcessor._extract_with_ocr(b"pdf bytes", "eng", 1)

    @patch("ocr.utils.PDF_SUPPORT", True)
    def test_extract_specific_pages_success(self):
        """Test extracting specific pages from PDF"""
        # Mock PDF with multiple pages
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 text"

        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 text"

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page1, mock_page2]

        with patch("PyPDF2.PdfReader", return_value=mock_reader):
            pdf_content = b"%PDF-1.4 fake pdf"
            pdf_file = io.BytesIO(pdf_content)

            result = PDFProcessor.extract_specific_pages(pdf_file, page_numbers=[1], use_ocr=False)

            self.assertEqual(result["total_pages"], 2)
            self.assertEqual(result["requested_pages"], [1])
            self.assertIn("Page 1 text", result["text"])
            self.assertEqual(len(result["pages"]), 1)

    @patch("ocr.utils.PDF_SUPPORT", True)
    def test_extract_specific_pages_out_of_range(self):
        """Test extracting pages with out of range page numbers"""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Page 1 text"

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]

        with patch("PyPDF2.PdfReader", return_value=mock_reader):
            pdf_content = b"%PDF-1.4 fake pdf"
            pdf_file = io.BytesIO(pdf_content)

            # Request page that doesn't exist
            result = PDFProcessor.extract_specific_pages(
                pdf_file, page_numbers=[1, 5, 10], use_ocr=False  # Only page 1 exists
            )

            self.assertEqual(len(result["pages"]), 1)  # Only page 1 extracted

    @patch("ocr.utils.PDF_SUPPORT", True)
    def test_extract_specific_pages_with_ocr(self):
        """Test extracting specific pages using OCR for scanned content"""
        # Mock page with no text
        mock_page = MagicMock()
        mock_page.extract_text.return_value = ""

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]

        mock_image = Image.new("RGB", (100, 100), color="white")

        with (
            patch("PyPDF2.PdfReader", return_value=mock_reader),
            patch("ocr.utils.convert_from_bytes", return_value=[mock_image]),
            patch.object(OCRProcessor, "extract_text", return_value="OCR page text"),
        ):

            pdf_content = b"%PDF-1.4 fake scanned pdf"
            pdf_file = io.BytesIO(pdf_content)

            result = PDFProcessor.extract_specific_pages(pdf_file, page_numbers=[1], language="ara", use_ocr=True)

            self.assertIn("OCR page text", result["text"])

    def test_extract_specific_pages_no_support(self):
        """Test specific page extraction when PDF support is not available"""
        with patch("ocr.utils.PDF_SUPPORT", False):
            pdf_file = io.BytesIO(b"fake pdf")

            with self.assertRaises(ImportError) as context:
                PDFProcessor.extract_specific_pages(pdf_file, [1])

            self.assertIn("PDF support not available", str(context.exception))
