"""
Application configuration loaded from environment variables.
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "sqlite+aiosqlite:///./kikulog.db"

    @field_validator("database_url", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None) -> str:
        if not v:
            return "sqlite+aiosqlite:///./kikulog.db"
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        if v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    # Security
    secret_key: str = "change-this"

    # Model / Tinker
    tinker_api_key: str = ""
    tinker_model_id: str = ""
    tinker_endpoint: str = "https://api.thinkingmachines.ai/tinker/v1"
    model_timeout_seconds: int = 30

    # Demo
    demo_mode: bool = False
    demo_rate_limit: int = 20

    # Operational
    work_timezone: str = "Asia/Tokyo"

    # Logging
    log_level: str = "INFO"


settings = Settings()
