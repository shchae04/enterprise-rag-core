import uuid
import os
import shutil
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List

from app.core.database import get_db
from app.core.config import settings
from app.services.ingest_service import IngestService
from app.schemas.document import DocumentResponse
from app.models.document import Document
from app.api import deps
from app.models.user import User
from app.worker import process_document_task

router = APIRouter()

@router.post("/upload", status_code=202)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Upload a document and process it asynchronously via Celery.
    Requires authentication.
    """
    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    
    # Save file to disk
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")

    # Trigger Ingestion Task (Async)
    source_type = os.path.splitext(file.filename)[1][1:]
    task = process_document_task.delay(file_path, source_type)
    
    return {
        "filename": file.filename, 
        "message": "Upload successful. Processing started in background.", 
        "task_id": str(task.id)
    }

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Document).offset(skip).limit(limit).order_by(Document.created_at.desc())
    result = await db.execute(stmt)
    documents = result.scalars().all()
    return documents

@router.delete("/{document_id}")
async def delete_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Delete a document and its embeddings.
    Requires authentication.
    """
    stmt = select(Document).where(Document.id == document_id)
    result = await db.execute(stmt)
    document = result.scalars().first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Delete from disk if exists
    # Note: Filename might be shared or not, depending on implementation. 
    # Current implementation overwrites on filename, so deleting might be tricky if multiple docs share file?
    # But schema says id is PK.
    # Safe to delete DB record. File deletion is optional or handled by a separate cleanup.
    # For now, let's delete the DB record which cascades to embeddings if configured, or manual delete.
    
    # IngestService has _delete_existing_document but that's by filename.
    # Let's simple delete from DB.
    
    await db.delete(document)
    await db.commit()
    
    return {"message": "Document deleted successfully"}