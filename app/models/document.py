import uuid
from typing import List, Optional
from sqlalchemy import String, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.models.base import Base, TimestampMixin

class FileStatus(str, enum.Enum):
    READY = "ready"
    PROCESSING = "processing"
    FAILED = "failed"
    COMPLETED = "completed"

class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String, index=True)
    file_type: Mapped[str] = mapped_column(String)
    file_size: Mapped[int] = mapped_column(Integer)
    category: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    status: Mapped[FileStatus] = mapped_column(SQLEnum(FileStatus), default=FileStatus.READY)
    
    # Relationship
    embeddings: Mapped[List["Embedding"]] = relationship(back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document(filename={self.filename}, status={self.status})>"
