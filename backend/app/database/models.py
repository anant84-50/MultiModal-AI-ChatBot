import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")
    documents = relationship("Document", back_populates="conversation", cascade="all, delete-orphan")
    web_searches = relationship("WebSearch", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    input_type = Column(String(50), default="text")  # 'text', 'image', 'document', 'audio'
    output_type = Column(String(50), default="text")  # 'text', 'audio', 'document'
    metadata_json = Column(JSON, default=dict)  # stores sources, attachments, generated document links, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    conversation = relationship("Conversation", back_populates="messages")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # 'pdf', 'docx', 'txt', 'md', 'image', 'audio'
    file_path = Column(String(500), nullable=False)
    extracted_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)  # List of floats for vector search
    chunk_metadata = Column(JSON, default=dict)  # page number, section, chunk index

    # Relationship
    document = relationship("Document", back_populates="chunks")


class WebSearch(Base):
    __tablename__ = "web_searches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    query = Column(String(500), nullable=False)
    results = Column(JSON, default=list)  # list of {title, url, snippet}
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    conversation = relationship("Conversation", back_populates="web_searches")
