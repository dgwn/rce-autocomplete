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

    def _sys_prompt(self, all_content: str, content_up_until_cursor: str) -> str:
        return (
            f"Take in this html, and autocomplete it. If there seems like a youtube video that could be relevant,"
            f"please use the youtube tool to search for a video. The youtube video will return a few results."
            f"Out of these results, choose the best youtube video and return JUST the link of the video. Absolutely do NOT embed the youtube video in an iFrame,"
            f"or any other way. Just return the link of the video."
            f"DO NOT include ANY other text other than the html that you have completed, youtube or not."
            f"DO NOT include ANY of my html, yours should be a CONTINUATION of mine."
            f"DO NOT include ANY of my html, yours should be a CONTINUATION of mine."
            f"DO NOT include ANY of my html, yours should be a CONTINUATION of mine."
            f"And here is all the content: {all_content}"
            f"This is the html that you have to complete: {content_up_until_cursor}"
        )

    async def complete_text(
        self,
        all_content_in_rce: str,
        content_up_until_cursor: str,
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
                all_content_in_rce=all_content_in_rce,
                content_up_until_cursor=content_up_until_cursor,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=stream,
                model=model,
            )
            return response
        
        if provider == "anthropic":
            print("in anthropic")
            response = await self._complete_text_anthropic_aws(
                all_content_in_rce=all_content_in_rce,
                content_up_until_cursor=content_up_until_cursor,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=stream,
                model=model,
            )
            return response

        return CompletionResponse(suggestion="", tokens_used=0)

    # async def _complete_text_openai(
    #     self, text, max_tokens, temperature, stream, model
    # ) -> CompletionResponse:
    #     if not stream:
    #         response = await self.openai.chat.completions.create(
    #             model=model,
    #             messages=[
    #                 {"role": "system", "content": self._sys_prompt(text)}
    #             ],
    #         )
    #         return {
    #             "completed_text": response.choices[0].message.content,
    #             "tokens_used": response.usage.total_tokens,
    #         }
    #     # TODO: Implement streaming

    #     return CompletionResponse(completed_text="", tokens_used=0)
    
    async def _complete_text_anthropic_aws(self, all_content_in_rce, content_up_until_cursor, max_tokens, temperature, stream, model, tools=anthropic_tools, tool_choice={"type": "any"}) -> CompletionResponse:

        client = AsyncAnthropicBedrock(
            aws_access_key=settings.AWS_ACCESS_KEY_ID,
            aws_secret_key=settings.AWS_SECRET_KEY,
            aws_region=settings.AWS_REGION
        )
        
        text_with_sys_prompt = self._sys_prompt(all_content_in_rce, content_up_until_cursor)
        
        print("tools: ", tools)
        messages = [{"role": "user", "content": text_with_sys_prompt}]
        if tools == []:
            response = await client.messages.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens
            )
            return CompletionResponse(suggestion=response.content[0].text, tokens_used=0)
        else:
            response = await client.messages.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                tools=tools,
                tool_choice=tool_choice
            )
            
            if response.stop_reason == "tool_use":
                print("tool use")
                
                last_content_block = response.content[-1]

                if last_content_block.type == 'tool_use':

                    tool_use_dict = {
                        "id": last_content_block.id,
                        "input": last_content_block.input,
                        "name": last_content_block.name,
                        "type": last_content_block.type
                    }
                    
                    messages.append(
                        {
                            "role": response.role,
                            "content": [tool_use_dict]
                        }
                    )
                    
                    tool_name = last_content_block.name
                    tool_inputs = last_content_block.input
                    tool_id = last_content_block.id
                    if tool_name == "youtube":
                        youtube_res = json.dumps(youtube(tool_inputs["query"]))
                        print(f"called youtube with {tool_inputs['query']}")
                        print(f"youtube_res: {youtube_res}")
                        tool_message = {
                            "role": "user",
                            "content": [{
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "content": youtube_res
                            }]
                        }
                        messages.append(tool_message)
                        for m in messages:
                            print(f"message: {json.dumps(m, indent=4)}")
                        
                        new_response = await client.messages.create(
                            model=model,
                            messages=messages,
                            max_tokens=max_tokens,
                            tools=tools
                        )
                        
                        return CompletionResponse(suggestion=new_response.content[0].text, tokens_used=0)
                    # TODO: process tool response better
            else:
                print("no tool use")
            
        return CompletionResponse("No response", tokens_used=0)
        
    