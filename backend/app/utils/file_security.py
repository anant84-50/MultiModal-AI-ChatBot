import re
import os
from pathlib import Path
from fastapi import HTTPException, UploadFile
from app.config import settings

def sanitize_filename(filename: str) -> str:
    """Removes dangerous characters and path traversal sequences from filenames."""
    basename = os.path.basename(filename)
    clean_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', basename)
    return clean_name or "uploaded_file"

def validate_uploaded_file(file: UploadFile) -> str:
    """
    Validates file extension and ensures file exists and conforms to security boundaries.
    Returns the file extension (lowercase).
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")
    
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File extension '{ext}' is not supported. Allowed formats: {', '.join(sorted(settings.ALLOWED_EXTENSIONS))}"
        )
    return ext

def detect_file_category(extension: str) -> str:
    """Classifies file extension into image, pdf, docx, txt, audio, or document."""
    ext = extension.lower()
    if ext in [".png", ".jpg", ".jpeg", ".webp", ".gif"]:
        return "image"
    elif ext == ".pdf":
        return "pdf"
    elif ext in [".docx", ".doc"]:
        return "docx"
    elif ext in [".txt", ".md"]:
        return "text"
    elif ext in [".mp3", ".wav", ".m4a", ".ogg"]:
        return "audio"
    return "document"
