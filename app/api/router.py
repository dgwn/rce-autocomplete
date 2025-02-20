from fastapi import APIRouter
from app.api.endpoints import completion, chat

api_router = APIRouter()

api_router.include_router(
    completion.router,
    tags=["completion"],
    prefix="/completion",
)

api_router.include_router(
    chat.router,
    tags=["chat"],
    prefix="/chat",
)
