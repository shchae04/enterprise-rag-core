# 🏗️ Enterprise RAG Core 아키텍처 설계서

## 1. 시스템 개요
본 시스템은 대규모 사내 문서를 효율적으로 관리하고, 고도화된 RAG(Retrieval-Augmented Generation) 파이프라인을 통해 정확한 정보를 제공하는 엔터프라이즈급 검색 시스템입니다.

---

## 2. 핵심 아키텍처 원칙

1.  **계층형 모듈식 모놀리스 (Modular Monolith)**: 관심사 분리를 통해 유지보수성과 확장성을 극대화합니다.
2.  **비동기 분산 작업 처리 (Distributed Task Queue)**: Celery와 Redis를 사용하여 무거운 문서 처리 로직을 API 서버와 분리합니다.
3.  **보안 우선 (Security First)**: OAuth2 및 JWT 인증을 통해 API 접근을 제어하고 사용자별 권한을 관리합니다.
4.  **데이터 무결성 (Data Integrity)**: Alembic 마이그레이션과 데이터베이스 트랜잭션을 통해 데이터 일관성을 보장합니다.

---

## 3. 계층별 구조 (Layered Design)

### 3.1 API Layer (`app/api/v1/`)
- 요청 수신 및 응답 포맷팅 담당.
- **인증 미들웨어**: `deps.py`를 통해 JWT 토큰 검증 및 사용자 권한 확인.
- Pydantic 스키마를 이용한 데이터 검증.

### 3.2 Service Layer (`app/services/`)
- 핵심 비즈니스 로직 및 RAG 파이프라인 구현.
- `IngestService`: 문서 파싱 및 벡터화 로직 (Worker에서 주로 호출).
- `ChatService`: 쿼리 확장, 검색, 답변 생성.

### 3.3 Worker Layer (`app/worker.py`)
- Celery 기반의 비동기 작업 환경.
- API 서버의 부하를 분산하고 대용량 파일의 안정적인 처리 담당.

### 3.4 Data Layer (`app/models/`)
- SQLAlchemy ORM을 이용한 DB 테이블 정의.
- `users`: 사용자 계정 및 권한.
- `documents`: 문서 메타데이터.
- `embeddings`: pgvector 기반 벡터 데이터.

---

## 4. 고도화된 하이브리드 검색 엔진 (Hybrid Search Engine)

단순 벡터 유사도 검색의 한계를 극복하기 위해 **Vector + Keyword** 앙상블 전략을 사용합니다.

### Phase 1: 쿼리 확장 (Query Expansion)
- 사용자 질문의 의도를 분석하여 관련 키워드와 동의어를 포함한 확장 쿼리 생성.
- 어휘 불일치(Vocabulary Mismatch) 문제를 해결.

### Phase 2: 이원화 검색 (Dual Retrieval)
두 가지 검색 알고리즘을 병렬로 수행하여 후보군을 추출합니다.
1.  **Vector Search**: `pgvector` HNSW 인덱스를 사용한 **의미론적(Semantic)** 검색.
2.  **Keyword Search**: 한국어의 특성(띄어쓰기, 조사)을 고려하여 `ILIKE` 패턴 매칭을 통한 **키워드 포함(Partial Match)** 검색 사용 (기존 TSVECTOR의 토큰화 불일치 문제 해결).
3.  **Enhanced Recall**: 검색 후보군을 요청된 개수(k)의 **10배수**로 설정하여, 관련 문서가 누락될 확률을 최소화합니다.

### Phase 3: RRF (Reciprocal Rank Fusion)
- 두 검색 결과의 순위를 융합하여 최종 순위를 산출합니다.
- 공식: $Score(d) = \sum \frac{1}{k + rank(d)}$
- 의미적으로 연관되거나 키워드가 정확히 일치하는 문서 모두 상위권에 노출됩니다.

### Phase 4: 답변 생성 (Generation)
- 상위 K개 문서를 LLM(Gemini 2.0 Flash)에 Context로 제공하여 근거 있는 답변(Grounded Generation)을 생성합니다.

---

## 5. 데이터 처리 흐름 (Data Flow)

### 5.1 비동기 문서 수집 (Async Ingestion)
1.  **Client**: 문서 업로드 요청 (Auth Token 필요).
2.  **API**: 파일 로컬 저장 후 Celery Task 발행 (`process_document_task`).
3.  **API**: 사용자에게 `task_id` 즉시 응답 (비차단).
4.  **Redis**: 작업을 큐에 대기시킴.
5.  **Worker**: 큐에서 작업을 가져와 파싱 -> 임베딩 -> DB 저장 수행.

### 5.2 질의응답 (Querying)
1.  **Query Input**: 사용자 자연어 질문 수신.
2.  **Auth**: 토큰 유효성 검사.
3.  **RAG Pipeline**: 쿼리 확장 -> 광범위 벡터/키워드 검색(ILIKE) -> 재순위화 -> 답변 생성.

---

## 6. 보안 아키텍처

- **Authentication**: JWT (HS256) 기반의 무상태(Stateless) 인증.
- **Password Storage**: `bcrypt`를 이용한 단방향 해시 암호화.
- **Authorization**: OAuth2 Password Bearer 흐름 준수.

---
**최종 업데이트**: 2025-12-25
