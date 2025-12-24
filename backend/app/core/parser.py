import fitz
from PIL import Image
import io
import pytesseract
from typing import Dict
from tempfile import NamedTemporaryFile
from pathlib import Path


class PDFParser:
    """"PDF Parser to extract text from PDF files."""

    def _extract_text(self, file_path: str) -> str:
        """Extract text from a PDF file.

        Args:
            file_path (str): Path to the PDF file.
        Returns:
            str: Extracted text.    
        """
        text = ""
        try:
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text() or ""
        except Exception as e:
            print(f"Error reading PDF with PyMuPDF: {e}")
            text = self._extract_text_with_ocr(file_path)
        return text

    def _extract_text_with_ocr(self, file_path: str) -> str:    
        """Extract text from a PDF file using OCR.

        Args:
            file_path (str): Path to the PDF file.  
        Returns:
            str: Extracted text.
        """
        text = ""
        try:
            doc = fitz.open(file_path)
            for page in doc:
                pix = page.get_pixmap(dpi=300)
                img_bytes = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_bytes))
                text += pytesseract.image_to_string(image)
        except Exception as e:
            print(f"Error during OCR extraction: {e}")
        return text
    
    def parse_pdf(self, pdf_bytes: bytes, filename: str) -> Dict[str, any]:
        """Parse PDF bytes and extract text.
        Args:
            pdf_bytes (bytes): PDF file content in bytes.
            filename (str): Original filename of the PDF.
        Returns:
            Dict[str, any]: Dictionary containing filename, raw_text, text_length, and success status.
        """
        
        with NamedTemporaryFile(delete=True, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp.flush()
            pdf_path = Path(tmp.name)
            try:
                text = self._extract_text(str(pdf_path))
            except Exception as e:
                print(f"Error extracting text: {e}")    
                text = self._extract_text_with_ocr(str(pdf_path))

        if len(text) < 50:
            raise ValueError("Text extraction failed")

        return {
            "filename": filename,
            "raw_text": text,
            "text_length": len(text),
            "success": True
        }


parser = PDFParser()