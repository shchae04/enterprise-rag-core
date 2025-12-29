@echo off
echo ================================
echo 사내 문서 RAG 백엔드 설정 및 실행
echo ================================
echo.

:: 1. 가상환경 확인
if not exist "venv\" (
    echo [1/5] 가상환경 생성 중...
    python -m venv venv
) else (
    echo [1/5] 가상환경이 이미 존재합니다.
)

:: 2. 가상환경 활성화
echo [2/5] 가상환경 활성화 중...
call venv\Scripts\activate

:: 3. 의존성 설치
echo [3/5] Python 패키지 설치 중...
pip install -r requirements.txt

:: 4. .env 파일 확인
if not exist ".env" (
    echo [4/5] .env 파일을 찾을 수 없습니다.
    echo .env.example을 복사하여 .env 파일을 생성하고 API 키를 입력하세요.
    echo.
    pause
    exit /b 1
) else (
    echo [4/5] .env 파일 확인 완료
)

:: 5. 데이터베이스 초기화
echo [5/5] 데이터베이스 초기화 중...
python database.py

echo.
echo ================================
echo 설정 완료! 서버를 시작합니다...
echo ================================
echo.
echo API 문서: http://localhost:8000/docs
echo.

:: 6. FastAPI 서버 실행
python main.py
