import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import Document, Conversation
from app.schemas.documents import (
    DocumentResponse, DocumentCreateRequest, DocumentEditRequest, DocumentActionResponse
)
from app.utils.file_security import sanitize_filename, validate_uploaded_file, detect_file_category
from app.services.rag_service import rag_service
from app.services.document_service import document_service
from app.config import settings

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload", response_model=DocumentResponse)
async def upload_file(
    file: UploadFile = File(...),
    conversation_id: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Uploads a file (image, PDF, DOCX, text, or audio), validates its type and size,
    saves it to disk, and runs RAG indexing if it is a text/document format.
    """
    ext = validate_uploaded_file(file)
    safe_name = sanitize_filename(file.filename)
    category = detect_file_category(ext)

    # If conversation_id is provided, verify it exists
    if conversation_id:
        convo = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not convo:
            # Create the conversation automatically if it doesn't exist
            convo = Conversation(id=conversation_id, title=f"Chat about {safe_name}")
            db.add(convo)
            db.commit()

    # Generate unique stored filename to prevent name collisions
    unique_filename = f"{uuid.uuid4().hex[:8]}_{safe_name}"
    file_path = settings.UPLOAD_DIR / unique_filename

    # Save to disk
    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB."
        )

    with open(str(file_path), "wb") as f:
        f.write(contents)

    # Save database record
    doc_record = Document(
        conversation_id=conversation_id,
        filename=safe_name,
        file_type=category,
        file_path=str(file_path)
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)

    # Run RAG ingestion for document formats (pdf, docx, txt, md)
    chunk_count = 0
    if category in ["pdf", "docx", "text"]:
        try:
            chunk_count = rag_service.process_and_index_document(db, doc_record)
        except Exception as e:
            # File is still saved even if text extraction encounters non-critical warnings
            pass

    return DocumentResponse(
        id=doc_record.id,
        conversation_id=doc_record.conversation_id,
        filename=doc_record.filename,
        file_type=doc_record.file_type,
        file_path=str(doc_record.file_path),
        file_url=f"/uploads/{unique_filename}",
        chunk_count=chunk_count,
        created_at=doc_record.created_at
    )

@router.post("/create", response_model=DocumentActionResponse)
def create_document(req: DocumentCreateRequest):
    """Generates a downloadable document in DOCX, PDF, TXT, or MD format."""
    try:
        filename, filepath = document_service.create_document(
            title=req.title,
            format_type=req.format,
            content=req.prompt_or_content
        )
        return DocumentActionResponse(
            success=True,
            message="Document generated successfully.",
            filename=filename,
            download_url=f"/api/documents/download/{filename}",
            file_type=req.format
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create document: {str(e)}")

@router.post("/edit", response_model=DocumentActionResponse)
def edit_document(req: DocumentEditRequest, db: Session = Depends(get_db)):
    """Edits an existing document based on instructions without overwriting the original file."""
    doc = db.query(Document).filter(Document.id == req.document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Original document not found.")

    try:
        new_filename, new_filepath, summary = document_service.edit_document(
            original_path=doc.file_path,
            file_type=doc.file_type,
            instructions=req.instructions
        )
        return DocumentActionResponse(
            success=True,
            message=summary,
            filename=new_filename,
            download_url=f"/api/documents/download/{new_filename}",
            file_type=doc.file_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to edit document: {str(e)}")

@router.get("/download/{filename}")
def download_document(filename: str):
    """Securely downloads a generated or uploaded document."""
    safe_name = sanitize_filename(filename)
    
    # Check in generated folder first
    gen_path = settings.GENERATED_DIR / safe_name
    if gen_path.exists():
        return FileResponse(
            path=str(gen_path),
            filename=safe_name,
            media_type="application/octet-stream"
        )
    
    # Check in upload folder
    upload_path = settings.UPLOAD_DIR / safe_name
    if upload_path.exists():
        return FileResponse(
            path=str(upload_path),
            filename=safe_name,
            media_type="application/octet-stream"
        )

    raise HTTPException(status_code=404, detail="File not found.")
