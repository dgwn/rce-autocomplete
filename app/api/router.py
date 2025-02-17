from fastapi import APIRouter
from app.api.endpoints import completion

api_router = APIRouter()

api_router.include_router(completion.router, tags=["completion"], prefix="/completion")