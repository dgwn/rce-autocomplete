from openai import AsyncOpenAI
from app.core.config import settings
from dotenv import load_dotenv
from app.schemas.completion import CompletionResponse
from app.schemas.chat import ChatResponse
from app.schemas.transform import TransformResponse
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
            "Complete the following HTML naturally, ensuring clean, accessible, and well-structured formatting. "
            "Do not repeat or modify the given HTML—just extend it logically. "
            "If a relevant YouTube video could enhance the content, use the YouTube tool to search for one. "
            "From the search results, choose the most relevant video and embed it as a clickable thumbnail using this format: "
            '<div style="text-align: center; margin-bottom: 20px;">'
            '<a href="https://www.youtube.com/watch?v=[VIDEO_ID]" target="_blank" rel="noopener noreferrer">'
            '<img src="https://img.youtube.com/vi/[VIDEO_ID]/hqdefault.jpg" '
            'alt="YouTube Video Thumbnail" width="560" height="315" '
            'style="border-radius: 8px; box-shadow: 2px 2px 10px rgba(0,0,0,0.2);">'
            '</a>'
            '</div>. '
            "Ensure that all generated HTML is properly structured using semantic elements where appropriate, "
            "such as <h2> for headings and <p> for paragraphs. "
            "Use spacing and formatting for readability and accessibility. "
            "Return only the completed HTML—do not include any explanations or extra text. "
            f"Here is the HTML to complete: {content_up_until_cursor}"
        )

    def _sys_prompt_chat(self, text):
        return (
            f"You are a chatbot that is responsible for adding text content to educational pages"
            f"The user has asked you to add informative content to the page about the following topic: "
            f"{text}"
            f"Please provide a response that is informative and engaging and return it in HTML format"
            f"Return only the HTML, DO NOT REPLY WITH A PREAMBLE. JUST HTML CONTENT"
        )
    
    def _sys_prompt_translate(self, text):
        return (
            f"Translate the following HTML content into Spanish. Ensure that the translation is accurate and grammatically correct. "
            f"Return only the translated HTML content—do not include any explanations or extra text. "
            f"Here is the HTML to translate: {text}"
        )
    
    def _sys_prompt_concise(self, text):
        return (
            f"Condense the following HTML content into a more concise form while maintaining the original meaning. "
            f"Return only the condensed HTML content—do not include any explanations or extra text. "
            f"Here is the HTML to condense: {text}"
        )
    
    def _sys_prompt_casual(self, text):
        return (
            f"Rewrite the following HTML content in a more casual tone. "
            f"Return only the rewritten HTML content—do not include any explanations or extra text. "
            f"Here is the HTML to rewrite: {text}"
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
    
    async def transform(
        self, text, action, max_tokens=5000, temperature=0, model="us.anthropic.claude-3-5-haiku-20241022-v1:0"
    ) -> TransformResponse:
        if action == "translate":
            response = await self._transform_claude_aws(
                action=action,
                text=text,
                max_tokens=max_tokens,
                temperature=temperature,
                model=model
            )
            return response
        
        if action == "casual":
            response = await self._transform_claude_aws(
                action=action,
                text=text,
                max_tokens=max_tokens,
                temperature=temperature,
                model=model
            )
            return response
        
        if action == "concise":
            response = await self._transform_claude_aws(
                action=action,
                text=text,
                max_tokens=max_tokens,
                temperature=temperature,
                model=model
            )
            return response

        return TransformResponse(transformed_text="")

    async def _transform_claude_aws(
        self, action, text, max_tokens, temperature, model
    ) -> ChatResponse:
        client = AsyncAnthropicBedrock(
            aws_access_key=settings.AWS_ACCESS_KEY_ID,
            aws_secret_key=settings.AWS_SECRET_KEY,
            aws_region=settings.AWS_REGION
        )

        if action == "translate":
            response = await client.messages.create(
                model=model,
                messages=[
                    {"role": "user", "content": self._sys_prompt_translate(text)}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )

        if action == "casual":
            response = await client.messages.create(
                model=model,
                messages=[
                    {"role": "user", "content": self._sys_prompt_casual(text)}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
        
        if action == "concise":
            response = await client.messages.create(
                model=model,
                messages=[
                    {"role": "user", "content": self._sys_prompt_concise(text)}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )

        return TransformResponse(
            transformed_text=response.content[0].text,
        )
    
    async def chat(
        self, text, max_tokens=500, temperature=0, model="us.anthropic.claude-3-5-haiku-20241022-v1:0"
    ) -> ChatResponse:
        response = await self._chat_anthropic_aws(
            text=text,
            max_tokens=max_tokens,
            temperature=temperature,
            model=model
        )

        return response


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
    
    async def _chat_anthropic_aws(
            self, text, max_tokens, temperature, model
    ) -> ChatResponse:
        client = AsyncAnthropicBedrock(
            aws_access_key=settings.AWS_ACCESS_KEY_ID,
            aws_secret_key=settings.AWS_SECRET_KEY,
            aws_region=settings.AWS_REGION
        )

        response = await client.messages.create(
            model=model,
            messages=[
                {"role": "user", "content": self._sys_prompt_chat(text)}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )

        print(type(response.content[0].text))

        return ChatResponse(
            html=response.content[0].text,
        )
    
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
            
        return CompletionResponse(completed_text="No response", tokens_used=0)
        
    
    async def _let_llm_choose_youtube_video(self, query):
        return youtube(query)
