# 🔧 엔터프라이즈 리팩토링 가이드 (완료)

본 문서는 `ics2-vector`에서 `rag-vector`로의 성공적인 엔터프라이즈 리팩토링 결과를 정리한 문서입니다.

## 1. 마이그레이션 핵심 요약

### AS-IS (PoC 버전)
- `main.py`에 모든 로직이 포함된 거대 파일.
- 직접 SQL 쿼리 작성 (SQL Injection 취약성).
- 동기식(Synchronous) 데이터베이스 처리.
- 스키마 변경 이력 추적 불가.

### TO-BE (엔터프라이즈 버전)
- **계층별 분리**: `app/` 하위 디렉토리로 역할 분담.
- **비동기 ORM**: SQLAlchemy Async를 사용한 안전한 데이터 핸들링.
- **자동 마이그레이션**: Alembic을 통한 데이터베이스 버전 관리.
- **고급 RAG**: 쿼리 확장 및 재순위화 알고리즘 탑재.

## 2. 개발자를 위한 주요 변경 사항

### 2.1 모델 정의 및 수정
데이터베이스 테이블을 수정하려면 `app/models/`에서 클래스를 수정한 후, 아래 명령어를 실행하세요.
```bash
# Docker 환경
docker-compose exec backend alembic revision --autogenerate -m "설명"
docker-compose exec backend alembic upgrade head
```

### 2.2 새 API 추가
1.  `app/schemas/`에 입출력 DTO 정의.
2.  `app/api/v1/endpoints/`에 새 엔드포인트 파일 생성 또는 추가.
3.  `app/api/v1/api.py`에 라우터 등록.

### 2.3 검색 알고리즘 튜닝
검색 품질을 조정하려면 `app/services/chat_service.py`와 `app/services/rerank_service.py`를 확인하세요.
- `RERANK_K`: 재순위화 대상 후보 수 조정 (기본 k*10).
- `boost_weight`: 키워드 일치 가중치 조정 (기본 0.3).

## 3. 트러블슈팅 가이드

### 3.1 DB 연결 실패 시
- `.env`의 `DATABASE_URL` 형식이 `postgresql+asyncpg://...`인지 확인하세요. (비동기 드라이버 필수)

### 3.2 문서 업로드 후 검색이 안 될 때
- 관리자 UI에서 문서의 `status`가 `ready`인지 확인하세요.
- 임베딩 생성 중 API Quota 초과가 발생했는지 로그를 확인하세요.

---
**최종 업데이트**: 2025-12-22