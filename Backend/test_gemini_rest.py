import httpx
import json

api_key = "AIzaSyDUUs-rJGtnCpD_PVpOAWBhzrBAmHRPEl4"

test_models = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-3.8-flash",
    "gemini-pro"
]

print("--- Testing Direct REST API with Google Gemini ---")
for m in test_models:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": "Answer this question in 1 line: What is the capital of France?"}]}]
    }
    try:
        res = httpx.post(url, json=payload, timeout=10.0)
        print(f"Model [{m}] -> Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            print(f"SUCCESS [{m}]: {text.strip()}")
            break
        else:
            print(f"Error [{m}]:", res.text[:200])
    except Exception as e:
        print(f"Exception [{m}]:", e)

# Also test v1 instead of v1beta
print("\n--- Testing v1 REST API ---")
for m in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash"]:
    url = f"https://generativelanguage.googleapis.com/v1/models/{m}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": "What is 2+2?"}]}]
    }
    try:
        res = httpx.post(url, json=payload, timeout=10.0)
        print(f"v1 [{m}] -> Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            print(f"SUCCESS v1 [{m}]: {text.strip()}")
            break
        else:
            print(f"Error v1 [{m}]:", res.text[:200])
    except Exception as e:
        print(f"Exception v1 [{m}]:", e)
