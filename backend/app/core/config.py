import os
from dotenv import load_dotenv
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator
load_dotenv()

class Settings(BaseSettings):
    LLM_API_KEY: str = ""
    LLM_PROVIDER: str  = "ollama"
    EMBEDDING_MODEL: str ="sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSIONS: int = 384
    POSTGRES_DB: str = ""
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str= ""
    POSTGRES_HOST: str= ""
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


    API_PREFIX: str= "/api/v1"
    SECRET_KEY: str
    DEBUG: bool =False



    # @field_validator("ALLOWED_ORIGINS")
    # def validate_allowed_origins(cls, v: str) -> List[str]:
    #     return [origin.strip() for origin in v.split(",")] if v else []

    

settings = Settings()