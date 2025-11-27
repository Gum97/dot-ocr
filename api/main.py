"""
FastAPI main application
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from api.config import settings
from api.routers import process

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    **dots.ocr API** - Intelligent Document Processing
    
    Features:
    - 🔍 Auto-detect file types (PDF, Images, DOC, DOCX)
    - 🔄 Auto-convert documents (DOC/DOCX → PDF)
    - 📝 OCR with multiple prompt modes
    - 🎯 Layout detection and analysis
    - 💻 CPU and GPU support (auto-detect)
    - 🌍 Multilingual support (100+ languages)
    
    Just upload your file and let the API handle the rest!
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(process.router)

# Mount static files (for serving results)
app.mount(
    "/results",
    StaticFiles(directory=str(settings.RESULTS_DIR)),
    name="results"
)

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("="*60)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Device: {settings.device_name}")
    logger.info(f"GPU Available: {settings.is_gpu_available}")
    logger.info(f"Model Path: {settings.MODEL_PATH}")
    logger.info(f"Use vLLM: {settings.USE_VLLM}")
    logger.info("="*60)

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Shutting down API server...")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "dots.ocr API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
