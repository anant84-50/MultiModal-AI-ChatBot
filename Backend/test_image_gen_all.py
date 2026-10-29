import httpx
from app.services.llm_service import get_genai_client

client = get_genai_client()

# 1. Test generate_content with gemini-2.5-flash-image
print("Testing gemini-2.5-flash-image generate_content...")
try:
    resp = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents="Generate a photo of a cute golden retriever puppy",
    )
    print("Response parts count:", len(resp.candidates[0].content.parts))
    for p in resp.candidates[0].content.parts:
        if hasattr(p, 'inline_data') and p.inline_data:
            print("Received inline image bytes! Mime:", p.inline_data.mime_type, "len:", len(p.inline_data.data))
        elif hasattr(p, 'text') and p.text:
            print("Received text:", p.text[:100])
except Exception as e:
    print("Error with gemini-2.5-flash-image:", e)

# 2. Test generate_content with imagen-3.0-generate-002
print("\nTesting imagen-3.0-generate-002 generate_content...")
try:
    resp = client.models.generate_content(
        model="imagen-3.0-generate-002",
        contents="A cute golden retriever puppy playing in green grass"
    )
    print("Imagen generate_content success! parts:", len(resp.candidates[0].content.parts))
    for p in resp.candidates[0].content.parts:
        if hasattr(p, 'inline_data') and p.inline_data:
            print("Received image bytes! len:", len(p.inline_data.data))
        elif hasattr(p, 'text') and p.text:
            print("Received text:", p.text[:100])
except Exception as e:
    print("Error with imagen-3.0-generate-002 generate_content:", e)

# 3. Test Pollinations / Flux direct image generation
print("\nTesting Pollinations / Flux image generation...")
try:
    url = "https://image.pollinations.ai/prompt/a%20cute%20golden%20retriever%20puppy%20in%20a%20golden%20sunlit%20garden?width=1024&height=1024&nologo=true"
    r = httpx.get(url, timeout=30.0, follow_redirects=True)
    print("Pollinations status:", r.status_code, "Content-Type:", r.headers.get("content-type"), "Bytes:", len(r.content))
except Exception as e:
    print("Error with Pollinations:", e)
