"""
Application settings for ScrapIt AI Classification Module
"""
import os
from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    
    # OpenAI API settings
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "o1")
    
    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/scrapit")
    
    # Application settings
    app_name: str = "ScrapIt AI Classification"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # API rate limits
    rate_limit_per_minute: int = 60
    
    class Config:
        """Pydantic config"""
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    """Get cached settings"""
    return Settings()