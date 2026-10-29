import httpx

api_key = "AIzaSyDUUs-rJGtnCpD_PVpOAWBhzrBAmHRPEl4"

for m in ["gemini-3.1-flash-lite", "gemini-3.5-flash-lite"]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": "Answer in 1 sentence: What is photosynthesis?"}]}]
    }
    res = httpx.post(url, json=payload, timeout=10.0)
    if res.status_code == 200:
        data = res.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        print(f"SUCCESS {m}: {text.strip().encode('ascii', errors='replace').decode('ascii')}")
