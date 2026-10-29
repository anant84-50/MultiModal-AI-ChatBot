import io
import time
import requests
from PIL import Image, ImageDraw

BASE_URL = "http://127.0.0.1:8000"

def test_camera_flow():
    print("[1/4] Checking health endpoint...")
    r = requests.get(f"{BASE_URL}/api/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print(f"Health OK: {r.json()}")

    print("[2/4] Generating a simulated camera capture image...")
    # Create a 640x480 test image with a circle and text
    img = Image.new("RGB", (640, 480), color=(30, 41, 59))
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 100, 540, 380], outline=(99, 102, 241), width=4)
    draw.ellipse([270, 190, 370, 290], fill=(16, 185, 129))
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    print("[3/4] Uploading captured image to /api/documents/upload...")
    files = {
        'file': ('camera_capture_test.png', img_byte_arr, 'image/png')
    }
    r = requests.post(f"{BASE_URL}/api/documents/upload", files=files)
    assert r.status_code == 200, f"Upload failed: {r.status_code} - {r.text}"
    uploaded_doc = r.json()
    print(f"Uploaded Doc OK: id={uploaded_doc['id']}, filename={uploaded_doc['filename']}, file_url={uploaded_doc.get('file_url')}")

    print("[4/4] Sending multimodal chat query with uploaded camera image...")
    t0 = time.time()
    chat_payload = {
        "message": "What shapes and colors do you see in this captured image?",
        "attachment_ids": [uploaded_doc["id"]],
        "enable_web_search": False,
        "speak_response": False
    }
    r = requests.post(f"{BASE_URL}/api/chat", json=chat_payload, timeout=25)
    t1 = time.time()
    assert r.status_code == 200, f"Chat call failed: {r.status_code} - {r.text}"
    data = r.json()
    
    print(f"\nResponse received in {t1 - t0:.2f}s!")
    print(f"Assistant content: {data['assistant_message']['content'][:200]}...")
    print(f"User message metadata: {data['user_message'].get('metadata_json')}")
    print("\nALL CAMERA CAPTURE & VISION TESTS PASSED!")

if __name__ == "__main__":
    test_camera_flow()
