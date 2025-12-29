from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID

class DocumentBase(BaseModel):
    filename: str
    category: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    status: Optional[str] = None
    category: Optional[str] = None

class DocumentResponse(DocumentBase):
    id: UUID
    file_type: str
    file_size: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
