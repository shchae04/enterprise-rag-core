import logging
import sys
from app.core.config import settings

# 로거 설정
def setup_logging():
    logger = logging.getLogger("ics2_vector")
    logger.setLevel(logging.INFO)

    # 콘솔 핸들러 (Docker/K8s 환경 표준)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # 중복 핸들러 방지
    if not logger.handlers:
        logger.addHandler(handler)
    
    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return logger

logger = setup_logging()
