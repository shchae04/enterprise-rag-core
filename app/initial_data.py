import asyncio
import logging
from sqlalchemy import select, text
from app.core.database import AsyncSessionLocal, engine
from app.models import Base
from app.models.user import User
from app.core.security import get_password_hash

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db() -> None:
    async with AsyncSessionLocal() as db:
        try:
            # Ensure tables exist when migrations are not present
            async with engine.begin() as conn:
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                except Exception as e:
                    logger.warning(f"⚠️ pgvector extension check failed (continuing): {e}")
                await conn.run_sync(Base.metadata.create_all)

            # 1. 관리자 계정이 이미 있는지 확인
            result = await db.execute(select(User).where(User.email == "admin@example.com"))
            user = result.scalars().first()
            
            if user:
                logger.info("✅ 관리자 계정이 이미 존재합니다.")
                return

            # 2. 없으면 생성
            logger.info("👤 관리자 계정을 생성합니다...")
            superuser = User(
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"), # 초기 비밀번호
                is_active=True,
                is_superuser=True,
            )
            db.add(superuser)
            await db.commit()
            logger.info("✅ 관리자 계정 생성 완료! [Email: admin@example.com / PW: admin123]")
            
        except Exception as e:
            logger.error(f"❌ 초기 데이터 생성 중 오류 발생: {e}")
            raise e

if __name__ == "__main__":
    asyncio.run(init_db())
