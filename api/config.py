"""
Configuration settings for the API
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional
import torch

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "dots.ocr API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Model Configuration
    MODEL_PATH: str = "./weights/DotsOCR"
    USE_VLLM: bool = False  # Use transformers by default (easier for CPU)
    VLLM_HOST: str = "127.0.0.1"
    VLLM_PORT: int = 8000
    
    # Auto-detect device (CPU/GPU)
    DEVICE: str = "auto"  # auto, cpu, cuda
    
    # OCR Settings
    DPI: int = 200
    MIN_PIXELS: int = 256 * 28 * 28
    MAX_PIXELS: int = 1280 * 28 * 28
    
    # Upload Settings
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".jpg", ".jpeg", ".png", ".docx", ".doc"}
    
    # Storage
    UPLOAD_DIR: Path = Path("./uploads")
    RESULTS_DIR: Path = Path("./results")
    TEMP_DIR: Path = Path("./temp")
    
    # Document Conversion
    USE_LIBREOFFICE: bool = False  # Use python-docx by default
    LIBREOFFICE_PATH: Optional[str] = None
    
    # Task Queue (optional, for background processing)
    USE_REDIS: bool = False
    REDIS_URL: str = "redis://localhost:6379"
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    @property
    def device_name(self) -> str:
        """Auto-detect and return device name"""
        if self.DEVICE == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return self.DEVICE
    
    @property
    def is_gpu_available(self) -> bool:
        """Check if GPU is available"""
        return torch.cuda.is_available()

# Global settings instance
settings = Settings()
