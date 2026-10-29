from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

try:
    resp = client.models.embed_content(
        model="gemini-embedding-001",
        contents="Hello world this is a test"
    )
    print("Embedding type:", type(resp))
    # Check attributes
    values = None
    if hasattr(resp, "embedding") and resp.embedding:
        values = resp.embedding.values
    elif hasattr(resp, "embeddings") and resp.embeddings:
        values = resp.embeddings[0].values
    print("Extracted values length:", len(values) if values else "None")
    print("SUCCESS embedding generation!")
except Exception as e:
    print("Embedding error:", e)
