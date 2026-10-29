from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

for m in ["gemini-flash-latest", "gemini-3.5-flash", "gemini-2.5-flash-lite"]:
    try:
        print(f"Testing model: {m} ...")
        resp = client.models.generate_content(
            model=m,
            contents="Say 'Hello! API is working.'"
        )
        print(f"SUCCESS with {m}:", resp.text.strip())
        break
    except Exception as e:
        print(f"Failed with {m}: {e}")
