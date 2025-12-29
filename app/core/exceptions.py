from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.logging import logger

class AppError(Exception):
    """애플리케이션 비즈니스 로직 기본 에러"""
    def __init__(self, message: str, code: str = "APP_ERROR"):
        self.message = message
        self.code = code

class ServiceUnavailableError(AppError):
    """외부 서비스(LLM 등) 연동 실패"""
    def __init__(self, message: str = "External service is unavailable"):
        super().__init__(message, "SERVICE_UNAVAILABLE")

async def app_exception_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=400,
        content={"error": {"code": exc.code, "message": exc.message}}
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "HTTP_ERROR", "message": exc.detail}}
    )

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please check the server logs."
            }
        }
    )
