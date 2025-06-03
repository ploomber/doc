from enum import Enum
from typing import Literal
from fastapi import Request
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.services.ai_provider import AIProvider

class Profile(str, Enum):
    """Application deployment profiles"""
    TEST = "TEST"
    DEV = "DEV"
    PROD = "PROD"

type SupportEngine = Literal['sqlite', 'postgresql']

class Settings(BaseSettings):
    """
    Application configuration settings
    Loads from environment variables with automatic type conversion
    """
    PROFILE: Profile = Profile.DEV
    VERSION: str = f"local"
    
    ALLOWED_ORIGINS: list[str] = [
        "*"
    ]

    # Application Settings
    DEBUG: bool = False
    
    # Logging Configuration
    LOG_LEVEL: str = "DEBUG"

    # # OpenAI
    # MODEL_PROVIDER: AIProvider = AIProvider.OPENAI

    # # Anthropic
    # MODEL_PROVIDER: AIProvider = AIProvider.CLAUDE

    # Google
    MODEL_PROVIDER: AIProvider = AIProvider.GEMINI
    MODEL_API_KEY: str = ""
    MODEL_NAME: str = "gemini-2.0-flash"

    @field_validator('MODEL_API_KEY')
    def validate_openai_api_key(cls, v: str):
        if not v:
            print("ERROR - Settings.py - Aborting the launching procedure")
            print("-> MODEL_API_KEY cannot be empty")
            print("-> export MODEL_API_KEY={your-key}")
            raise ValueError("MODEL_API_KEY cannot be empty. Set it using: export MODEL_API_KEY={your-key}")
        return v

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if 'MODEL_PROVIDER' in kwargs:
            self.MODEL_PROVIDER = kwargs['MODEL_PROVIDER']

        # Set MODEL_NAME based on MODEL_PROVIDER
        if self.MODEL_PROVIDER == AIProvider.OPENAI:
            self.MODEL_NAME = "gpt-4-turbo-preview"
        elif self.MODEL_PROVIDER == AIProvider.CLAUDE:
            self.MODEL_NAME = "claude-3-opus-20240229"
        elif self.MODEL_PROVIDER == AIProvider.GEMINI:
            self.MODEL_NAME = "gemini-2.0-flash"


    # Allow environment variable overrides
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

async def get_settings(request: Request) -> Settings:
    return request.app.state.settings

