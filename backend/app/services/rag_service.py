import logging
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from pypdf import PdfReader
from docx import Document as DocxDocument

from app.database.models import Document, DocumentChunk
from app.services.llm_service import llm_service

logger = logging.getLogger("rag_service")

class RAGService:
    def extract_text(self, file_path: str, file_type: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Extracts raw text and per-page/per-section text metadata from PDF, DOCX, TXT, or MD files.
        Returns (full_text, pages_or_sections).
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        extracted_text = ""
        sections = []

        try:
            if file_type == "pdf":
                reader = PdfReader(str(path))
                for idx, page in enumerate(reader.pages, 1):
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        extracted_text += f"\n--- Page {idx} ---\n" + page_text
                        sections.append({"page": idx, "text": page_text})
                        
            elif file_type in ["docx", "doc"]:
                doc = DocxDocument(str(path))
                current_p_texts = []
                for idx, paragraph in enumerate(doc.paragraphs, 1):
                    if paragraph.text.strip():
                        current_p_texts.append(paragraph.text)
                extracted_text = "\n\n".join(current_p_texts)
                sections.append({"page": 1, "text": extracted_text})

            elif file_type in ["text", "txt", "md"]:
                with open(str(path), "r", encoding="utf-8", errors="ignore") as f:
                    extracted_text = f.read()
                sections.append({"page": 1, "text": extracted_text})
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            raise e

        return extracted_text.strip(), sections

    def chunk_text(self, text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
        """
        Splits text into overlapping chunks using sliding window.
        """
        if not text:
            return []
            
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + chunk_size, text_len)
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end == text_len:
                break
            start += chunk_size - chunk_overlap

        return chunks

    def process_and_index_document(self, db: Session, doc_record: Document) -> int:
        """
        Extracts text, splits into chunks, generates vector embeddings, and stores
        them in the document_chunks table. Returns the number of chunks indexed.
        """
        full_text, sections = self.extract_text(doc_record.file_path, doc_record.file_type)
        doc_record.extracted_text = full_text
        db.commit()

        raw_chunks = self.chunk_text(full_text, chunk_size=500, chunk_overlap=60)
        chunks_created = 0

        for idx, chunk_str in enumerate(raw_chunks):
            embedding_vector = llm_service.generate_embedding(chunk_str)
            
            chunk_entry = DocumentChunk(
                document_id=doc_record.id,
                chunk_text=chunk_str,
                embedding=embedding_vector,
                chunk_metadata={"chunk_index": idx, "char_count": len(chunk_str)}
            )
            db.add(chunk_entry)
            chunks_created += 1

        db.commit()
        logger.info(f"Indexed {chunks_created} chunks for document {doc_record.filename}.")
        return chunks_created

    def similarity_search(
        self,
        db: Session,
        query: str,
        conversation_id: str = None,
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Calculates cosine similarity between query embedding and stored document chunks.
        Returns top-K relevant chunks with similarity score and document name.
        """
        query_embedding = np.array(llm_service.generate_embedding(query), dtype=np.float32)
        query_norm = np.linalg.norm(query_embedding)
        if query_norm == 0:
            query_norm = 1.0

        # Query chunks for this conversation (or all documents if conversation_id not specified)
        q = db.query(DocumentChunk).join(Document)
        if conversation_id:
            q = q.filter(Document.conversation_id == conversation_id)
        
        all_chunks = q.all()
        if not all_chunks:
            return []

        scored_chunks = []
        for chunk in all_chunks:
            if not chunk.embedding:
                continue
            chunk_vec = np.array(chunk.embedding, dtype=np.float32)
            chunk_norm = np.linalg.norm(chunk_vec)
            if chunk_norm == 0:
                continue
            
            # Cosine similarity
            similarity = float(np.dot(query_embedding, chunk_vec) / (query_norm * chunk_norm))
            scored_chunks.append({
                "score": similarity,
                "text": chunk.chunk_text,
                "document_id": chunk.document_id,
                "document_name": chunk.document.filename if chunk.document else "Document",
                "metadata": chunk.chunk_metadata
            })

        # Sort descending by similarity
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]

rag_service = RAGService()
