from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from typing import Optional

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "RCE Autocomplete"
    API_STR: str = "/api"
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    DEFAULT_MODEL: str = "gpt-4o-mini"
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_KEY: str = os.getenv("AWS_SECRET_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION")
    
    class Config:
        env_file = ".env"

settings = Settings()