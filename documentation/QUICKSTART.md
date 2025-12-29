# RAG Vector 5분 빠른 시작 가이드

## 1. 사전 요구사항
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 설치 및 실행
- [Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키 발급

## 2. 환경 설정
1. 프로젝트 루트 폴더로 이동합니다.
2. `.env.example` 파일을 복사하여 `.env` 파일을 생성합니다.
   ```bash
   cp .env.example .env
   ```
3. `.env` 파일을 열어 발급받은 API 키를 입력합니다.
   ```env
   GOOGLE_API_KEY=your_api_key_here
   ```

## 3. 시스템 실행 (Docker 권장)
Docker Compose를 사용하여 모든 서비스를 한 번에 실행합니다.
```bash
docker-compose up -d --build
```
최초 실행 시 데이터베이스 마이그레이션이 자동으로 수행됩니다.

## 4. 서비스 접속
| 서비스 | URL | 용도 |
| :--- | :--- | :--- |
| **관리자 UI** | [http://localhost:8501](http://localhost:8501) | 문서 업로드 및 관리 |
| **채팅 UI** | [http://localhost:3000](http://localhost:3000) | AI와 질의응답 |
| **API 문서** | [http://localhost:8000/docs](http://localhost:8000/docs) | 개발자 테스트 (Swagger) |

## 5. 단계별 테스트

### Step 1: 문서 업로드
1. 관리자 UI([http://localhost:8501](http://localhost:8501))에 접속합니다.
2. PDF, HWP 등 샘플 문서를 업로드하고 **[처리 시작]** 버튼을 누릅니다.
3. 문서 상태가 `ready`로 바뀔 때까지 기다립니다.

### Step 2: 질의응답
1. 채팅 UI([http://localhost:3000](http://localhost:3000))에 접속합니다.
2. (최초 1회) 계정을 생성하고 로그인합니다.
3. 업로드한 문서 내용에 대해 질문합니다.
   - 예: "이 문서의 핵심 요약은 뭐야?"

## 6. 문제 해결 (FAQ)
- **Q: DB 연결 에러가 납니다.**
  - A: `docker-compose ps`로 `db` 컨테이너가 실행 중인지 확인하세요.
- **Q: 답변이 "모르는 내용"이라고 나옵니다.**
  - A: 문서 업로드가 완료되었는지, 그리고 관리자 UI에서 문서 목록에 표시되는지 확인하세요.
- **Q: Gemini API 에러가 발생합니다.**
  - A: `.env`에 입력한 API 키가 유효한지, 그리고 할당량(Quota)이 남아있는지 확인하세요.

---
**최종 업데이트**: 2025-12-25