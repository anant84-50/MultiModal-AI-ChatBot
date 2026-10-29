from app.main import app
from app.database.session import init_db, SessionLocal
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.services.search_service import perform_web_search, should_search_web
from app.services.emotion_service import check_emotional_context
from app.services.document_service import document_service
from app.services.audio_service import audio_service

print("Testing database initialization...")
init_db()

print("Testing LLM fallback...")
resp = llm_service.generate_chat_response([{"role": "user", "content": "Hello!"}])
print("LLM Response:", resp[:50], "...")

print("Testing Web Search Intent...")
assert should_search_web("latest AI news") == True
assert should_search_web("what is python") == False
print("Search intent tests passed.")

print("Testing Emotional & Crisis Guardrails...")
is_emo, is_cris, reply = check_emotional_context("I feel very sad and lonely today")
assert is_emo == True
assert is_cris == False

is_emo2, is_cris2, reply2 = check_emotional_context("I want to commit suicide")
assert is_cris2 == True
assert "988" in reply2
print("Emotional & crisis tests passed.")

print("Testing Document Creation...")
fn, fp = document_service.create_document("Test Proposal", "docx", "This is a test document.\n- Bullet point 1\n- Bullet point 2")
print(f"Created docx: {fn}")

print("Testing Document Editing...")
fn_edit, fp_edit, summary = document_service.edit_document(fp, "docx", "Add a section on Python skills")
print(f"Edited docx: {fn_edit}")

print("Testing Audio TTS...")
afn, afp = audio_service.text_to_speech("Welcome to the Multimodal AI Chatbot.")
print(f"Generated TTS: {afn}")

print("ALL BACKEND SERVICES TESTED AND FUNCTIONAL!")
