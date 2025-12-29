from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time
import uuid

from app.core.database import get_db
from app.core.config import settings
from app.schemas.chat import ChatRequest, ChatResponse, SourceDocument
from app.services.chat_service import ChatService

router = APIRouter()

# --- Internal API ---

@router.post("/query", response_model=ChatResponse)
async def chat_query(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    # Restore default top_k to 4
    k = request.top_k if request.top_k > 0 else 4
    
    service = ChatService(db)
    answer, sources_data = await service.get_answer(request.query, k)
    
    # Convert dict sources to Pydantic models
    sources = []
    for s in sources_data:
        sources.append(SourceDocument(
            document_id=s['document_id'],
            filename=s['filename'],
            content=s['content'],
            score=s.get('score', 0.0)
        ))

    return ChatResponse(answer=answer, sources=sources)


# --- OpenAI Compatible API (For Open WebUI) ---

class OpenAIMessage(BaseModel):
    role: str
    content: str

class OpenAIRequest(BaseModel):
    model: str
    messages: List[OpenAIMessage]
    stream: bool = False

@router.post("/completions") # Full path: /api/v1/chat/completions
async def openai_chat_completion(
    request: OpenAIRequest,
    db: AsyncSession = Depends(get_db)
):
    # 1. Extract latest user query
    last_user_message = next((m.content for m in reversed(request.messages) if m.role == "user"), None)
    if not last_user_message:
        raise HTTPException(status_code=400, detail="No user message found")

    # 2. Call internal service
    service = ChatService(db)
    answer, sources = await service.get_answer(last_user_message, k=4)

    # 3. Format response as OpenAI format
    return {
        "id": f"chatcmpl-{uuid.uuid4()}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": answer
            },
            "finish_reason": "stop"
        }],
        "usage": { # Dummy usage
            "prompt_tokens": len(last_user_message),
            "completion_tokens": len(answer),
            "total_tokens": len(last_user_message) + len(answer)
        }
    }

@router.get("/models") # Full path: /api/v1/chat/models (Note: Open WebUI usually looks for /v1/models)
async def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "rag-model", # The single custom RAG model
                "object": "model",
                "created": int(time.time()),
                "owned_by": "organization",
            }
        ]
    }
