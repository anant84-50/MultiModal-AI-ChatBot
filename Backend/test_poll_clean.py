import httpx

# Test parameter for nologo in pollinations
url = "https://image.pollinations.ai/prompt/cyberpunk%20golden%20sports%20car%20neon%20city?width=1024&height=1024&nologo=true&seed=42"
r = httpx.get(url, timeout=30.0, follow_redirects=True)
print("Response status:", r.status_code, "Length:", len(r.content))

with open("test_clean.jpg", "wb") as f:
    f.write(r.content)
print("Saved test_clean.jpg")
