from openai import AsyncOpenAI
from app.core.config import settings
from dotenv import load_dotenv
from app.schemas.completion import CompletionResponse

# import boto3
from anthropic import AsyncAnthropicBedrock
import json

load_dotenv()


class LLMService:
    def __init__(self):
        self.openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    def _sys_prompt(self, text):
        return (
            f"Please complete this html code and don't say anything else:"
            f"{text}"
        )

    async def complete_text(
        self,
        text,
        max_tokens=100,
        temperature=0.8,
        stream=False,
        provider="aws",
        model="anthropic.claude-3-haiku-20240307-v1:0",
        tools: dict = None,
    ) -> CompletionResponse:
        if provider == "openai":
            response = await self._complete_text_openai(
                text=text,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=stream,
                model=model,
            )
            return response
        
        if provider == "anthropic":
            response = await self._complete_text_anthropic_aws(
                text=text,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=stream,
                model=model,
                tools=tools,
            )
            return response

        return CompletionResponse(completed_text="", tokens_used=0)

    async def _complete_text_openai(
        self, text, max_tokens, temperature, stream, model
    ) -> CompletionResponse:
        if not stream:
            response = await self.openai.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": self._sys_prompt(text)}
                ],
            )
            return {
                "completed_text": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
            }
        # TODO: Implement streaming

        return CompletionResponse(completed_text="", tokens_used=0)
    
    async def _complete_text_anthropic_aws(self, text, max_tokens, temperature, stream, model, tools, tool_choice={"type": "auto"}) -> CompletionResponse:

        client = AsyncAnthropicBedrock(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
            region_name=settings.AWS_REGION
        )
        
        if tools == []:
            response = await client.messages.create(
                model=model,
                messages=[
                    {"role": "user", "content": text},
                ],
                max_tokens=max_tokens
            )
            return CompletionResponse(response.content[0].text, tokens_used=0)
        else:
            response = await client.messages.create(
                model=model,
                messages=[{"role": "user", "content": text}],
                max_tokens=max_tokens,
                tools=tools,
                tool_choice=tool_choice
            )
            
            if response.stop_reason == "tool_use":
                last_content_block = response.content[-1]
                if last_content_block.type == 'tool_use':
                    tool_name = last_content_block.name
                    tool_inputs = last_content_block.inputs
                    # tool_id = last_content_block.id
                    if tool_name == "youtube":
                        youtube_res = youtube(tool_inputs["text"])
        
    