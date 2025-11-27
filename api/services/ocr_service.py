"""
OCR Service - Main processing logic
"""
import os
import uuid
import time
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from dots_ocr.parser import DotsOCRParser
from api.config import settings
from api.models.schemas import (
    FileType, ProcessingStatus, PromptMode, 
    ProcessResponse, LayoutElement
)
from api.services.detector import FileTypeDetector
from api.services.converter import DocumentConverter

logger = logging.getLogger(__name__)

class OCRService:
    """Main OCR processing service"""
    
    def __init__(self):
        """Initialize OCR service"""
        self.detector = FileTypeDetector()
        self.converter = DocumentConverter(
            use_libreoffice=settings.USE_LIBREOFFICE,
            libreoffice_path=settings.LIBREOFFICE_PATH
        )
        self.parser: Optional[DotsOCRParser] = None
        self._model_loaded = False
        
    def initialize_model(self):
        """Initialize the OCR model (lazy loading)"""
        if self._model_loaded:
            return
        
        logger.info(f"Initializing dots.ocr model on {settings.device_name}...")
        start_time = time.time()
        
        try:
            if settings.USE_VLLM:
                # Use vLLM server
                self.parser = DotsOCRParser(
                    ip=settings.VLLM_HOST,
                    port=settings.VLLM_PORT,
                    dpi=settings.DPI,
                    min_pixels=settings.MIN_PIXELS,
                    max_pixels=settings.MAX_PIXELS,
                    use_hf=False
                )
            else:
                # Use HuggingFace Transformers (works on CPU)
                self.parser = DotsOCRParser(
                    model_path=settings.MODEL_PATH,
                    dpi=settings.DPI,
                    min_pixels=settings.MIN_PIXELS,
                    max_pixels=settings.MAX_PIXELS,
                    use_hf=True  # Use HuggingFace backend
                )
            
            self._model_loaded = True
            load_time = time.time() - start_time
            logger.info(f"Model loaded successfully in {load_time:.2f}s on {settings.device_name}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise RuntimeError(f"Model initialization failed: {e}")
    
    def is_model_loaded(self) -> bool:
        """Check if model is loaded"""
        return self._model_loaded
    
    async def process_file(
        self, 
        file_path: str,
        original_filename: str,
        prompt_mode: PromptMode = PromptMode.LAYOUT_ALL,
        fitz_preprocess: bool = True,
        bbox: Optional[List[int]] = None
    ) -> ProcessResponse:
        """
        Process a file (auto-detect type and convert if needed)
        
        Args:
            file_path: Path to uploaded file
            original_filename: Original filename
            prompt_mode: Prompt mode for OCR
            fitz_preprocess: Enable fitz preprocessing
            bbox: Bounding box for grounding OCR
            
        Returns:
            ProcessResponse with results
        """
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Create result directory
        result_dir = settings.RESULTS_DIR / task_id
        result_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize response
        response = ProcessResponse(
            task_id=task_id,
            status=ProcessingStatus.PROCESSING,
            file_type=FileType.IMAGE,  # Will be updated
            original_filename=original_filename,
            created_at=datetime.now()
        )
        
        start_time = time.time()
        
        try:
            # Ensure model is loaded
            if not self._model_loaded:
                self.initialize_model()
            
            # Step 1: Detect file type
            logger.info(f"[{task_id}] Detecting file type: {original_filename}")
            file_type, ext = self.detector.detect(file_path)
            response.file_type = file_type
            
            # Step 2: Convert if needed
            process_path = file_path
            
            if file_type in [FileType.DOC, FileType.DOCX]:
                logger.info(f"[{task_id}] Converting DOCX to PDF...")
                pdf_path = self.converter.docx_to_pdf(
                    file_path, 
                    output_path=str(result_dir / f"{Path(original_filename).stem}.pdf")
                )
                process_path = pdf_path
                file_type = FileType.PDF
                response.file_type = FileType.PDF
            
            # Step 3: Process with OCR
            logger.info(f"[{task_id}] Processing with OCR (prompt: {prompt_mode})...")
            
            if file_type == FileType.PDF:
                results = self.parser.parse_pdf(
                    input_path=process_path,
                    filename=f"task_{task_id}",
                    prompt_mode=prompt_mode.value,
                    save_dir=str(result_dir)
                )
                response.total_pages = len(results)
            else:
                # Image processing
                results = self.parser.parse_image(
                    input_path=process_path,
                    filename=f"task_{task_id}",
                    prompt_mode=prompt_mode.value,
                    save_dir=str(result_dir),
                    fitz_preprocess=fitz_preprocess
                )
                response.total_pages = 1
            
            # Step 4: Parse results
            logger.info(f"[{task_id}] Parsing results...")
            
            # Combine markdown content
            markdown_parts = []
            all_layout_elements = []
            
            for result in results:
                # Read markdown
                if 'md_content_path' in result and os.path.exists(result['md_content_path']):
                    with open(result['md_content_path'], 'r', encoding='utf-8') as f:
                        markdown_parts.append(f.read())
                
                # Read layout elements
                if 'layout_info_path' in result and os.path.exists(result['layout_info_path']):
                    with open(result['layout_info_path'], 'r', encoding='utf-8') as f:
                        layout_data = json.load(f)
                        for elem in layout_data:
                            all_layout_elements.append(
                                LayoutElement(
                                    bbox=elem.get('bbox', []),
                                    category=elem.get('category', ''),
                                    text=elem.get('text')
                                )
                            )
            
            response.markdown_content = "\n\n---\n\n".join(markdown_parts)
            response.layout_elements = all_layout_elements
            
            # Set file URLs (relative to result directory)
            if results:
                first_result = results[0]
                if 'layout_image_path' in first_result:
                    response.layout_image_url = f"/results/{task_id}/{os.path.basename(first_result['layout_image_path'])}"
                if 'layout_info_path' in first_result:
                    response.json_url = f"/results/{task_id}/{os.path.basename(first_result['layout_info_path'])}"
                if 'md_content_path' in first_result:
                    response.markdown_url = f"/results/{task_id}/{os.path.basename(first_result['md_content_path'])}"
            
            # Step 5: Finalize response
            processing_time = time.time() - start_time
            
            response.status = ProcessingStatus.COMPLETED
            response.processing_time = processing_time
            response.device_used = settings.device_name
            response.completed_at = datetime.now()
            response.message = f"Successfully processed {len(results)} {'page' if len(results) == 1 else 'pages'}"
            
            logger.info(f"[{task_id}] Processing completed in {processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"[{task_id}] Processing failed: {e}", exc_info=True)
            response.status = ProcessingStatus.FAILED
            response.error = str(e)
            response.completed_at = datetime.now()
            
            import traceback
            response.traceback = traceback.format_exc()
        
        return response

# Global service instance
ocr_service = OCRService()
