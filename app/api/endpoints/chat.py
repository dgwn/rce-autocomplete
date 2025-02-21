# FILE: app/api/endpoints/chat.py
from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm import LLMService

router = APIRouter()
llm_service = LLMService()  

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    result = await llm_service.chat(request.userInput)

    return result
