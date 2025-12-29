# 🚀 RAG Vector 설치 및 설정 가이드

본 문서는 로컬 개발 환경 및 운영 환경 구축을 위한 상세 가이드입니다.

---

## 1. 사전 요구사항
- **Docker**: 필수 (PostgreSQL, Redis, Worker 구동용)
- **API Key**: Google Gemini API Key

## 2. 설치 및 실행 (Docker)

1. **환경 변수 설정**
   ```bash
   cp .env.example .env
   ```

2. **서비스 실행**
   ```bash
   docker-compose up -d --build
   ```

3. **초기 데이터베이스 및 계정 확인**
   - 시스템 기동 시 `alembic upgrade head`가 자동으로 실행됩니다.
   - **기본 관리자 계정**이 자동으로 생성됩니다:
     - **Email**: `admin@example.com`
     - **Password**: `admin123`

## 3. 구성 요소 확인
- **Redis**: 비동기 작업 브로커 (6379 포트)
- **Worker**: `rag_worker` 컨테이너가 문서 처리를 담당합니다.
- **Backend**: `rag_backend` 컨테이너 (8000 포트)


---

## 3. 로컬 개발 환경 수동 설치

### 3.1 가상환경 및 패키지 설치
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3.2 데이터베이스 (PostgreSQL) 설정
1. PostgreSQL에 `pgvector` 확장을 설치합니다.
   ```sql
   CREATE EXTENSION vector;
   ```
2. `.env` 파일의 `DATABASE_URL`을 로컬 DB 정보에 맞게 수정합니다.
   ```env
   DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/rag_db
   ```
3. 마이그레이션 실행:
   ```bash
   alembic upgrade head
   ```

### 3.3 서버 실행
```bash
# 백엔드 서버
python -m app.main

# 관리자 UI (별도 터미널)
streamlit run admin_app.py
```

---

## 4. 주요 설정값 설명 (`.env`)

| 변수명 | 설명 | 기본값 |
| :--- | :--- | :--- |
| `LLM_PROVIDER` | 사용할 AI 모델 제공자 (gemini, openai 등) | `gemini` |
| `LLM_MODEL` | 사용할 모델 명칭 | `gemini-2.0-flash` |
| `CHUNK_SIZE` | 문서 분할 시 청크 크기 (문자 수) | `1000` |
| `CHUNK_OVERLAP` | 청크 간 겹침 범위 | `200` |
| `SEARCH_K` | 최종 반환할 문서 수 | `4` |
| `RERANK_K` | 재순위화 후보군 수 (K의 배수) | `40` |

---

## 5. 설치 확인 및 테스트

1. **상태 확인**: `http://localhost:8000/` 접속 시 `{"status": "ok"}` 반환 확인.
2. **API 문서**: `http://localhost:8000/docs` 접속 가능 여부 확인.
3. **DB 확인**: `embeddings` 테이블에 `vector` 및 `content_search` 컬럼이 정상적으로 생성되었는지 확인.

---
**최종 업데이트**: 2025-12-25