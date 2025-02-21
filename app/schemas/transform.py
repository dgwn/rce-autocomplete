from pydantic import BaseModel


class TransformRequest(BaseModel):
    text: str
    action: str


class TransformResponse(BaseModel):
    transformed_text: str
