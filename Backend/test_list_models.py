from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

try:
    print("Listing available models for this key:")
    for m in client.models.list():
        # print first 15 models
        name = getattr(m, "name", str(m))
        print("Model:", name)
except Exception as e:
    print("Error listing models:", e)
