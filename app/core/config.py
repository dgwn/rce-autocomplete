from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "RCE Autocomplete"
    API_STR: str = "/api"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    DEFAULT_MODEL: str = "gpt-4o-mini"
    
    class Config:
        env_file = ".env"

settings = Settings()