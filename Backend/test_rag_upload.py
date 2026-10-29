import io
from fastapi.testclient import TestClient
from PIL import Image
from app.main import app

client = TestClient(app)

print("--- 1. Testing Document Upload & RAG Ingestion ---")
doc_content = """# Company Handbook
Welcome to TechCorp.
Our primary values are Innovation, Empathy, and Integrity.
Working hours are flexible between 9 AM and 6 PM.
Annual vacation allowance is 25 days paid leave.
Health insurance covers medical, dental, and vision from day one."""

doc_file = io.BytesIO(doc_content.encode("utf-8"))
upload_res = client.post(
    "/api/documents/upload",
    files={"file": ("handbook.txt", doc_file, "text/plain")}
)
assert upload_res.status_code == 200, upload_res.text
doc_data = upload_res.json()
print("Document uploaded successfully:", doc_data["filename"], "Chunks indexed:", doc_data["chunk_count"])
assert doc_data["chunk_count"] > 0
doc_id = doc_data["id"]

print("--- 2. Testing Chat with RAG Grounding ---")
chat_res = client.post(
    "/api/chat",
    json={
        "message": "What is the annual vacation allowance?",
        "attachment_ids": [doc_id]
    }
)
assert chat_res.status_code == 200, chat_res.text
chat_data = chat_res.json()
print("RAG Assistant answer:", chat_data["assistant_message"]["content"])
print("Document sources returned:", len(chat_data["sources"]))
assert len(chat_data["sources"]) > 0
assert any(s["type"] == "document" for s in chat_data["sources"])

print("--- 3. Testing Multimodal Image Upload & Vision Q&A ---")
# Create a dummy test image (RGB red square)
img_byte_arr = io.BytesIO()
test_image = Image.new("RGB", (100, 100), color="red")
test_image.save(img_byte_arr, format="PNG")
img_byte_arr.seek(0)

img_upload_res = client.post(
    "/api/documents/upload",
    files={"file": ("red_square.png", img_byte_arr, "image/png")}
)
assert img_upload_res.status_code == 200, img_upload_res.text
img_data = img_upload_res.json()
img_id = img_data["id"]
print("Image uploaded successfully:", img_data["filename"], "Type:", img_data["file_type"])

img_chat_res = client.post(
    "/api/chat",
    json={
        "message": "Explain this diagram or image.",
        "input_type": "image",
        "attachment_ids": [img_id]
    }
)
assert img_chat_res.status_code == 200, img_chat_res.text
img_chat_data = img_chat_res.json()
print("Vision Assistant response:", img_chat_data["assistant_message"]["content"][:150], "...")

print("--- 4. Testing Document Edit Workflow via Chat ---")
edit_chat_res = client.post(
    "/api/chat",
    json={
        "message": "Edit this handbook and add a section about remote work policy.",
        "attachment_ids": [doc_id]
    }
)
assert edit_chat_res.status_code == 200, edit_chat_res.text
edit_chat_data = edit_chat_res.json()
print("Document Edit Response:", edit_chat_data["assistant_message"]["content"][:150], "...")
print("Generated Document download metadata:", edit_chat_data.get("generated_document"))
assert edit_chat_data.get("generated_document") is not None
assert "download_url" in edit_chat_data["generated_document"]

print("ALL RAG, MULTIMODAL VISION, AND DOCUMENT EDITING TESTS PASSED!")
