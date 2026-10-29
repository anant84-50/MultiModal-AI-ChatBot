import os
import time
import httpx
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
UPLOADS_DIR = Path("uploads")

def test_suite():
    print("=== STARTING FULL MULTIMODAL IMAGE GENERATION SUITE ===", flush=True)
    
    with httpx.Client(base_url=BASE_URL, timeout=90.0) as client:
        # Check health first
        h = client.get("/api/health")
        assert h.status_code == 200, f"Backend not healthy: {h.text}"
        print("Backend health verified: 200 OK", flush=True)

        # TEST 1: Direct Image Generation Endpoint (English prompt)
        print("\n--- TEST 1: Direct POST /api/chat/generate-image (Cyberpunk Car) ---", flush=True)
        prompt1 = "futuristic electric sports car in neon cyberpunk city"
        t0 = time.time()
        r1 = client.post("/api/chat/generate-image", json={"prompt": prompt1})
        elapsed1 = time.time() - t0
        print(f"Status code: {r1.status_code} (took {elapsed1:.1f}s)", flush=True)
        assert r1.status_code == 200, f"Expected 200, got {r1.status_code}: {r1.text}"
        data1 = r1.json()
        print("Response payload:", data1, flush=True)
        assert data1.get("success") is True, "Success should be True"
        fname1 = data1.get("filename")
        assert (UPLOADS_DIR / fname1).exists(), f"File {fname1} must exist in uploads"
        file_size1 = (UPLOADS_DIR / fname1).stat().st_size
        print(f"File {fname1} exists! Size: {file_size1} bytes", flush=True)
        assert file_size1 > 5000, "Image must be larger than 5KB"

        # Verify static file serving via HTTP
        img_http = client.get(data1["file_url"])
        assert img_http.status_code == 200, f"Image should be accessible over HTTP: {img_http.status_code}"
        print(f"Image HTTP 200 verified ({len(img_http.content)} bytes served)", flush=True)

        print("\nWaiting 46 seconds for rate limit window to refresh...", flush=True)
        for i in range(46, 0, -10):
            print(f"  {i}s remaining...", flush=True)
            time.sleep(10)
        time.sleep(6)

        # TEST 2: Chat Conversational Image Request in Hindi / Hinglish
        print("\n--- TEST 2: Conversational Chat in Hindi: 'ek pyare golden puppy ki photo banao' ---", flush=True)
        req2 = {
            "message": "ek pyare golden puppy ki photo banao grass me",
            "attachment_ids": []
        }
        t0 = time.time()
        r2 = client.post("/api/chat", json=req2)
        elapsed2 = time.time() - t0
        print(f"Chat status: {r2.status_code} (took {elapsed2:.1f}s)", flush=True)
        assert r2.status_code == 200, f"Expected 200, got {r2.status_code}: {r2.text}"
        chat_data2 = r2.json()
        print("Assistant reply preview:\n", chat_data2["assistant_message"]["content"][:220], flush=True)
        gen_img2 = chat_data2.get("generated_image")
        print("Generated image meta:", gen_img2, flush=True)
        assert gen_img2 is not None, "generated_image must be present in ChatResponse"
        assert gen_img2.get("success") is True, "Image generation should be marked success"
        fname2 = gen_img2.get("filename")
        assert (UPLOADS_DIR / fname2).exists(), f"File {fname2} must exist"
        file_size2 = (UPLOADS_DIR / fname2).stat().st_size
        print(f"File {fname2} exists! Size: {file_size2} bytes", flush=True)
        assert file_size2 > 5000, "Image must be larger than 5KB"

        # Verify second image HTTP serving
        img2_http = client.get(gen_img2["file_url"])
        assert img2_http.status_code == 200, f"Image 2 HTTP failed: {img2_http.status_code}"
        print(f"Image 2 HTTP 200 verified ({len(img2_http.content)} bytes served)", flush=True)

    print("\n=======================================================", flush=True)
    print("=== ALL MULTIMODAL IMAGE GENERATION TESTS PASSED! ===", flush=True)
    print("=======================================================", flush=True)

if __name__ == "__main__":
    test_suite()
