"""
Document conversion service (DOC/DOCX to PDF/Image)
"""
import os
import subprocess
from pathlib import Path
from typing import Optional, List
from PIL import Image
import tempfile
import logging

logger = logging.getLogger(__name__)

class DocumentConverter:
    """Converts documents between formats"""
    
    def __init__(self, use_libreoffice: bool = False, libreoffice_path: Optional[str] = None):
        """
        Initialize converter
        
        Args:
            use_libreoffice: Use LibreOffice for conversion (more accurate)
            libreoffice_path: Path to LibreOffice executable
        """
        self.use_libreoffice = use_libreoffice
        self.libreoffice_path = libreoffice_path or self._find_libreoffice()
    
    def _find_libreoffice(self) -> Optional[str]:
        """Try to find LibreOffice installation"""
        possible_paths = [
            "libreoffice",
            "/usr/bin/libreoffice",
            "/usr/local/bin/libreoffice",
            "C:\\Program Files\\LibreOffice\\program\\soffice.exe",
            "C:\\Program Files (x86)\\LibreOffice\\program\\soffice.exe",
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run(
                    [path, "--version"], 
                    capture_output=True, 
                    timeout=5
                )
                if result.returncode == 0:
                    logger.info(f"Found LibreOffice at: {path}")
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                continue
        
        logger.warning("LibreOffice not found, will use python-docx fallback")
        return None
    
    def docx_to_pdf_libreoffice(self, docx_path: str, output_dir: Optional[str] = None) -> str:
        """
        Convert DOCX to PDF using LibreOffice
        
        Args:
            docx_path: Path to DOCX file
            output_dir: Output directory (default: same as input)
            
        Returns:
            Path to generated PDF
        """
        if not self.libreoffice_path:
            raise RuntimeError("LibreOffice not available")
        
        docx_path = Path(docx_path).resolve()
        output_dir = Path(output_dir or docx_path.parent).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Run LibreOffice conversion
        cmd = [
            str(self.libreoffice_path),
            "--headless",
            "--convert-to", "pdf",
            "--outdir", str(output_dir),
            str(docx_path)
        ]
        
        logger.info(f"Running LibreOffice conversion: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"LibreOffice conversion failed: {result.stderr}")
        
        # Expected output PDF name
        pdf_name = docx_path.stem + ".pdf"
        pdf_path = output_dir / pdf_name
        
        if not pdf_path.exists():
            raise RuntimeError(f"PDF not generated at expected path: {pdf_path}")
        
        logger.info(f"Successfully converted to PDF: {pdf_path}")
        return str(pdf_path)
    
    def docx_to_pdf_python(self, docx_path: str, output_path: Optional[str] = None) -> str:
        """
        Convert DOCX to PDF using python-docx + reportlab
        Note: This is a basic conversion, may not preserve all formatting
        
        Args:
            docx_path: Path to DOCX file
            output_path: Output PDF path
            
        Returns:
            Path to generated PDF
        """
        try:
            from docx import Document
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
        except ImportError as e:
            raise RuntimeError(
                "Missing dependencies for DOCX conversion. "
                "Install with: pip install python-docx reportlab"
            ) from e
        
        docx_path = Path(docx_path)
        if not output_path:
            output_path = docx_path.parent / f"{docx_path.stem}.pdf"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Read DOCX
        doc = Document(str(docx_path))
        
        # Create PDF
        pdf = SimpleDocTemplate(str(output_path), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Convert paragraphs
        for para in doc.paragraphs:
            if para.text.strip():
                p = Paragraph(para.text, styles['Normal'])
                story.append(p)
                story.append(Spacer(1, 12))
        
        pdf.build(story)
        
        logger.info(f"Successfully converted to PDF (python): {output_path}")
        return str(output_path)
    
    def docx_to_pdf(self, docx_path: str, output_path: Optional[str] = None) -> str:
        """
        Convert DOCX to PDF (auto-select method)
        
        Args:
            docx_path: Path to DOCX file
            output_path: Output PDF path
            
        Returns:
            Path to generated PDF
        """
        if self.use_libreoffice and self.libreoffice_path:
            return self.docx_to_pdf_libreoffice(docx_path, output_path)
        else:
            return self.docx_to_pdf_python(docx_path, output_path)
    
    def pdf_to_images(self, pdf_path: str, output_dir: Optional[str] = None, dpi: int = 200) -> List[str]:
        """
        Convert PDF pages to images
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Output directory
            dpi: DPI for conversion
            
        Returns:
            List of image paths
        """
        try:
            from pdf2image import convert_from_path
        except ImportError as e:
            raise RuntimeError(
                "Missing pdf2image. Install with: pip install pdf2image"
            ) from e
        
        pdf_path = Path(pdf_path)
        output_dir = Path(output_dir or pdf_path.parent)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert PDF to images
        images = convert_from_path(str(pdf_path), dpi=dpi)
        
        image_paths = []
        for i, img in enumerate(images):
            img_path = output_dir / f"{pdf_path.stem}_page_{i+1}.png"
            img.save(str(img_path), "PNG")
            image_paths.append(str(img_path))
        
        logger.info(f"Converted {len(image_paths)} pages to images")
        return image_paths
