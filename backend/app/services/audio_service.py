import os
import uuid
import logging
from pathlib import Path
from typing import Tuple
from gtts import gTTS

from app.config import settings

logger = logging.getLogger("audio_service")

class AudioService:
    def text_to_speech(self, text: str, lang: str = "en") -> Tuple[str, str]:
        """
        Converts text to an MP3 audio file using Google Text-to-Speech (gTTS).
        Saves output to generated/ directory.
        Returns (filename, filepath).
        """
        # Trim text to reasonable length for TTS
        clean_text = text[:800].strip()
        if not clean_text:
            clean_text = "Here is your response."

        unique_id = uuid.uuid4().hex[:8]
        filename = f"speech_{unique_id}.mp3"
        output_path = settings.GENERATED_DIR / filename

        try:
            tts = gTTS(text=clean_text, lang=lang, slow=False)
            tts.save(str(output_path))
            logger.info(f"Generated TTS audio file: {output_path}")
            return filename, str(output_path)
        except Exception as e:
            logger.warning(f"gTTS failed ({e}). Creating blank audio stub.")
            # Create an empty file so request doesn't fail
            output_path.touch()
            return filename, str(output_path)

    def transcribe_audio_bytes(self, audio_bytes: bytes, mime_type: str = "audio/webm") -> str:
        """
        Transcribes speech audio bytes directly using Gemini 3.1 Flash Lite multimodal model.
        Supports WebM, WAV, MP3, OGG, and AAC recorded from modern web browsers.
        """
        if not audio_bytes or len(audio_bytes) < 100:
            return ""

        try:
            from app.services.llm_service import get_genai_client
            from google.genai import types

            client = get_genai_client()
            if not client:
                logger.warning("GenAI client not available for audio transcription.")
                return ""

            # Standardize mime types if needed
            clean_mime = mime_type.split(";")[0].strip().lower()
            if not clean_mime:
                clean_mime = "audio/webm"

            part = types.Part.from_bytes(data=audio_bytes, mime_type=clean_mime)
            prompt = (
                "Transcribe this speech verbatim. "
                "Preserve the exact language spoken (English, Hindi, Hinglish, etc.). "
                "Return ONLY the plain transcript text with standard capitalization and punctuation. "
                "Do NOT include explanations, timestamps, notes, speaker tags, or quotation marks. "
                "If the audio is completely silent or only background noise, reply strictly with: [silence]"
            )

            response = client.models.generate_content(
                model=settings.LLM_MODEL,
                contents=[part, prompt]
            )

            text = (response.text or "").strip()
            if not text or text.lower() == "[silence]":
                return ""

            logger.info(f"Successfully transcribed audio bytes ({len(audio_bytes)} bytes) -> '{text[:60]}...'")
            return text
        except Exception as e:
            logger.error(f"Failed to transcribe audio bytes via Gemini: {e}")
            return ""

    def transcribe_audio(self, file_path: str) -> str:
        """
        Transcribes uploaded audio file using Gemini multimodal model.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        logger.info(f"Processing audio transcription for: {path.name}")
        ext = path.suffix.lower()
        mime_map = {
            ".wav": "audio/wav",
            ".mp3": "audio/mp3",
            ".webm": "audio/webm",
            ".ogg": "audio/ogg",
            ".m4a": "audio/m4a"
        }
        mime = mime_map.get(ext, "audio/webm")
        with open(path, "rb") as f:
            data = f.read()

        transcript = self.transcribe_audio_bytes(data, mime_type=mime)
        return transcript or f"Audio file {path.name} processed."

audio_service = AudioService()
