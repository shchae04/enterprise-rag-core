import uuid
from typing import Optional, Any
from sqlalchemy import String, Integer, Text, ForeignKey, Index, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
from pgvector.sqlalchemy import Vector
from sqlalchemy.types import TypeDecorator

from app.models.base import Base

class TSVector(TypeDecorator):
    impl = TSVECTOR

class Embedding(Base):
    __tablename__ = "embeddings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    # HNSW Index for fast approximate nearest neighbor search
    embedding: Mapped[Any] = mapped_column(Vector(768))
    
    # Full-Text Search Column (TSVector)
    # Note: Alembic might need explicit type definition or we use raw SQL for GIN index
    content_search: Mapped[Optional[Any]] = mapped_column(TSVECTOR)
    
    metadata_info: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationship
    document: Mapped["Document"] = relationship(back_populates="embeddings")

    # Define explicit indices
    __table_args__ = (
        # HNSW Index for Vector Search
        Index(
            'ix_embeddings_embedding_hnsw', 
            embedding, 
            postgresql_using='hnsw', 
            postgresql_with={'m': 16, 'ef_construction': 64},
            postgresql_ops={'embedding': 'vector_l2_ops'}
        ),
        # GIN Index for Full-Text Search
        Index(
            'ix_embeddings_content_search_gin',
            content_search,
            postgresql_using='gin'
        )
    )

    def __repr__(self):
        return f"<Embedding(doc_id={self.document_id}, chunk={self.chunk_index})>"