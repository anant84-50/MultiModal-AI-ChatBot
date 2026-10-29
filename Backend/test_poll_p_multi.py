import httpx
from urllib.parse import quote
import time

prompts = [
    "a majestic eagle in the sky",
    "a cyber sports car in neon lights",
    "a cute golden retriever puppy"
]

for i, p in enumerate(prompts):
    encoded = quote(p)
    url = f"https://pollinations.ai/p/{encoded}?width=1024&height=1024&seed={i*100}"
    print(f"\nRequesting {i+1}: '{p}'...")
    r = httpx.get(url, timeout=30.0, follow_redirects=True)
    print(f"Status: {r.status_code}, type: {r.headers.get('content-type')}, bytes: {len(r.content)}")
    if r.status_code == 200:
        with open(f"test_p_{i}.jpg", "wb") as f:
            f.write(r.content)
        print(f"Saved test_p_{i}.jpg successfully!")
    time.sleep(2)
