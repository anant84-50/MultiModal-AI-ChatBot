import time
import httpx
from urllib.parse import quote

last_call_time = 0

def generate_image_paced(prompt: str, seed: int = 101) -> int:
    global last_call_time
    now = time.time()
    elapsed = now - last_call_time
    min_interval = 46.0

    if last_call_time > 0 and elapsed < min_interval:
        wait_seconds = min_interval - elapsed
        print(f"Pacing: waiting {wait_seconds:.1f}s for free rate limit window...")
        time.sleep(wait_seconds)

    encoded = quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true&seed={seed}"
    print(f"Calling Pollinations for '{prompt}'...")
    
    with httpx.Client(timeout=45.0, follow_redirects=True) as client:
        r = client.get(url)
        last_call_time = time.time()
        print(f"Result: {r.status_code}, Bytes: {len(r.content)}")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text[:200]}"
        return len(r.content)

print("--- Calling 1st Image ---")
s1 = generate_image_paced("A majestic golden eagle soaring above snowy mountains", seed=1)
print("1st Image Success! Size:", s1)

print("\n--- Calling 2nd Image Immediately Back-to-Back ---")
s2 = generate_image_paced("A futuristic electric supercar speeding in neon cyberpunk city", seed=2)
print("2nd Image Success! Size:", s2)
