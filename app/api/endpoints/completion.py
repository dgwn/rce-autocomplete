from fastapi import APIRouter
from app.schemas.completion import (
    DummyCompletionRequest,
    CompletionRequest,
    DummyCompletionResponse,
    CompletionResponse,
)
from app.services.llm import LLMService

router = APIRouter()
llm_service = LLMService()


@router.post("/complete", response_model=CompletionResponse)
async def complete_text(request: CompletionRequest):
    if not request.content_up_until_cursor.strip() or not request.all_content_in_rce.strip():
        return CompletionResponse(suggestion="", tokens_used=0)

    result = await llm_service.complete_text(
        content_up_until_cursor=request.content_up_until_cursor,
        all_content_in_rce=request.all_content_in_rce,
        max_tokens=1000,
        temperature=request.temperature,
        stream=request.stream,
        provider=request.provider,
        model=request.model,
    )

    return result


@router.post("/dummy-complete", response_model=DummyCompletionResponse)
async def dummy_complete(request: DummyCompletionRequest):
    if not request.content_up_until_cursor.strip():
        return DummyCompletionResponse(html="")

    return DummyCompletionResponse(
        suggestion="""<h1> Hello Danny G you silly billy </h1><iframe width="560" height="315" src="https://www.youtube.com/embed/T6HDVVWan_A?si=7O06s78s1q5kMOiU" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>"""
    )
