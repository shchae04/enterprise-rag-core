# Enterprise RAG Core 백엔드 API 명세서

## 1. 개요
기본 접두사: `/api/v1`

---

## 2. 인증 API (Auth)

### 2.1 로그인 및 토큰 발급
- **URL**: `/auth/login`
- **Method**: `POST`
- **Content-Type**: `application/x-www-form-urlencoded`
- **Parameters**: `username` (email), `password`

**Success Response:**
```json
{
  "access_token": "eyJhbG...",
  "token_type": "bearer"
}
```

---

## 3. 문서 관리 API (Documents)

### 3.1 문서 업로드 (비동기)
**인증 필요** (Bearer Token)

- **URL**: `/documents/upload`
- **Method**: `POST`
- **Response**: `202 Accepted`

**Success Response:**
```json
{
  "filename": "report.pdf",
  "message": "Upload successful. Processing started in background.",
  "task_id": "uuid-string"
}
```

### 3.2 문서 삭제
**인증 필요** (Bearer Token)

- **URL**: `/documents/{document_id}`
- **Method**: `DELETE`

---

## 4. 채팅 API (Chat)

### 4.1 RAG 질의
- **URL**: `/chat/query`
- **Method**: `POST`
- **Content-Type**: `application/json`

**Request Body:**
```json
{
  "query": "재택 근무 규정이 어떻게 되나요?",
  "top_k": 4
}
```
- `query`: 사용자 질문 (필수)
- `top_k`: 참고할 문서 수 (선택, 기본값: 4)

**Success Response:**
```json
{
  "answer": "재택 근무 규정은...",
  "sources": [
    {
      "document_id": "uuid...",
      "filename": "규정집.pdf",
      "content": "발췌 내용...",
      "score": 0.95
    }
  ]
}
```

### 4.2 모델 목록 조회 (Open WebUI 호환)
- **URL**: `/chat/models` (또는 `/api/v1/models`)
- **Method**: `GET`

**Success Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "rag-model",
      "object": "model",
      "created": 1703480000,
      "owned_by": "organization"
    }
  ]
}
```

---

**최종 업데이트**: 2025-12-25
