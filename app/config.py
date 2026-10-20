"""
Application configuration loaded from environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/kikulog"

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
