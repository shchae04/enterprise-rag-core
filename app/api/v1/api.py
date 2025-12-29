from fastapi import APIRouter
from app.api.v1.endpoints import documents, chat, auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

# For Open WebUI compatibility
from app.api.v1.endpoints.chat import list_models
api_router.add_api_route("/models", list_models, methods=["GET"], tags=["models"])
