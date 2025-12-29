# Python 3.11 슬림 이미지 사용
FROM python:3.11-slim

# 로그 버퍼링 비활성화
ENV PYTHONUNBUFFERED=1

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 의존성 설치 (캐시 활용을 위해 먼저 복사)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 전체 소스 코드 복사
COPY . .

# entrypoint.sh 파일 처리
# 1. 파일이 존재하는지 확인하고 (디버깅용)
# 2. Windows 줄바꿈 문자 제거 및 실행 권한 부여
# 3. 만약 docker/entrypoint.sh가 없으면 에러를 뱉도록 함
RUN ls -la docker/ && \
    sed -i 's/\r$//' docker/entrypoint.sh && \
    chmod +x docker/entrypoint.sh

# 업로드 디렉토리 생성
RUN mkdir -p docs

# 포트 노출
EXPOSE 8000

# entrypoint 실행
ENTRYPOINT ["/app/docker/entrypoint.sh"]