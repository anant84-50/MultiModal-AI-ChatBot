import httpx

api_key = "AIzaSyDUUs-rJGtnCpD_PVpOAWBhzrBAmHRPEl4"

test_models = [
    "gemini-2.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemma-4-26b-a4b-it",
    "gemma-4-31b-it"
]

print("--- Testing specific active models ---")
for m in test_models:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": "Hello, answer in 5 words: what is Python?"}]}]
    }
    try:
        res = httpx.post(url, json=payload, timeout=12.0)
        print(f"Model [{m}] -> Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            print(f"🎉 SUCCESS [{m}]: {text.strip()}\n")
            break
        else:
            print(f"Error [{m}]:", res.text[:200], "\n")
    except Exception as e:
        print(f"Exception [{m}]:", e, "\n")
