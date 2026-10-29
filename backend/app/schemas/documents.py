from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class DocumentBase(BaseModel):
    filename: str
    file_type: str

class DocumentResponse(DocumentBase):
    id: str
    conversation_id: Optional[str] = None
    file_path: str
    file_url: Optional[str] = None
    chunk_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentCreateRequest(BaseModel):
    title: str
    format: str = "docx"  # 'docx', 'pdf', 'txt', 'md'
    prompt_or_content: str
    conversation_id: Optional[str] = None

class DocumentEditRequest(BaseModel):
    document_id: str
    instructions: str
    conversation_id: Optional[str] = None

class DocumentActionResponse(BaseModel):
    success: bool
    message: str
    filename: str
    download_url: str
    file_type: str
