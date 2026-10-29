import sys
from app.services.llm_service import get_genai_client

client = get_genai_client()
print("Client initialized:", client is not None)

# Test 1: Check client.models.generate_images with imagen-3.0-generate-002
try:
    print("Testing generate_images with imagen-3.0-generate-002...")
    result = client.models.generate_images(
        model='imagen-3.0-generate-002',
        prompt='A beautiful golden retriever puppy playing in the grass',
        config=dict(
            number_of_images=1,
            output_mime_type='image/jpeg',
            aspect_ratio='1:1',
        )
    )
    print("Success! Number of images:", len(result.generated_images))
    for i, img in enumerate(result.generated_images):
        print(f"Image {i}: size {len(img.image.image_bytes)} bytes")
except Exception as e:
    print("Error with imagen-3.0-generate-002:", e)

# Test 2: List models or check what image models exist
try:
    print("\nChecking available models...")
    for m in client.models.list(config={"page_size": 50}):
        if "image" in m.name.lower() or "imagen" in m.name.lower():
            print("Found image model:", m.name, m.supported_actions if hasattr(m, 'supported_actions') else '')
except Exception as e:
    print("Error listing models:", e)
