"""
Pydantic models for request/response schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

class PromptMode(str, Enum):
    """Available prompt modes"""
    LAYOUT_ALL = "prompt_layout_all_en"
    LAYOUT_ONLY = "prompt_layout_only_en"
    OCR_ONLY = "prompt_ocr"
    GROUNDING_OCR = "prompt_grounding_ocr"

class FileType(str, Enum):
    """Supported file types"""
    PDF = "pdf"
    IMAGE = "image"
    DOCX = "docx"
    DOC = "doc"

class ProcessingStatus(str, Enum):
    """Processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ProcessRequest(BaseModel):
    """Request for processing a document"""
    prompt_mode: PromptMode = Field(
        default=PromptMode.LAYOUT_ALL,
        description="Prompt mode for OCR processing"
    )
    fitz_preprocess: bool = Field(
        default=True,
        description="Enable fitz preprocessing for images"
    )
    bbox: Optional[List[int]] = Field(
        default=None,
        description="Bounding box for grounding OCR [x1, y1, x2, y2]"
    )

class LayoutElement(BaseModel):
    """Layout element in the result"""
    bbox: List[float]
    category: str
    text: Optional[str] = None

class ProcessResponse(BaseModel):
    """Response from processing"""
    model_config = {'protected_namespaces': ()}  # Allow model_ prefix
    
    task_id: str
    status: ProcessingStatus
    file_type: FileType
    original_filename: str
    message: Optional[str] = None
    
    # Results (when completed)
    markdown_content: Optional[str] = None
    layout_elements: Optional[List[LayoutElement]] = None
    layout_image_url: Optional[str] = None
    json_url: Optional[str] = None
    markdown_url: Optional[str] = None
    
    # Metadata
    total_pages: Optional[int] = None
    processing_time: Optional[float] = None
    device_used: Optional[str] = None
    model_info: Optional[Dict[str, Any]] = None
    
    # Error info
    error: Optional[str] = None
    traceback: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

class TaskStatusResponse(BaseModel):
    """Response for task status check"""
    task_id: str
    status: ProcessingStatus
    progress: Optional[int] = Field(default=None, ge=0, le=100)
    message: Optional[str] = None
    result_url: Optional[str] = None

class HealthResponse(BaseModel):
    """Health check response"""
    model_config = {'protected_namespaces': ()}  # Allow model_ prefix
    
    status: str
    version: str
    device: str
    gpu_available: bool
    model_loaded: bool
    uptime: float

class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    task_id: Optional[str] = None
