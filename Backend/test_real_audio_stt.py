from app.services.audio_service import audio_service
from app.services.llm_service import get_genai_client
from google.genai import types

# 1. Generate real speech using gTTS
fname, fpath = audio_service.text_to_speech("Testing voice recognition, how are you today?")
print("Generated audio:", fpath)

with open(fpath, "rb") as f:
    audio_data = f.read()

# 2. Call Gemini
client = get_genai_client()
part = types.Part.from_bytes(data=audio_data, mime_type="audio/mp3")

resp = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents=[
        part,
        "Transcribe this speech accurately verbatim. Return only the exact transcribed text, nothing else."
    ]
)
print("Transcript received:", resp.text.strip())
