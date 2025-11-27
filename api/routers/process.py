"""
Unified processing API endpoint
"""
import os
import logging
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from api.config import settings
from api.models.schemas import (
    PromptMode, ProcessResponse, ErrorResponse
)
from api.services.ocr_service import ocr_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Process"])

@router.post("/process", response_model=ProcessResponse)
async def process_document(
    file: UploadFile = File(..., description="File to process (PDF, Image, DOC, DOCX)"),
    prompt_mode: PromptMode = Form(
        default=PromptMode.LAYOUT_ALL,
        description="Prompt mode for OCR processing"
    ),
    fitz_preprocess: bool = Form(
        default=True,
        description="Enable fitz preprocessing for images"
    ),
    bbox: Optional[str] = Form(
        default=None,
        description="Bounding box for grounding OCR, format: 'x1,y1,x2,y2'"
    )
):
    """
    **Unified endpoint to process any document type**
    
    This endpoint automatically:
    - Detects file type (PDF, Image, DOC, DOCX)
    - Converts DOC/DOCX to PDF if needed
    - Performs OCR with specified prompt mode
    - Returns structured results
    
    **Supported file types:**
    - Images: JPG, PNG, GIF, BMP, WEBP, TIFF
    - Documents: PDF, DOC, DOCX
    
    **Prompt modes:**
    - `prompt_layout_all_en`: Full layout analysis + OCR
    - `prompt_layout_only_en`: Layout detection only
    - `prompt_ocr`: OCR text only
    - `prompt_grounding_ocr`: OCR with bounding box (requires bbox parameter)
    
    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/process" \\
      -F "file=@document.pdf" \\
      -F "prompt_mode=prompt_layout_all_en"
    ```
    """
    try:
        # Validate file size
        file_size = 0
        chunk_size = 1024 * 1024  # 1MB chunks
        content = bytearray()
        
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            file_size += len(chunk)
            content.extend(chunk)
            
            if file_size > settings.MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024:.0f}MB"
                )
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Save uploaded file
        upload_path = settings.UPLOAD_DIR / file.filename
        upload_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(upload_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Uploaded file: {file.filename} ({file_size / 1024:.1f}KB)")
        
        # Parse bbox if provided
        bbox_list = None
        if bbox:
            try:
                bbox_list = [int(x.strip()) for x in bbox.split(',')]
                if len(bbox_list) != 4:
                    raise ValueError("bbox must have 4 values")
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid bbox format. Expected 'x1,y1,x2,y2', got: {bbox}"
                )
        
        # Process the file
        response = await ocr_service.process_file(
            file_path=str(upload_path),
            original_filename=file.filename,
            prompt_mode=prompt_mode,
            fitz_preprocess=fitz_preprocess,
            bbox=bbox_list
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns system status and model information
    """
    import time
    
    # Try to initialize model if not loaded
    model_loaded = ocr_service.is_model_loaded()
    if not model_loaded:
        try:
            ocr_service.initialize_model()
            model_loaded = True
        except:
            pass
    
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "device": settings.device_name,
        "gpu_available": settings.is_gpu_available,
        "model_loaded": model_loaded,
        "timestamp": time.time()
    }
