import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database.session import init_db
from app.api import health, chat, documents, search, audio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB tables
    logger.info("Initializing database tables...")
    try:
        init_db()
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
    yield
    # Shutdown
    logger.info("Shutting down application...")

app = FastAPI(
    title=settings.APP_NAME,
    description="Beginner-friendly Multimodal AI Chatbot MVP with RAG, Web Search, Document Editing, Audio, and Emotional Assistance.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for React frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(audio.router, prefix="/api")

# Mount uploads and generated files for static serving if required
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")
app.mount("/generated", StaticFiles(directory=str(settings.GENERATED_DIR)), name="generated")

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "/docs",
        "health": "/api/health",
        "download_zip": "/api/download-zip"
    }

@app.get("/api/download-zip")
@app.get("/download")
def download_chatbot_zip():
    """Direct browser download of the complete chatbot zip file."""
    zip_path = Path(r"C:\Users\Anant\Desktop\multimodal-ai-chatbot.zip")
    if not zip_path.exists():
        zip_path = Path(r"C:\Users\Anant\.gemini\antigravity\scratch\multimodal-ai-chatbot.zip")
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="ZIP archive not found on server.")
    return FileResponse(
        path=str(zip_path),
        filename="multimodal-ai-chatbot.zip",
        media_type="application/zip"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
