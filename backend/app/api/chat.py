import os
import uuid
import logging
from pathlib import Path
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import Conversation, Message, Document, WebSearch
from app.schemas.chat import (
    ChatRequest, ChatResponse, MessageResponse, ConversationResponse,
    ConversationSummary, SourceItem
)
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.services.search_service import should_search_web, perform_web_search
from app.services.emotion_service import check_emotional_context, EMOTIONAL_PROMPT_INSTRUCTION
from app.services.document_service import document_service
from app.services.audio_service import audio_service
from app.services.image_generation_service import image_generation_service

logger = logging.getLogger("chat_api")
router = APIRouter(prefix="", tags=["chat"])

@router.post("/chat/transcribe-audio")
async def transcribe_audio_endpoint(file: UploadFile = File(...)):
    """
    Direct endpoint for browser microphone audio transcription.
    Accepts audio recordings (WebM/WAV/MP3/OGG) and returns transcribed text via Gemini.
    """
    try:
        content = await file.read()
        mime = file.content_type or "audio/webm"
        transcript = audio_service.transcribe_audio_bytes(content, mime_type=mime)
        return {
            "success": True,
            "transcript": transcript,
            "filename": file.filename
        }
    except Exception as e:
        logger.error(f"Error in transcribe_audio_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/generate-image")
def direct_generate_image(req: dict):
    """
    Direct image generation endpoint.
    Accepts {"prompt": "..."} and returns generated image metadata.
    """
    prompt = req.get("prompt", "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required.")
    try:
        return image_generation_service.generate_image(prompt)
    except Exception as e:
        logger.error(f"Error in direct_generate_image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations", response_model=List[ConversationSummary])
def list_conversations(db: Session = Depends(get_db)):
    """Lists all conversations ordered by recent activity."""
    convos = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
    results = []
    for c in convos:
        count = db.query(Message).filter(Message.conversation_id == c.id).count()
        results.append(
            ConversationSummary(
                id=c.id,
                title=c.title or "New Conversation",
                created_at=c.created_at,
                updated_at=c.updated_at,
                message_count=count
            )
        )
    return results

@router.get("/conversations/{convo_id}", response_model=ConversationResponse)
def get_conversation(convo_id: str, db: Session = Depends(get_db)):
    """Retrieves full conversation with ordered message history."""
    convo = db.query(Conversation).filter(Conversation.id == convo_id).first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return convo

@router.delete("/conversations")
def clear_all_conversations(db: Session = Depends(get_db)):
    """Deletes all conversations and clears chat history."""
    db.query(Message).delete()
    db.query(Document).delete()
    db.query(WebSearch).delete()
    db.query(Conversation).delete()
    db.commit()
    return {"success": True, "message": "All conversations cleared."}

@router.delete("/conversations/{convo_id}")
def delete_conversation(convo_id: str, db: Session = Depends(get_db)):
    """Deletes a conversation and its cascaded messages and documents."""
    convo = db.query(Conversation).filter(Conversation.id == convo_id).first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    db.delete(convo)
    db.commit()
    return {"success": True, "message": "Conversation deleted."}

@router.post("/chat", response_model=ChatResponse)
def handle_chat_message(req: ChatRequest, db: Session = Depends(get_db)):
    """
    Core multimodal conversational endpoint orchestrating:
    - Multimodal input (text, images, documents, audio)
    - Conversation memory
    - RAG document context retrieval
    - Web search intent & execution
    - Emotional assistance & Crisis safety
    - Document creation/editing workflows
    - Optional audio TTS output
    """
    user_query = req.message.strip()
    if not user_query:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # 1. Manage Conversation instance
    if req.conversation_id:
        conversation = db.query(Conversation).filter(Conversation.id == req.conversation_id).first()
        if not conversation:
            conversation = Conversation(id=req.conversation_id, title=user_query[:40])
            db.add(conversation)
            db.commit()
    else:
        conversation = Conversation(title=user_query[:40])
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # 2. Resolve Attachments
    image_paths = []
    attached_documents = []
    docs = []
    if req.attachment_ids:
        docs = db.query(Document).filter(Document.id.in_(req.attachment_ids)).all()
        for doc in docs:
            # Associate document with this conversation
            doc.conversation_id = conversation.id
            if doc.file_type == "image":
                image_paths.append(doc.file_path)
            else:
                attached_documents.append(doc)
        db.commit()

    # 3. Emotional & Crisis Safety Guardrails
    is_emotional, is_crisis, crisis_response = check_emotional_context(user_query)

    sources: List[SourceItem] = []
    web_results = []
    rag_chunks = []
    generated_doc_meta = None
    generated_img_meta = None
    assistant_content = ""

    if is_crisis:
        # Immediate empathetic safety intervention
        assistant_content = crisis_response
    elif image_generation_service.is_image_request(user_query) and not attached_documents:
        # Image Generation Request
        try:
            img_data = image_generation_service.generate_image(user_query)
            generated_img_meta = img_data
            assistant_content = (
                f"I've generated your image based on **'{user_query}'**:\n\n"
                f"![{img_data['prompt']}]({img_data['file_url']})\n\n"
                f"**Prompt:** *{img_data['prompt']}*"
            )
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            assistant_content = f"I tried to generate an image for your request, but the service was temporarily unavailable: {str(e)}. Please try again."
    else:
        # 4. Check for Document Editing Request
        editing_keywords = ["edit", "rewrite", "modify", "update my resume", "change my objective", "add to my skills", "correct grammar"]
        is_edit_request = any(kw in user_query.lower() for kw in editing_keywords)

        if is_edit_request and attached_documents:
            target_doc = attached_documents[0]
            try:
                new_fn, new_fp, summary = document_service.edit_document(
                    original_path=target_doc.file_path,
                    file_type=target_doc.file_type,
                    instructions=user_query
                )
                generated_doc_meta = {
                    "filename": new_fn,
                    "download_url": f"/api/documents/download/{new_fn}",
                    "summary": summary
                }
                assistant_content = (
                    f"I have reviewed your document **{target_doc.filename}** and processed your requested modifications:\n\n"
                    f"**Changes applied:**\n- {summary}\n\n"
                    f"Your original file remains untouched. You can download the newly updated file using the card below."
                )
            except Exception as e:
                assistant_content = f"I encountered an issue editing the document: {str(e)}"

        # 5. RAG Retrieval if not editing (Only run if documents exist in this conversation)
        if not assistant_content:
            has_documents = db.query(Document).filter(
                (Document.conversation_id == conversation.id) | (Document.id.in_(req.attachment_ids or []))
            ).count() > 0

            if has_documents:
                rag_chunks = rag_service.similarity_search(
                    db=db,
                    query=user_query,
                    conversation_id=conversation.id,
                    top_k=4
                )
                for chunk in rag_chunks:
                    sources.append(
                        SourceItem(
                            type="document",
                            title=chunk["document_name"],
                            snippet=chunk["text"][:300],
                            page=chunk["metadata"].get("page")
                        )
                    )

            # 6. Web Search Determination
            needs_search = req.enable_web_search if req.enable_web_search is not None else should_search_web(user_query)
            if needs_search:
                web_results = perform_web_search(user_query, max_results=3)
                for item in web_results:
                    sources.append(
                        SourceItem(
                            type="web",
                            title=item["title"],
                            snippet=item["snippet"],
                            url=item["url"]
                        )
                    )

            # 7. Fetch Past Conversation Memory
            past_messages = db.query(Message).filter(
                Message.conversation_id == conversation.id
            ).order_by(Message.created_at.asc()).all()[-10:]

            history_for_llm = []
            for pm in past_messages:
                history_for_llm.append({"role": pm.role, "content": pm.content})
            history_for_llm.append({"role": "user", "content": user_query})

            # System prompt configuration
            system_prompt = "You are a versatile, polite, and helpful Multimodal AI assistant."
            if is_emotional:
                system_prompt += "\n" + EMOTIONAL_PROMPT_INSTRUCTION

            # 8. Generate LLM Response
            assistant_content = llm_service.generate_chat_response(
                messages=history_for_llm,
                system_instruction=system_prompt,
                context_chunks=rag_chunks,
                web_search_results=web_results,
                image_paths=image_paths
            )

    # 9. Audio TTS Generation (if requested)
    audio_url = None
    if req.speak_response:
        try:
            fn, _ = audio_service.text_to_speech(assistant_content[:500])
            audio_url = f"/api/audio/stream/{fn}"
        except Exception:
            pass

    # 10. Persist Messages in PostgreSQL
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=user_query,
        input_type=req.input_type or "text",
        metadata_json={
            "attachments": req.attachment_ids or [],
            "attached_files": [
                {
                    "id": d.id,
                    "filename": d.filename,
                    "file_type": d.file_type,
                    "file_url": f"/uploads/{os.path.basename(d.file_path)}"
                }
                for d in docs
            ]
        }
    )
    db.add(user_msg)

    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=assistant_content,
        output_type="image" if generated_img_meta else ("document" if generated_doc_meta else ("audio" if audio_url else "text")),
        metadata_json={
            "sources": [s.model_dump() for s in sources],
            "audio_url": audio_url,
            "generated_document": generated_doc_meta,
            "generated_image": generated_img_meta,
            "is_emotional_support": is_emotional,
            "is_crisis_alert": is_crisis
        }
    )
    db.add(assistant_msg)
    
    # Touch conversation updated_at
    conversation.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user_msg)
    db.refresh(assistant_msg)

    return ChatResponse(
        conversation_id=conversation.id,
        user_message=MessageResponse.model_validate(user_msg),
        assistant_message=MessageResponse.model_validate(assistant_msg),
        sources=sources,
        audio_url=audio_url,
        generated_document=generated_doc_meta,
        generated_image=generated_img_meta,
        is_emotional_support=is_emotional,
        is_crisis_alert=is_crisis
    )
