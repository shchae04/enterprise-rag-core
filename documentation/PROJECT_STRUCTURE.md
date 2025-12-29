# 프로젝트 디렉토리 구조 상세 가이드

```text
rag-vector/
├── app/                        # 🚀 백엔드 애플리케이션
│   ├── main.py                # FastAPI 앱 진입점
│   ├── worker.py              # Celery Worker 태스크 정의 (비동기 처리)
│   ├── initial_data.py        # 초기 관리자 계정 생성 스크립트
│   ├── api/                   # API 레이어
│   │   ├── deps.py            # 의존성 주입 (Auth, DB)
│   │   └── v1/
│   │       ├── api.py         # 라우터 통합
│   │       └── endpoints/     # auth, chat, documents 엔드포인트
│   ├── core/                  # 핵심 설정
│   │   ├── celery_app.py      # Celery 설정 및 브로커 연결
│   │   ├── security.py        # JWT 및 패스워드 보안
│   │   ├── config.py          # 환경 변수 (Redis, JWT 설정 추가)
│   │   └── ...
│   ├── models/                # DB 모델 (User, Document, Embedding)
│   ├── schemas/               # Pydantic DTO (Token, User 등)
│   ├── services/              # 비즈니스 로직
│   └── utils/                 # 유틸리티
│
├── docker-compose.yml         # 🚢 전역 서비스 오케스트레이션 (DB, Redis, Worker 포함)
```
---
**최종 업데이트**: 2025-12-22
