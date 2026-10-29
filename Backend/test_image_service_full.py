import os
import uuid
import httpx
from pathlib import Path
from urllib.parse import quote
from app.services.llm_service import get_genai_client
from app.config import settings

def enhance_image_prompt(user_query: str) -> str:
    """Uses Gemini to translate and expand the user's prompt into an artistic image generation prompt."""
    try:
        client = get_genai_client()
        if not client:
            return user_query
        resp = client.models.generate_content(
            model=settings.LLM_MODEL,
            contents=(
                f"You are an AI image prompt expert. The user wants an image: '{user_query}'.\n"
                "Convert this into a detailed, photorealistic, English image prompt (under 40 words) describing lighting, details, atmosphere, and quality.\n"
                "Return ONLY the prompt text, nothing else."
            )
        )
        enhanced = (resp.text or "").strip().strip('"').strip("'")
        return enhanced or user_query
    except Exception as e:
        print("Prompt enhancement fallback:", e)
        return user_query

def generate_image_file(prompt: str) -> str:
    """Generates an image via high-resolution Flux/SDXL engine, saves locally, returns filepath."""
    encoded_prompt = quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={uuid.uuid4().int % 100000}"
    print(f"Requesting image from: {url[:80]}...")
    
    with httpx.Client(timeout=45.0, follow_redirects=True) as http_client:
        r = http_client.get(url)
        if r.status_code != 200 or len(r.content) < 5000:
            raise RuntimeError(f"Image generation failed with status {r.status_code}")
        
        filename = f"gen_{uuid.uuid4().hex[:8]}.jpg"
        target_path = settings.UPLOAD_DIR / filename
        with open(target_path, "wb") as f:
            f.write(r.content)
            
        print(f"Successfully generated and saved image: {filename} ({len(r.content)} bytes)")
        return filename

# Test running end-to-end
test_query = "ek sher ki photo banao cinematic lighting me"
print("User Query:", test_query)
enhanced = enhance_image_prompt(test_query)
print("Enhanced Prompt:", enhanced)
fname = generate_image_file(enhanced)
print("Result File:", fname)
