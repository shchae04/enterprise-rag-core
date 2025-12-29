# 기여 가이드 (Contributing Guide)

이 문서는 Corp RAG Agent 프로젝트에 기여하고자 하는 개발자를 위한 가이드입니다. 프로젝트의 코드 품질과 일관성을 유지하기 위해 모든 기여자는 이 가이드를 준수해야 합니다.

## 목차

- [기여 환경 설정](#기여-환경-설정)
- [개발 워크플로우](#개발-워크플로우)
- [코드 스타일](#코드-스타일)
- [테스트](#테스트)
- [데이터베이스 마이그레이션](#데이터베이스-마이그레이션)
- [문서화](#문서화)
- [리뷰 프로세스](#리뷰-프로세스)

---

## 기여 환경 설정

### 시스템 요구사항

프로젝트 개발을 위해 다음 소프트웨어가 필요합니다:

- **Python**: 3.11 이상
- **Docker Desktop**: 필수 (PostgreSQL, Redis, Worker 구동용)
- **Git**: 2.30 이상

### 저장소 클론 및 설정

... (중략) ...

#### 방법 1: Docker Compose 사용 (권장)

비동기 작업 큐(Celery)와 메시지 브로커(Redis) 환경을 포함하여 한 번에 실행합니다.

```bash
# 전체 서비스 실행
docker-compose up --build -d

# 관리자 계정 확인: admin@example.com / admin123
```

**접속 주소:**
- 백엔드 API: http://localhost:8000
- API 문서: http://localhost:8000/docs
- Admin UI: http://localhost:8501
- Open WebUI: http://localhost:3000

#### 방법 2: 로컬 Python 환경

로컬에서 직접 개발하려면 다음 단계를 따르세요:

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# PostgreSQL + pgvector 필요 (Docker 권장)
docker-compose up db -d

# 데이터베이스 마이그레이션
alembic upgrade head

# 개발 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 개발 도구 설정

코드 품질을 위해 다음 도구들을 사용합니다:

```bash
# 개발 의존성 설치 (향후 추가 예정)
pip install black flake8 mypy pytest pytest-asyncio pytest-cov
```

**IDE 설정 권장사항:**
- **VSCode**: Python 확장, Pylance 활성화
- **PyCharm**: 타입 체크 활성화, PEP 8 검사 활성화

---

## 개발 워크플로우

### 브랜치 전략

Git Flow를 기반으로 한 브랜치 전략을 사용합니다:

```
main          (프로덕션 배포용, 항상 안정적인 상태 유지)
  ├─ develop  (개발 통합 브랜치)
       ├─ feature/기능명    (새로운 기능 개발)
       ├─ bugfix/버그명     (버그 수정)
       └─ hotfix/긴급수정   (프로덕션 긴급 패치)
```

#### 브랜치 생성 규칙

```bash
# 기능 개발
git checkout -b feature/add-user-authentication

# 버그 수정
git checkout -b bugfix/fix-document-upload-error

# 긴급 패치
git checkout -b hotfix/fix-security-vulnerability
```

**브랜치 이름 규칙:**
- 소문자와 하이픈 사용
- 명확하고 설명적인 이름
- 이슈 번호가 있다면 포함 (예: `feature/123-add-oauth`)

### 커밋 메시지 컨벤션

[Conventional Commits](https://www.conventionalcommits.org/) 스펙을 따릅니다.

#### 커밋 메시지 형식

```
<타입>(<범위>): <제목>

<본문 (선택사항)>

<푸터 (선택사항)>
```

#### 타입 (Type)

- `feat`: 새로운 기능 추가
- `fix`: 버그 수정
- `docs`: 문서 변경
- `style`: 코드 포맷팅, 세미콜론 누락 등 (기능 변경 없음)
- `refactor`: 코드 리팩토링 (기능 변경 없음)
- `perf`: 성능 개선
- `test`: 테스트 추가 또는 수정
- `chore`: 빌드 프로세스, 도구 설정 등
- `ci`: CI/CD 설정 변경

#### 예시

```bash
# 기본 커밋
git commit -m "feat(chat): 채팅 히스토리 저장 기능 추가"

# 본문이 있는 커밋
git commit -m "fix(database): pgvector 연결 타임아웃 문제 수정

데이터베이스 연결 풀 설정을 조정하여 동시 접속 시
타임아웃이 발생하는 문제를 해결했습니다.

Fixes #123"

# Breaking Change
git commit -m "feat(api)!: REST API 엔드포인트 경로 변경

BREAKING CHANGE: /api/documents -> /api/v1/documents로 변경"
```

### Pull Request 프로세스

#### 1. 작업 전 준비

```bash
# develop 브랜치를 최신 상태로 업데이트
git checkout develop
git pull upstream develop

# 새 기능 브랜치 생성
git checkout -b feature/your-feature-name
```

#### 2. 개발 및 커밋

```bash
# 변경사항 추가
git add .

# 커밋
git commit -m "feat(module): 설명"

# 주기적으로 원격 저장소에 푸시
git push origin feature/your-feature-name
```

#### 3. Pull Request 생성

1. GitHub에서 본인의 포크 저장소로 이동
2. "Compare & pull request" 버튼 클릭
3. **Base 브랜치**: `upstream/develop`
4. **PR 제목**: 커밋 메시지 컨벤션 준수
5. **PR 설명 템플릿 작성**:

```markdown
## 변경 사항 요약
- 변경 내용을 간략히 설명

## 관련 이슈
- Closes #이슈번호
- Related to #이슈번호

## 변경 타입
- [ ] 새로운 기능
- [ ] 버그 수정
- [ ] 문서 업데이트
- [ ] 리팩토링
- [ ] 성능 개선

## 체크리스트
- [ ] 코드가 PEP 8 스타일 가이드를 준수합니다
- [ ] 타입 힌트가 모든 함수에 추가되었습니다
- [ ] 단위 테스트를 작성하고 통과했습니다
- [ ] 문서를 업데이트했습니다
- [ ] 로컬에서 전체 시스템을 테스트했습니다

## 테스트 방법
1. 테스트 단계 설명
2. 예상 결과 설명

## 스크린샷 (UI 변경 시)
(스크린샷 첨부)
```

#### 4. 코드 리뷰 대응

- 리뷰어의 피드백에 정중하게 응답
- 요청된 변경사항을 반영한 후 추가 커밋
- 리뷰가 완료되면 승인 대기

#### 5. Merge

- 최소 1명 이상의 승인 필요
- CI/CD 체크가 모두 통과해야 함
- Squash and merge 권장 (커밋 히스토리 정리)

---

## 코드 스타일

### Python 스타일 가이드 (PEP 8)

프로젝트는 [PEP 8](https://peps.python.org/pep-0008/) 스타일 가이드를 따릅니다.

#### 주요 규칙

**들여쓰기:**
```python
# 좋은 예
def process_document(
    document_id: int,
    content: str,
    metadata: dict
) -> ProcessedDocument:
    pass
```

**네이밍 컨벤션:**
```python
# 클래스: PascalCase
class DocumentService:
    pass

# 함수/변수: snake_case
def calculate_embedding_similarity(vector_a, vector_b):
    user_name = "admin"
    max_results = 10

# 상수: UPPER_SNAKE_CASE
MAX_DOCUMENT_SIZE = 10_000_000
DEFAULT_CHUNK_SIZE = 1000

# Private: _prefix
def _internal_helper_function():
    pass
```

**임포트 순서:**
```python
# 1. 표준 라이브러리
import os
import sys
from typing import List, Optional

# 2. 서드파티 라이브러리
from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# 3. 로컬 애플리케이션
from app.core.config import settings
from app.models.document import Document
from app.services.vector_service import VectorService
```

**라인 길이:**
- 최대 88자 (Black 포맷터 기준)
- 복잡한 표현식은 여러 줄로 나눔

### 타입 힌트 사용

모든 함수는 타입 힌트를 포함해야 합니다:

```python
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

# 함수 시그니처에 타입 힌트 필수
async def get_document_by_id(
    document_id: int,
    db: AsyncSession
) -> Optional[Document]:
    """문서 ID로 문서를 조회합니다.

    Args:
        document_id: 조회할 문서의 ID
        db: 데이터베이스 세션

    Returns:
        Document 객체 또는 None (존재하지 않을 경우)
    """
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    return result.scalar_one_or_none()

# 복잡한 타입은 Type Alias 사용
EmbeddingVector = List[float]
DocumentMetadata = Dict[str, Any]

def create_embedding(text: str) -> EmbeddingVector:
    pass
```

### Docstring 작성

Google 스타일 Docstring을 사용합니다:

```python
def search_similar_documents(
    query_vector: List[float],
    limit: int = 5,
    threshold: float = 0.7
) -> List[Document]:
    """쿼리 벡터와 유사한 문서를 검색합니다.

    벡터 유사도 기반으로 데이터베이스에서 가장 관련성 높은
    문서를 검색하여 반환합니다.

    Args:
        query_vector: 검색 쿼리의 임베딩 벡터
        limit: 반환할 최대 문서 수 (기본값: 5)
        threshold: 유사도 임계값 (0.0 ~ 1.0, 기본값: 0.7)

    Returns:
        유사도 순으로 정렬된 문서 리스트

    Raises:
        ValueError: query_vector가 비어있거나 형식이 잘못된 경우
        DatabaseError: 데이터베이스 연결 실패 시

    Example:
        >>> vector = [0.1, 0.2, 0.3, ...]
        >>> results = search_similar_documents(vector, limit=3)
        >>> for doc in results:
        ...     print(doc.title)
    """
    if not query_vector:
        raise ValueError("query_vector는 비어있을 수 없습니다")

    # 구현...
```

### 코드 포맷팅 도구

프로젝트는 다음 도구를 사용합니다:

```bash
# Black (코드 포맷터)
black app/ --line-length 88

# Flake8 (린터)
flake8 app/ --max-line-length 88 --extend-ignore E203,W503

# MyPy (타입 체커)
mypy app/ --ignore-missing-imports
```

---

## 테스트

### 테스트 작성 원칙

1. **모든 새로운 기능은 테스트를 포함해야 합니다**
2. **버그 수정 시 재현 테스트를 먼저 작성합니다**
3. **테스트는 독립적이고 순서에 무관해야 합니다**
4. **테스트 커버리지는 최소 80% 이상 유지합니다**

### 테스트 구조

```
tests/
├── unit/              # 단위 테스트
│   ├── test_services/
│   │   ├── test_vector_service.py
│   │   └── test_chat_service.py
│   ├── test_utils/
│   │   └── test_parsers.py
│   └── test_models/
├── integration/       # 통합 테스트
│   ├── test_api/
│   │   ├── test_documents_api.py
│   │   └── test_chat_api.py
│   └── test_database/
└── conftest.py        # 공통 픽스처
```

### 단위 테스트 작성

```python
# tests/unit/test_services/test_vector_service.py

import pytest
from unittest.mock import Mock, AsyncMock
from app.services.vector_service import VectorService

@pytest.fixture
def mock_db_session():
    """Mock 데이터베이스 세션"""
    session = AsyncMock()
    return session

@pytest.fixture
def vector_service(mock_db_session):
    """VectorService 인스턴스"""
    return VectorService(db=mock_db_session)

@pytest.mark.asyncio
async def test_search_similar_documents_success(vector_service):
    """유사 문서 검색 성공 테스트"""
    # Given
    query_vector = [0.1, 0.2, 0.3]
    expected_documents = [
        Mock(id=1, title="문서1", similarity=0.95),
        Mock(id=2, title="문서2", similarity=0.87)
    ]
    vector_service.db.execute = AsyncMock(return_value=Mock(
        scalars=Mock(return_value=Mock(all=Mock(return_value=expected_documents)))
    ))

    # When
    results = await vector_service.search_similar(query_vector, limit=5)

    # Then
    assert len(results) == 2
    assert results[0].id == 1
    assert results[0].similarity == 0.95

@pytest.mark.asyncio
async def test_search_similar_documents_empty_vector_raises_error(vector_service):
    """빈 벡터로 검색 시 에러 발생 테스트"""
    # Given
    query_vector = []

    # When & Then
    with pytest.raises(ValueError, match="query_vector는 비어있을 수 없습니다"):
        await vector_service.search_similar(query_vector)
```

### 통합 테스트 작성

```python
# tests/integration/test_api/test_documents_api.py

import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_upload_document_success():
    """문서 업로드 API 통합 테스트"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Given
        files = {"file": ("test.txt", b"Test content", "text/plain")}

        # When
        response = await client.post("/api/v1/documents/upload", files=files)

        # Then
        assert response.status_code == 200
        data = response.json()
        assert "document_id" in data
        assert data["status"] == "success"

@pytest.mark.asyncio
async def test_upload_invalid_file_type_returns_error():
    """지원하지 않는 파일 타입 업로드 시 에러 반환 테스트"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Given
        files = {"file": ("test.exe", b"Binary content", "application/x-msdownload")}

        # When
        response = await client.post("/api/v1/documents/upload", files=files)

        # Then
        assert response.status_code == 400
        assert "unsupported file type" in response.json()["detail"].lower()
```

### 테스트 실행 방법

```bash
# 모든 테스트 실행
pytest

# 특정 디렉토리 테스트
pytest tests/unit/

# 특정 파일 테스트
pytest tests/unit/test_services/test_vector_service.py

# 특정 테스트 함수
pytest tests/unit/test_services/test_vector_service.py::test_search_similar_documents_success

# 커버리지 포함
pytest --cov=app --cov-report=html

# 상세 출력
pytest -v

# 실패 시 즉시 중단
pytest -x
```

### 테스트 픽스처

공통 픽스처는 `tests/conftest.py`에 정의합니다:

```python
# tests/conftest.py

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.database import Base

@pytest.fixture(scope="session")
async def test_db_engine():
    """테스트용 데이터베이스 엔진"""
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:1234@localhost:5432/test_db",
        echo=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def test_db_session(test_db_engine):
    """테스트용 데이터베이스 세션"""
    async_session = sessionmaker(
        test_db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()
```

---

## 데이터베이스 마이그레이션

프로젝트는 **Alembic**을 사용하여 데이터베이스 스키마를 관리합니다.

### 모델 변경 시 마이그레이션 생성

1. **모델 변경**

```python
# app/models/document.py

from sqlalchemy import Column, Integer, String, DateTime, Text
from app.models.base import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)

    # 새로운 컬럼 추가
    author = Column(String(100), nullable=True)  # 👈 새로 추가됨
    created_at = Column(DateTime, server_default=func.now())
```

2. **마이그레이션 파일 생성**

```bash
# 마이그레이션 파일 자동 생성
alembic revision --autogenerate -m "Add author column to documents table"

# 생성된 파일 확인 (alembic/versions/xxxx_add_author_column.py)
```

3. **마이그레이션 파일 검토 및 수정**

```python
# alembic/versions/xxxx_add_author_column.py

def upgrade() -> None:
    # 자동 생성된 코드 확인
    op.add_column('documents', sa.Column('author', sa.String(length=100), nullable=True))

def downgrade() -> None:
    # 롤백 시 실행될 코드
    op.drop_column('documents', 'author')
```

4. **마이그레이션 적용**

```bash
# 로컬 환경
alembic upgrade head

# Docker 환경
docker-compose exec backend alembic upgrade head
```

### Alembic 명령어

```bash
# 현재 마이그레이션 상태 확인
alembic current

# 마이그레이션 히스토리 확인
alembic history

# 특정 버전으로 이동
alembic upgrade <revision>

# 이전 버전으로 롤백
alembic downgrade -1

# 처음으로 롤백
alembic downgrade base

# 마이그레이션 SQL만 확인 (실행하지 않음)
alembic upgrade head --sql
```

### 복잡한 마이그레이션 작성

데이터 변환이 필요한 경우 수동으로 작성합니다:

```python
# alembic/versions/xxxx_migrate_document_metadata.py

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

def upgrade() -> None:
    # 새 컬럼 추가
    op.add_column('documents', sa.Column('metadata_json', sa.JSON, nullable=True))

    # 기존 데이터 변환
    connection = op.get_bind()
    connection.execute(text("""
        UPDATE documents
        SET metadata_json = json_build_object(
            'file_type', file_type,
            'file_size', file_size
        )
        WHERE metadata_json IS NULL
    """))

    # 기존 컬럼 삭제
    op.drop_column('documents', 'file_type')
    op.drop_column('documents', 'file_size')

def downgrade() -> None:
    # 역방향 마이그레이션
    op.add_column('documents', sa.Column('file_type', sa.String(50), nullable=True))
    op.add_column('documents', sa.Column('file_size', sa.Integer, nullable=True))

    connection = op.get_bind()
    connection.execute(text("""
        UPDATE documents
        SET
            file_type = metadata_json->>'file_type',
            file_size = (metadata_json->>'file_size')::integer
        WHERE metadata_json IS NOT NULL
    """))

    op.drop_column('documents', 'metadata_json')
```

### 마이그레이션 베스트 프랙티스

1. **항상 마이그레이션 파일을 리뷰하세요**
   - `--autogenerate`는 완벽하지 않습니다
   - 수동으로 확인하고 필요시 수정합니다

2. **데이터 손실 방지**
   - 컬럼 삭제 전 백업
   - NOT NULL 제약조건 추가 시 기본값 설정

3. **롤백 가능성 고려**
   - `downgrade()` 함수를 항상 작성합니다
   - 데이터 변환은 가역적으로 작성합니다

4. **프로덕션 배포 전 테스트**
   ```bash
   # 테스트 환경에서 마이그레이션 테스트
   alembic upgrade head
   alembic downgrade -1
   alembic upgrade head
   ```

---

## 문서화

### 코드 주석

```python
# 복잡한 로직에는 주석 추가
def calculate_weighted_similarity(
    vector_a: List[float],
    vector_b: List[float],
    weights: Optional[List[float]] = None
) -> float:
    """가중치를 적용한 벡터 유사도를 계산합니다."""

    # 가중치가 없으면 모든 차원에 동일한 가중치 적용
    if weights is None:
        weights = [1.0] * len(vector_a)

    # 가중치 정규화 (합이 1이 되도록)
    total_weight = sum(weights)
    normalized_weights = [w / total_weight for w in weights]

    # 가중 코사인 유사도 계산
    # 공식: Σ(wi * ai * bi) / (√Σ(wi * ai²) * √Σ(wi * bi²))
    dot_product = sum(w * a * b for w, a, b in zip(normalized_weights, vector_a, vector_b))
    norm_a = sum(w * a ** 2 for w, a in zip(normalized_weights, vector_a)) ** 0.5
    norm_b = sum(w * b ** 2 for w, b in zip(normalized_weights, vector_b)) ** 0.5

    return dot_product / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0.0
```

### API 문서 (FastAPI 자동 생성)

FastAPI는 자동으로 OpenAPI 문서를 생성하지만, 더 나은 문서를 위해 다음을 추가합니다:

```python
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List

router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"]
)

@router.post(
    "/upload",
    summary="문서 업로드",
    description="""
    새로운 문서를 업로드하고 벡터 임베딩을 생성합니다.

    지원 파일 형식:
    - PDF (.pdf)
    - Word (.docx)
    - Excel (.xlsx)
    - HWP (.hwp)
    - Text (.txt, .md)
    """,
    response_description="업로드된 문서 정보",
    responses={
        200: {
            "description": "업로드 성공",
            "content": {
                "application/json": {
                    "example": {
                        "document_id": 123,
                        "title": "example.pdf",
                        "status": "success"
                    }
                }
            }
        },
        400: {"description": "잘못된 파일 형식"},
        500: {"description": "서버 오류"}
    }
)
async def upload_document(
    file: UploadFile = File(..., description="업로드할 문서 파일")
) -> dict:
    """문서를 업로드하고 처리합니다."""
    pass
```

### documentation/ 폴더 업데이트

주요 변경사항이 있을 때 다음 문서를 업데이트합니다:

- **API.md**: API 엔드포인트 변경 시
- **ARCHITECTURE.md**: 아키텍처 변경 시
- **PROJECT_STRUCTURE.md**: 프로젝트 구조 변경 시
- **USER_GUIDE.md**: 사용자 인터페이스 변경 시

```bash
# 예시: 새로운 API 엔드포인트 추가 시
# documentation/API.md 파일 업데이트
```

---

## 리뷰 프로세스

### 코드 리뷰 체크리스트

#### 리뷰어가 확인할 사항

- [ ] **기능성**: 코드가 의도한 대로 동작하는가?
- [ ] **테스트**: 충분한 테스트가 작성되었는가?
- [ ] **성능**: 불필요한 반복문이나 비효율적인 코드가 있는가?
- [ ] **보안**: SQL 인젝션, XSS 등 보안 취약점이 있는가?
- [ ] **가독성**: 코드가 명확하고 이해하기 쉬운가?
- [ ] **스타일**: 코드 스타일 가이드를 준수하는가?
- [ ] **문서화**: Docstring과 주석이 적절한가?
- [ ] **타입 힌트**: 모든 함수에 타입 힌트가 있는가?
- [ ] **에러 핸들링**: 예외 처리가 적절한가?
- [ ] **확장성**: 향후 변경에 유연한가?

#### 기여자가 확인할 사항 (Self Review)

PR을 제출하기 전에 스스로 다음을 확인하세요:

```bash
# 1. 코드 포맷팅
black app/ --check
flake8 app/

# 2. 타입 체크
mypy app/

# 3. 테스트
pytest tests/ --cov=app

# 4. 로컬 전체 시스템 테스트
docker-compose up --build
# 브라우저에서 http://localhost:8000/docs 접속하여 테스트
```

### Merge 기준

다음 조건을 모두 충족해야 Merge 가능합니다:

1. **최소 1명의 승인** (maintainer 또는 core contributor)
2. **CI/CD 체크 통과**
   - 린터 통과 (flake8, black)
   - 타입 체크 통과 (mypy)
   - 테스트 통과 (pytest)
   - 커버리지 80% 이상 유지
3. **Conflicts 없음** (develop 브랜치와 충돌 해결)
4. **문서 업데이트 완료** (필요 시)

### 리뷰 요청 시 고려사항

- **작은 PR을 선호합니다**: 가능하면 한 PR에 하나의 기능만
- **명확한 설명**: PR 설명에 무엇을, 왜, 어떻게 변경했는지 명시
- **스크린샷/GIF 첨부**: UI 변경 시 시각적 자료 첨부
- **Breaking Changes 명시**: API 변경 시 명확히 표시

---

## 추가 리소스

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 문서](https://docs.sqlalchemy.org/en/20/)
- [Alembic 튜토리얼](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Pydantic 문서](https://docs.pydantic.dev/)
- [Pytest 문서](https://docs.pytest.org/)

---

## 질문이나 도움이 필요하신가요?

- GitHub Issues에 질문 등록
- Discussions 탭에서 토론 참여
- 이메일: dev@example.com

**기여해주셔서 감사합니다!**
