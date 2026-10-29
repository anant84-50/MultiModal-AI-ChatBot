import httpx
from urllib.parse import quote

p = quote("a golden lion")

# Test 1: pollinations.ai/p/
print("Test 1: pollinations /p/")
try:
    r = httpx.get(f"https://pollinations.ai/p/{p}?width=512&height=512", timeout=10.0, follow_redirects=True)
    print("Status:", r.status_code, "type:", r.headers.get("content-type"), "len:", len(r.content))
except Exception as e:
    print("Error:", e)

# Test 2: pollinations gen endpoints
print("\nTest 2: pollinations enter / api")
try:
    r = httpx.get(f"https://image.pollinations.ai/prompt/{p}", timeout=10.0, follow_redirects=True)
    print("Status:", r.status_code, "type:", r.headers.get("content-type"), "len:", len(r.content))
except Exception as e:
    print("Error:", e)

# Test 3: DuckDuckGo image search / Unsplash for fallback
print("\nTest 3: DuckDuckGo images / Unsplash")
try:
    r = httpx.get("https://unsplash.com/napi/search/photos?query=golden+lion&per_page=1", timeout=10.0)
    print("Unsplash status:", r.status_code)
    if r.status_code == 200:
        data = r.json()
        print("Unsplash results:", len(data.get("results", [])))
        if data.get("results"):
            print("Unsplash URL:", data["results"][0]["urls"]["regular"])
except Exception as e:
    print("Unsplash error:", e)
