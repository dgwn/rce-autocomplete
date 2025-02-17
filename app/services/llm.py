from openai import AsyncOpenAI
import os
import asyncio
# from app.core.config import settings
from dotenv import load_dotenv
from app.schemas.completion import CompletionResponse

load_dotenv()

class LLMService:
    def __init__(self):
        self.openai = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def complete_text(
            self, text, max_tokens=100, temperature=0.8, stream=False, provider="openai", model="gpt-4o-mini"
    ) -> CompletionResponse:
        if provider == "openai":
                response = await self.complete_text_openai(
                    text=text, max_tokens=max_tokens, temperature=temperature, stream=stream, model=model
                )

    async def complete_text_openai (
            self, text, max_tokens, temperature, stream, model
    ) -> CompletionResponse:
        if not stream:
             response = await self.openai.chat.completions.create(
                  model=model,

             )
             return {
                    "completed_text": response.choices[0].message.content,
                    "tokens_used": response.usage.total_tokens,
             }
        # TODO: Implement streaming
        

        return CompletionResponse(completed_text="", tokens_used=0)