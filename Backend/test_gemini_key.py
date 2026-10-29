from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

try:
    print("Testing gemini-3.8-flash ...")
    resp = client.models.generate_content(
        model="gemini-3.8-flash",
        contents="Say 'Hello! Gemini 3.8 Flash is online.'"
    )
    print("SUCCESS:", resp.text.strip())
except Exception as e:
    print("Failed with gemini-3.8-flash:", e)
