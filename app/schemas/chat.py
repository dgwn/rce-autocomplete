from pydantic import BaseModel


class ChatRequest(BaseModel):
    userInput: str
    editorContent: str


class ChatResponse(BaseModel):
    html: str
