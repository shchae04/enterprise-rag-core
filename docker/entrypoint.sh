#!/bin/bash
set -e

# DB가 준비될 때까지 대기 (선택 사항이나 권장됨)
echo "Waiting for database..."
# sleep 2 # depends_on healthcheck가 처리해주지만 안전을 위해

# 마이그레이션 실행
echo "Running database migrations..."
alembic upgrade head

# 초기 데이터(관리자 계정) 생성
echo "Checking & Creating initial data..."
python -m app.initial_data

# 애플리케이션 실행
if [ "$#" -gt 0 ]; then
    echo "Executing command: $@"
    exec "$@"
else
    echo "Starting FastAPI server..."
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000
fi
