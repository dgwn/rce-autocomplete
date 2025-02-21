from fastapi import APIRouter
from app.schemas.transform import TransformRequest, TransformResponse
from app.services.llm import LLMService

router = APIRouter()
llm_service = LLMService()  

@router.post("/", response_model=TransformResponse)
async def transform(request: TransformRequest):
    # translate, casual, concise
    print(request.text)

    result = await llm_service.transform(request.text, request.action)

    return result
