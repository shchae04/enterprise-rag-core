from pydantic import BaseModel
from typing import List, Optional, Any
from uuid import UUID

class ChatRequest(BaseModel):
    query: str
    collection_name: Optional[str] = None # For specific category filtering
    top_k: int = 4

class SourceDocument(BaseModel):
    document_id: UUID
    filename: str
    content: str
    score: float
    page_number: Optional[int] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceDocument] = []
