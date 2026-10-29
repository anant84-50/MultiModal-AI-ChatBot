from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class MessageBase(BaseModel):
    role: str
    content: str
    input_type: Optional[str] = "text"
    output_type: Optional[str] = "text"
    metadata_json: Optional[Dict[str, Any]] = Field(default_factory=dict)

class MessageResponse(MessageBase):
    id: str
    conversation_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    title: Optional[str] = "New Conversation"

class ConversationResponse(ConversationBase):
    id: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True

class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    input_type: Optional[str] = "text"  # 'text', 'image', 'document', 'audio'
    attachment_ids: Optional[List[str]] = Field(default_factory=list)
    enable_web_search: Optional[bool] = None  # None = auto-detect, True/False = explicit
    speak_response: Optional[bool] = False

class SourceItem(BaseModel):
    type: str  # 'document' or 'web'
    title: str
    snippet: str
    url: Optional[str] = None
    page: Optional[int] = None

class ChatResponse(BaseModel):
    conversation_id: str
    user_message: MessageResponse
    assistant_message: MessageResponse
    sources: List[SourceItem] = []
    audio_url: Optional[str] = None
    generated_document: Optional[Dict[str, Any]] = None
    generated_image: Optional[Dict[str, Any]] = None
    is_emotional_support: bool = False
    is_crisis_alert: bool = False
