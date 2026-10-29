import os
import uuid
from pathlib import Path
from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from app.utils.file_security import sanitize_filename, validate_uploaded_file
from app.services.audio_service import audio_service
from app.config import settings

router = APIRouter(prefix="/audio", tags=["audio"])

class SpeakRequest(BaseModel):
    text: str
    lang: str = "en"

class SpeakResponse(BaseModel):
    audio_url: str
    filename: str

class TranscribeResponse(BaseModel):
    text: str
    filename: str

@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio_file(file: UploadFile = File(...)):
    """Transcribes an uploaded audio file into text."""
    ext = validate_uploaded_file(file)
    if ext not in [".mp3", ".wav", ".m4a", ".ogg"]:
        raise HTTPException(status_code=400, detail="Only audio files (.mp3, .wav, .m4a, .ogg) are supported.")

    safe_name = sanitize_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex[:8]}_{safe_name}"
    file_path = settings.UPLOAD_DIR / unique_name

    contents = await file.read()
    with open(str(file_path), "wb") as f:
        f.write(contents)

    transcription = audio_service.transcribe_audio(str(file_path))
    return TranscribeResponse(text=transcription, filename=safe_name)

@router.post("/speak", response_model=SpeakResponse)
def text_to_speech(req: SpeakRequest):
    """Converts input text to an MP3 audio file using Google Text-to-Speech."""
    filename, filepath = audio_service.text_to_speech(text=req.text, lang=req.lang)
    return SpeakResponse(
        audio_url=f"/api/audio/stream/{filename}",
        filename=filename
    )

@router.get("/stream/{filename}")
def stream_audio(filename: str):
    """Streams generated MP3 audio for browser playback."""
    safe_name = sanitize_filename(filename)
    file_path = settings.GENERATED_DIR / safe_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found.")

    return FileResponse(
        path=str(file_path),
        media_type="audio/mpeg",
        headers={"Accept-Ranges": "bytes"}
    )
