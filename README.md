# Enterprise RAG Core

[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fshchae04%2Frag-vector&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)
[![GitHub stars](https://img.shields.io/github/stars/shchae04/rag-vector?style=social)](https://github.com/shchae04/rag-vector)
[![GitHub forks](https://img.shields.io/github/forks/shchae04/rag-vector?style=social)](https://github.com/shchae04/rag-vector)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.2-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

> **기업용 지식 관리 및 질의응답을 위한 고성능 RAG 엔진의 핵심 코어**
> Gemini 2.5 Flash Lite 기반의 하이브리드 검색 파이프라인 탑재

## 개요

RAG Vector는 사내 문서를 안전하게 관리하고 AI 기반 질의응답을 제공하는 엔터프라이즈급 시스템입니다. Docker Compose 기반의 컨테이너 아키텍처로 복잡한 설치 과정 없이 즉시 실행 가능하며, 고급 RAG(Retrieval-Augmented Generation) 기술을 통해 높은 검색 정확도를 보장합니다.

## 스크린샷 (Screenshots)

| **Admin Dashboard (문서 관리)** | **Chat Interface (질의응답)** |
|:---------------------------:|:--------------------------:|
| <img src="assets/admin_ui_placeholder.png" alt="Admin UI" width="400"> | <img src="assets/chat_ui_placeholder.png" alt="Chat UI" width="400"> |
| *문서 업로드 및 처리 현황 모니터링* | *문서 기반의 정확한 답변 및 출처 제공* |
> *스크린샷은 예시입니다. 실제 구동 화면을 `assets/` 폴더에 캡처하여 넣어주세요.*

### 주요 특징

- **🔍 차세대 하이브리드 검색 (Hybrid Search Engine)**
  - **Vector Search**: 의미 기반 검색 (pgvector HNSW)
  - **Keyword Search**: 한국어 최적화 부분 일치 검색 (ILIKE Pattern Matching)
  - **RRF (Reciprocal Rank Fusion)**: 두 검색 결과를 앙상블하여 최적의 순위 도출
  - **Enhanced Recall**: 후보군을 10배수로 확대(`limit = top_k * 10`)하여 검색 누락 최소화

- **⚡️ 엔터프라이즈급 성능 및 아키텍처**
  - **비동기 처리**: Celery + Redis 기반의 Non-blocking 문서 처리
  - **보안**: JWT 인증 및 RBAC 권한 관리
  - **확장성**: 모듈형 모놀리스 구조로 기능 확장 용이

- **🧪 품질 보증 (Quality Assurance)**
  - **Ragas Evaluation**: Faithfulness, Answer Relevancy 자동 측정 파이프라인
  - **CI/CD Integration**: 코드 변경 시 검색 품질 자동 검증

- **다양한 문서 포맷 지원**
  - HWP, PDF, DOCX, XLSX, TXT, MD 등

## 기술 스택

| 구분 | 기술 | 용도 |
|------|------|------|
| **Backend** | FastAPI 0.109.2 | 비동기 API 서버 |
| **Database** | PostgreSQL 16 | pgvector (Vector) + ILIKE (Keyword) |
| **Broker/Queue** | Redis + Celery | 비동기 작업 처리 |
| **Search Algo** | RRF + KeywordReranker | 하이브리드 검색 및 재순위화 |
| **Evaluation** | Ragas + LangSmith | RAG 품질 평가 및 추적 |
| **Auth** | OAuth2 + JWT | 보안 및 인증 |
| **AI/LLM** | Google Gemini 2.5 Flash Lite | 임베딩 및 답변 생성 (안정성 강화) |
| **DevOps** | Docker, GitHub Actions | 배포 및 CI/CD |

## 빠른 시작 (Quick Start)

### 사전 요구사항

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 설치 및 실행
- [Google AI Studio](https://aistudio.google.com/)에서 API Key 발급 (무료)

### 설치 및 실행

1. **환경 변수 설정**
   ```bash
   cp .env.example .env
   # .env 파일을 열어 GOOGLE_API_KEY를 입력하세요
   ```

2. **Docker Compose로 전체 시스템 실행**
   ```bash
   docker-compose up --build -d
   ```
   최초 실행 시 마이그레이션과 **기본 관리자 계정 생성**(`admin@example.com / admin123`)이 자동으로 수행됩니다.

3. **서비스 접속**

   | 서비스 | URL | 용도 |
   |--------|-----|------|
   | **채팅 인터페이스** | [http://localhost:3000](http://localhost:3000) | AI 비서와 질의응답 (Rag-Model 선택) |
   | **문서 관리** | [http://localhost:8501](http://localhost:8501) | 문서 업로드/삭제 (로그인 필요) |
   | **API 문서** | [http://localhost:8000/docs](http://localhost:8000/docs) | FastAPI Swagger UI |

4. **시스템 상태 확인**
   ```bash
   docker-compose ps
   docker-compose logs -f worker  # 비동기 작업 로그 확인
   ```

## 프로젝트 구조

```
rag-vector/
├── app/                    # 백엔드 애플리케이션
│   ├── api/v1/            # API 라우터 (FastAPI)
│   ├── services/          # 비즈니스 로직 (RAG Pipeline)
│   ├── models/            # SQLAlchemy 모델 (Document, User 등)
│   ├── core/              # 설정, 로깅, 예외 처리, 보안, Celery 설정
│   ├── utils/             # 파일 파서 및 유틸리티
│   ├── worker.py          # Celery 비동기 작업 정의
│   └── initial_data.py    # 초기 데이터 (관리자) 생성 스크립트
├── docker/                # Docker 설정 (entrypoint에서 마이그레이션 및 초기화 수행)
```

### 상세 문서

더 자세한 정보는 `/documentation` 폴더의 문서를 참조하세요:

- [ARCHITECTURE.md](documentation/ARCHITECTURE.md) - 시스템 아키텍처 및 고급 RAG 파이프라인
- [API.md](documentation/API.md) - REST API 엔드포인트 상세
- [PROJECT_STRUCTURE.md](documentation/PROJECT_STRUCTURE.md) - 디렉토리 구조 설명
- [USER_GUIDE.md](documentation/USER_GUIDE.md) - 채팅 및 문서 관리 가이드
- [SETUP.md](documentation/SETUP.md) - 로컬 개발 환경 구축

## 주요 기능

### 1. 고급 RAG 파이프라인

**3단계 검색 전략으로 정확도 극대화**

```
사용자 질의
    ↓
[Step 1] 쿼리 확장 (Query Expansion)
    - 유의어, 관련 용어 추가 (Gemini 2.5 Flash Lite)
    - 어휘 불일치 문제 해결
    ↓
[Step 2] 광범위 후보 검색 (Wide Retrieval)
    - 상위 k*10개 후보 검색 (예: 40개~80개)
    - HNSW 인덱스로 밀리초 단위 검색
    - ILIKE 패턴 매칭으로 키워드 포함 문서 확보
    ↓
[Step 3] 하이브리드 재순위화 (RRF & Reranking)
    - 벡터 유사도 + 키워드 매칭 점수 결합
    - boost_weight=0.3 적용
    ↓
최종 상위 k개 문서를 LLM에 전달
```

### 2. 다양한 문서 포맷 지원

- **HWP**: `olefile` 기반 한글 문서 파싱
- **PDF**: `PyMuPDF` 고속 파싱
- **Office**: DOCX, XLSX 완벽 지원
- **텍스트**: TXT, MD 등

### 3. 멀티 LLM 지원 (Multi-Model Support)

본 프로젝트는 기본적으로 **Google Gemini 2.5 Flash Lite**를 사용하지만, 설정을 통해 다른 모델로 손쉽게 전환할 수 있습니다.

#### 모델 변경 방법

1. `.env` 파일을 엽니다.
2. `LLM_PROVIDER`와 `LLM_MODEL` 값을 수정합니다.

**Gemini (기본값)**
```bash
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash-lite  # 또는 gemini-1.5-pro
GOOGLE_API_KEY=your_google_key
```

**OpenAI (GPT-4o 등)**
```bash
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
OPENAI_API_KEY=your_openai_key
```

**Anthropic (Claude 3.5 Sonnet)**
```bash
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20240620
ANTHROPIC_API_KEY=your_anthropic_key
```

> **참고**: 모델 변경 후 변경 사항을 적용하려면 `docker-compose restart backend worker` 명령어를 실행하세요.

**⚠️ 주의: 임베딩 모델(Embedding Model) 관련**
본 프로젝트는 검색 성능 최적화를 위해 임베딩 모델을 **Google Gemini(`text-embedding-004`)**로 고정하여 사용합니다.
만약 코드 레벨에서 임베딩 모델을 변경할 경우, 기존에 저장된 벡터 데이터와 호환되지 않으므로 **데이터베이스를 초기화하고 모든 문서를 재업로드(Re-indexing)** 해야 합니다.

### 4. 엔터프라이즈급 운영 기능

- **데이터 무결성**: 트랜잭션 기반 원자적(Atomic) 작업
- **자동 마이그레이션**: 컨테이너 시작 시 Alembic 자동 실행
- **구조화된 로깅**: JSON 형식의 체계적인 로그
- **예외 처리**: 글로벌 예외 핸들러로 표준화된 에러 응답

## 개발 가이드

### 로컬 개발 환경

```bash
# 1. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 4. PostgreSQL 시작 (Docker Compose로 DB만 실행)
docker-compose up -d postgres

# 5. 데이터베이스 마이그레이션
alembic upgrade head

# 6. 백엔드 서버 실행
uvicorn app.main:app --reload --port 8000

# 7. 관리자 UI 실행 (별도 터미널)
streamlit run admin_app.py
```

### 테스트

```bash
# API 서버 상태 확인
curl http://localhost:8000/health

# 문서 업로드 테스트
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@test.pdf"

# 채팅 테스트
curl -X POST http://localhost:8000/api/v1/chat/query \
  -H "Content-Type: application/json" \
  -d '{"query": "테스트 질문"}'
```

### 데이터베이스 마이그레이션

```bash
# 마이그레이션 파일 생성
alembic revision --autogenerate -m "Add new column"

# 마이그레이션 적용
alembic upgrade head

# 롤백
alembic downgrade -1
```

## 환경 변수 설정

주요 환경 변수 목록 (`.env` 파일):

```bash
# LLM 설정
GOOGLE_API_KEY=your_google_api_key_here
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash-lite

# 데이터베이스
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/rag_db

# 서버 설정
BACKEND_PORT=8000
ADMIN_PORT=8501
WEBUI_PORT=3000

# RAG 설정
CHUNK_SIZE=500
CHUNK_OVERLAP=100
SEARCH_K=4
RERANK_K=40  # k*10

# 웹 UI
WEBUI_NAME=Corp RAG Agent
ENABLE_WEB_SEARCH=False
```

## 사용 가이드

### 문서 관리 (Admin UI)

1. **http://localhost:8501** 접속
2. 파일 드래그 앤 드롭으로 업로드
3. "업로드 시작" 버튼 클릭
4. 자동으로 문서 파싱 및 임베딩 처리

### 채팅 (Open WebUI)

1. **http://localhost:3000** 접속
2. 계정 생성 (최초 1회)
3. 모델 선택: `Corp-RAG-Agent`
4. 질문 입력:
   - "재택 근무 규정이 무엇인가요?"
   - "프로젝트 담당자는 누구인가요?"

## 문제 해결

### 일반적인 문제

**Q. "Quota exceeded" 오류**
A. Gemini API 무료 할당량 초과. `LLM_MODEL`을 `gemini-2.5-flash-lite`로 변경하여 해결했습니다.

**Q. 모델이 보이지 않음**
A. Open WebUI와 백엔드 연동 확인. `rag-model`만 표시되는 것이 정상입니다.

**Q. HWP 파일 읽기 실패**
A. 암호화된 HWP는 미지원. 암호 해제 후 업로드.

**Q. 문서가 있는데 검색이 안 됨**
A. 키워드 검색(ILIKE)이 적용되었으므로 정확한 단어가 포함되어 있다면 검색됩니다. 유사어가 문제라면 질문을 조금 더 구체적으로 해주세요.

### 로그 확인

```bash
# 전체 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f openwebui
```

## 기여 방법

프로젝트에 기여하고 싶으신가요?

1. 이 저장소를 Fork
2. Feature 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 변경사항 커밋 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 Push (`git push origin feature/AmazingFeature`)
5. Pull Request 생성

자세한 내용은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요.

## 로드맵 (Roadmap)

### ✅ Phase 1: Foundation (완료)
- [x] **Core Architecture**: 모듈형 모놀리스(Modular Monolith) 설계 및 비동기(Async) 처리 구현
- [x] **RAG Engine**: 쿼리 확장(Query Expansion) 및 하이브리드 재순위화(Hybrid Reranking) 파이프라인 구축
- [x] **Infrastructure**: Docker Compose 기반 컨테이너 오케스트레이션 및 CI/CD 자동화 (GitHub Actions)
- [x] **Documentation**: 엔터프라이즈 표준 기술 문서 및 운영 가이드 수립
- [x] **Search Optimization**: 한국어 처리를 위한 ILIKE 검색 도입 및 후보군 확대 적용

### 🚧 Phase 2: Knowledge Integration (진행 예정)
- [ ] **Unified Ingestion Layer**: `LangChain` 기반의 확장 가능한 데이터 커넥터 아키텍처 설계
  - **SaaS Connectors**: Confluence, Notion, Google Drive 연동
  - **Local Watcher**: `watchdog` 기반의 파일 시스템 실시간 변경 감지(Event-Driven)
- [ ] **Smart Sync Pipeline**: 데이터 효율성을 위한 증분 업데이트(Incremental Sync) 구현
  - **CDC(Change Data Capture)**: 콘텐츠 해시 비교를 통한 중복 처리 방지
  - **Job Scheduling**: `APScheduler`를 이용한 주기적 외부 소스 동기화

### 🔮 Phase 3: Advanced Intelligence
- [ ] **Frontend Modernization**: Streamlit을 대체하는 React(Next.js) 기반 엔터프라이즈 Admin Console 구축
- [ ] **Scalability**: Redis/Celery 도입을 통한 대용량 문서 비동기 분산 처리
- [ ] **Multi-modal RAG**: 이미지, 도표, 차트 분석이 가능한 멀티모달 파이프라인 고도화



## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 크레딧

- **FastAPI** - 고성능 Python 웹 프레임워크
- **PostgreSQL + pgvector** - 벡터 검색 데이터베이스
- **Google Gemini** - 무료 멀티모달 AI 모델
- **Open WebUI** - 오픈소스 채팅 인터페이스
- **Streamlit** - 빠른 관리자 UI 구축

---

**Made with precision by Enterprise RAG Team**
문의: [GitHub Issues](https://github.com/shchae04/rag-vector/issues)
