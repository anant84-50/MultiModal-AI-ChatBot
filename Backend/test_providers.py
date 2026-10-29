import httpx
from urllib.parse import quote

prompt = quote("a cute golden retriever puppy sitting in grass")

# 1. Pollinations with model=turbo
print("Testing pollinations model=turbo...")
try:
    r = httpx.get(f"https://image.pollinations.ai/prompt/{prompt}?model=turbo&nologo=true", timeout=25.0)
    print("Turbo status:", r.status_code, "len:", len(r.content), "type:", r.headers.get("content-type"))
except Exception as e:
    print("Turbo error:", e)

# 2. Pollinations with model=flux
print("\nTesting pollinations model=flux...")
try:
    r = httpx.get(f"https://image.pollinations.ai/prompt/{prompt}?model=flux&nologo=true", timeout=25.0)
    print("Flux status:", r.status_code, "len:", len(r.content), "type:", r.headers.get("content-type"))
except Exception as e:
    print("Flux error:", e)

# 3. Pollinations default retry
print("\nTesting pollinations default...")
try:
    r = httpx.get(f"https://image.pollinations.ai/prompt/{prompt}?nologo=true", timeout=25.0)
    print("Default status:", r.status_code, "len:", len(r.content), "type:", r.headers.get("content-type"))
except Exception as e:
    print("Default error:", e)

# 4. Hugging Face public serverless models (e.g. black-forest-labs/FLUX.1-schnell or stabilityai/stable-diffusion-xl-base-1.0)
print("\nTesting HuggingFace public router...")
try:
    hf_url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    r = httpx.post(hf_url, json={"inputs": "a cute golden retriever puppy"}, timeout=20.0)
    print("HF status:", r.status_code, "len:", len(r.content))
except Exception as e:
    print("HF error:", e)
