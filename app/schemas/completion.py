from pydantic import BaseModel, Field
from typing import Optional, List

class CompletionRequest(BaseModel):
    text: str = Field(..., description="The text to be completed")
    max_tokens: Optional[int] = Field(100, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(0.8, description="Sampling temperature")
    stream: Optional[bool] = Field(False, description="Whether to stream the response")
    provider: Optional[str] = Field("openai", description="The provider to use for completion")
    model: Optional[str] = Field("gpt-4o-mini", description="The model to use for completion")

# May have to edit
class CompletionResponse(BaseModel):
    completed_text: str
    tokens_used: int