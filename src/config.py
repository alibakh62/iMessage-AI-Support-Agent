"""
Configuration management for the iMessage AI Support Agent.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    imessage_api_key: Optional[str] = Field(None, env="IMESSAGE_API_KEY")

    # Database
    database_url: str = Field("sqlite:///conversations.db", env="DATABASE_URL")

    # Application Settings
    log_level: str = Field("INFO", env="LOG_LEVEL")
    debug: bool = Field(False, env="DEBUG")
    environment: str = Field("development", env="ENVIRONMENT")

    # Server Settings
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")

    # LangChain Settings
    langchain_tracing_v2: bool = Field(True, env="LANGCHAIN_TRACING_V2")
    langchain_endpoint: Optional[str] = Field(None, env="LANGCHAIN_ENDPOINT")
    langchain_api_key: Optional[str] = Field(None, env="LANGCHAIN_API_KEY")
    langchain_project: str = Field("imessage-ai-agent", env="LANGCHAIN_PROJECT")

    # iMessage Integration
    imessage_server_url: Optional[str] = Field(None, env="IMESSAGE_SERVER_URL")
    imessage_webhook_secret: Optional[str] = Field(None, env="IMESSAGE_WEBHOOK_SECRET")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings
