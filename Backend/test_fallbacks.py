import httpx

# Test free fallback providers
print("Testing airforce imagine...")
try:
    r = httpx.get("https://api.airforce/imagine?prompt=golden%20retriever%20puppy", timeout=15.0)
    print("Airforce status:", r.status_code, "type:", r.headers.get("content-type"), "len:", len(r.content))
except Exception as e:
    print("Airforce error:", e)

print("Testing Unsplash Source / Lexica...")
try:
    r = httpx.get("https://lexica.art/api/v1/search?q=golden%20retriever%20puppy", timeout=10.0)
    data = r.json()
    images = data.get("images", [])
    print("Lexica search results count:", len(images))
    if images:
        print("First Lexica image:", images[0].get("src"))
except Exception as e:
    print("Lexica error:", e)
