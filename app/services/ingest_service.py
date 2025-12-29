import os
import json
import asyncio
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, text
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.models.document import Document, FileStatus
from app.models.embedding import Embedding
from app.utils.parsers import parse_file, parse_web_content
from app.services.vector_service import VectorService
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import AppError

class IngestService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_document(self, file_path: str, source_type: str = "file") -> bool:
        """
        파일을 파싱하고, 임베딩을 생성하여 DB에 저장합니다.
        이미 존재하는 파일명일 경우 덮어씁니다 (기존 데이터 삭제).
        """
        
        filename = os.path.basename(file_path)
        logger.info(f"Starting ingestion for file: {filename}")
        
        try:
            # 1. Parse Content (Run in thread pool to avoid blocking event loop)
            if source_type == "web":
                # Network I/O is less blocking, but parsing HTML can be CPU bound
                content = await asyncio.to_thread(parse_web_content, file_path)
            else:
                # PDF/HWP parsing is heavily CPU bound
                content = await asyncio.to_thread(parse_file, file_path)

            if not content or len(content.strip()) < 10:
                logger.warning(f"Content empty or too short: {filename}")
                raise AppError(f"File content is empty or too short: {filename}")

            # Transaction Block
            async with self.db.begin_nested(): # Savepoint for partial rollback if needed, though we rely on main session
                # 2. Check Duplicate & Delete Existing
                await self._delete_existing_document(filename)

                # 3. Classify
                category = await VectorService.classify_content(filename, content)

                # 4. Create Document Record
                file_size = len(content.encode('utf-8'))
                doc = Document(
                    filename=filename,
                    file_type=source_type,
                    file_size=file_size,
                    category=category,
                    status=FileStatus.PROCESSING
                )
                self.db.add(doc)
                await self.db.flush() # Get ID
                
                # 5. Chunking
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=settings.CHUNK_SIZE,
                    chunk_overlap=settings.CHUNK_OVERLAP,
                    separators=["\n\n", "\n", ". ", " ", ""]
                )
                chunks = text_splitter.split_text(content)
                logger.info(f"Split {filename} into {len(chunks)} chunks")
                
                # 6. Embed & Save Chunks
                await self._process_chunks(doc, chunks, content)

                # 7. Update Full-Text Search Vector (TSVECTOR)
                # Note: We do this after inserting chunks. 
                # Ideally, we update each chunk's content_search column.
                # Since we are inside a transaction, we can execute a SQL update.
                await self.db.flush() # Ensure embeddings are in session
                await self._update_tsvectors(doc.id)

                # 8. Update Status
                doc.status = FileStatus.COMPLETED
                logger.info(f"Ingestion completed successfully for: {filename}")
            
            await self.db.commit()
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to ingest document {filename}: {str(e)}", exc_info=True)
            # Re-raise as AppError if it's not already one, or let global handler catch it
            if isinstance(e, AppError):
                raise e
            raise AppError(f"Document processing failed: {str(e)}")

    async def _delete_existing_document(self, filename: str):
        result = await self.db.execute(select(Document).where(Document.filename == filename))
        existing_doc = result.scalars().first()
        if existing_doc:
            logger.info(f"Removing existing document: {filename}")
            await self.db.delete(existing_doc)

    async def _process_chunks(self, doc: Document, chunks: List[str], full_content: str):
        base_metadata = {
            "document_id": str(doc.id),
            "filename": doc.filename,
            "category": doc.category,
        }

        BATCH_SIZE = 10
        total_chunks = len(chunks)

        for i in range(0, total_chunks, BATCH_SIZE):
            batch_chunks = chunks[i:i + BATCH_SIZE]
            tasks = []
            
            for chunk in batch_chunks:
                if len(chunk.strip()) < 10: 
                    # Placeholder to maintain index sync if needed, or just skip. 
                    # If skipping, we just won't have an embedding for this snippet.
                    tasks.append(asyncio.sleep(0)) 
                    continue
                tasks.append(VectorService.create_embedding_static(chunk))
            
            # Run batch in parallel
            embeddings_results = await asyncio.gather(*tasks)

            # Process results
            for j, embedding_vector in enumerate(embeddings_results):
                # Skip if it was a skipped chunk (asyncio.sleep result is None usually or 0, depending on sleep)
                if embedding_vector is None or isinstance(embedding_vector, int): 
                    continue
                    
                if not embedding_vector:
                    logger.warning(f"Empty embedding generated for chunk {i+j} of {doc.filename}")
                    continue

                chunk_idx = i + j
                chunk_content = batch_chunks[j]
                
                chunk_metadata = base_metadata.copy()
                chunk_metadata["chunk_index"] = chunk_idx

                embedding_entry = Embedding(
                    document_id=doc.id,
                    chunk_index=chunk_idx,
                    content=chunk_content,
                    embedding=embedding_vector,
                    metadata_info=chunk_metadata 
                )
                self.db.add(embedding_entry)

    async def _update_tsvectors(self, document_id):
        """
        Populate the content_search tsvector column for the inserted embeddings using PostgreSQL's to_tsvector function.
        We use the 'simple' configuration to support mixed languages (English/Korean) basically.
        For better Korean support, a specific configuration or extension would be needed, but 'simple' works for space-separated tokens.
        """
        sql = text("""
            UPDATE embeddings
            SET content_search = to_tsvector('simple', content)
            WHERE document_id = :doc_id
        """)
        await self.db.execute(sql, {"doc_id": document_id})
