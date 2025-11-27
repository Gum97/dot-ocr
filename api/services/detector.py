"""
File type detection service
"""
import os
import mimetypes
from pathlib import Path
from typing import Tuple
from api.models.schemas import FileType

class FileTypeDetector:
    """Detects file types from uploaded files"""
    
    # MIME type mappings
    IMAGE_MIMES = {
        "image/jpeg", "image/jpg", "image/png", "image/gif", 
        "image/bmp", "image/webp", "image/tiff"
    }
    
    PDF_MIMES = {"application/pdf"}
    
    DOC_MIMES = {
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }
    
    @staticmethod
    def detect(file_path: str | Path) -> Tuple[FileType, str]:
        """
        Detect file type from file path
        
        Args:
            file_path: Path to file
            
        Returns:
            Tuple of (FileType, extension)
        """
        file_path = Path(file_path)
        
        # Get extension
        ext = file_path.suffix.lower()
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        
        # Detect by extension first (more reliable)
        if ext in {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}:
            return FileType.IMAGE, ext
        
        if ext == ".pdf":
            return FileType.PDF, ext
        
        if ext == ".docx":
            return FileType.DOCX, ext
        
        if ext == ".doc":
            return FileType.DOC, ext
        
        # Fallback to MIME type
        if mime_type:
            if mime_type in FileTypeDetector.IMAGE_MIMES:
                return FileType.IMAGE, ext
            
            if mime_type in FileTypeDetector.PDF_MIMES:
                return FileType.PDF, ext
            
            if mime_type in FileTypeDetector.DOC_MIMES:
                if ext == ".docx":
                    return FileType.DOCX, ext
                return FileType.DOC, ext
        
        # If we still can't detect, raise error
        raise ValueError(f"Unsupported file type: {ext} (MIME: {mime_type})")
    
    @staticmethod
    def is_supported(file_path: str | Path) -> bool:
        """Check if file type is supported"""
        try:
            FileTypeDetector.detect(file_path)
            return True
        except ValueError:
            return False
