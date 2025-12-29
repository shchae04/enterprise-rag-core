# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.2.0] - 2025-12-22

### Added
- **Hybrid Search Engine**: Vector(pgvector)와 Keyword(TSVector) 검색을 결합한 하이브리드 검색 및 RRF(Reciprocal Rank Fusion) 알고리즘 도입.
- **Security & Authentication**: OAuth2 Password Flow 및 JWT 기반 인증 시스템 구축.
- **Distributed Task Queue**: Celery와 Redis를 도입하여 문서 파싱 및 임베딩 작업을 비동기화.
- **RAG Evaluation Pipeline**: Ragas 라이브러리를 사용한 정량적 품질 평가(Faithfulness, Relevance) 체계 마련.
- **Auto-Initialization**: 시스템 기동 시 기본 관리자 계정(`admin@example.com`) 자동 생성 기능.

### Changed
- **Admin UI Modernization**: Streamlit 관리자 페이지에 로그인 기능 및 비동기 작업 상태 모니터링 반영.
- **Architecture Refined**: API 서버와 Worker 프로세스 분리로 확장성 확보.

---

## [2.0.0] - 2025-12-22

### Added
- **모듈형 모놀리스 아키텍처**: 계층형 아키텍처 도입 (API/Service/Model/Core 계층 분리).
- **쿼리 확장 시스템**: LLM을 통한 검색 쿼리 확장 기능.
- **비동기 DB 처리**: SQLAlchemy 2.0 Async + asyncpg 도입.
- **Docker Multi-stage Build**: 최적화된 컨테이너 이미지 및 배포 환경.

### Changed
- **프로젝트 구조 개편**: scripts/, docker/, documentation/ 디렉토리 분리.
- **ORM 전환**: 동기식 psycopg2에서 비동기 SQLAlchemy로 전환.

---

## [1.0.0] - 2024-12-20
- 초기 릴리즈: 기본 RAG 시스템 및 다중 문서 포맷 지원.