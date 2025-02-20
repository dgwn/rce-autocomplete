from openai import AsyncOpenAI
from app.core.config import settings
from dotenv import load_dotenv
from app.schemas.completion import CompletionResponse
from app.services.yt import youtube

# import boto3
from anthropic import AsyncAnthropicBedrock
import json

load_dotenv()

anthropic_tools = [
    {
        "name": "youtube",
        "description": "Search for a youtube video",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to search for"
                }
            },
            "required": ["query"]
        }
    }
]

class LLMService:
    def __init__(self):
        self.openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    def _sys_prompt(self, text):
        return (
            f"Please complete this html code and search for a yt video related to programming"
            f"{text}"
        )

    async def complete_text(
        self,
        text,
        max_tokens=100,
        temperature=0.8,
        stream=False,
        provider="anthropic",
        model="us.anthropic.claude-3-5-haiku-20241022-v1:0"
    ) -> CompletionResponse:
        print("in complete_text")
        print("provider: ", provider)
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
            print("in anthropic")
            response = await self._complete_text_anthropic_aws(
                text=text,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=stream,
                model=model,
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
    
    async def _complete_text_anthropic_aws(self, text, max_tokens, temperature, stream, model, tools=anthropic_tools, tool_choice={"type": "any"}) -> CompletionResponse:

        client = AsyncAnthropicBedrock(
            aws_access_key=settings.AWS_ACCESS_KEY_ID,
            aws_secret_key=settings.AWS_SECRET_KEY,
            aws_region=settings.AWS_REGION
        )
        
        print("tools: ", tools)
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
                print("tool use")
                last_content_block = response.content[-1]
                if last_content_block.type == 'tool_use':
                    tool_name = last_content_block.name
                    tool_inputs = last_content_block.input
                    # tool_id = last_content_block.id
                    if tool_name == "youtube":
                        youtube_res = youtube(tool_inputs["query"])
                        print(f"called youtube with {tool_inputs['query']}")
                        return CompletionResponse(youtube_res, tokens_used=0)
                    # TODO: process tool response better
            else:
                print("no tool use")
            
        return CompletionResponse("No response", tokens_used=0)
        
    