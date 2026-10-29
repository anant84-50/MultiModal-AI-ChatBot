from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=10000))

candidate_models = [
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-3.5-flash",
    "gemini-3.8-flash"
]

for m in candidate_models:
    try:
        print(f"Testing {m}...")
        resp = client.models.generate_content(
            model=m,
            contents="Say hello"
        )
        print(f"--> {m} SUCCESS:", resp.text.strip())
        break
    except Exception as e:
        print(f"--> {m} Error:", e)
