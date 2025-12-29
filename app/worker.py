import asyncio
from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.services.ingest_service import IngestService
from asgiref.sync import async_to_sync

@celery_app.task(acks_late=True)
def process_document_task(file_path: str, source_type: str):
    """
    비동기 문서 처리 태스크 (Celery Worker에서 실행)
    """
    async def _process():
        async with AsyncSessionLocal() as db:
            service = IngestService(db)
            await service.process_document(file_path, source_type)

    # Celery는 기본적으로 동기 함수를 기대하므로, 비동기 코드를 실행하기 위해 async_to_sync 사용
    # 또는 asyncio.run(_process()) 사용
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(_process())
    return f"Processed {file_path}"
