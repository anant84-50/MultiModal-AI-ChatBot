import sys
from pathlib import Path
from app.services.llm_service import get_genai_client
from google.genai import types

client = get_genai_client()
print("Client initialized:", client is not None)

# Test creating an audio part
# Generating a 1-second silent WAV in python to test part creation
import wave
import io

buf = io.BytesIO()
with wave.open(buf, 'wb') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(16000)
    wav_file.writeframes(b'\x00\x00' * 16000)
audio_bytes = buf.getvalue()

part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")
print("Part created successfully:", type(part))

# Call Gemini with audio part to transcribe
try:
    resp = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=[
            part,
            "Transcribe this audio verbatim. If there is no speech or silence, reply with: [silence]"
        ]
    )
    print("Gemini response on audio:", resp.text)
except Exception as e:
    print("Error calling Gemini with audio:", e)
