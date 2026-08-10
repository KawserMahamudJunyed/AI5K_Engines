"""Configuration settings for the application."""

from pathlib import Path
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["AppSettings", "settings"]

class AppSettings(BaseSettings):
    """Application settings using Pydantic."""

    app_name: str = "AI5K"
    debug: bool = True
    database_url: str = "sqlite+aiosqlite:///./ai5k.db"
    echo_sql: bool = False
    llm_provider_url: str = "http://localhost:11434/v1"
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.1
    groq_api_key: SecretStr = SecretStr("")
    groq_model: str = "llama-3.3-70b-versatile"

    # Security (Defaults for MVP)
    secret_key: str = "super-secret-key-for-ai5k-local-dev-only"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = AppSettings()