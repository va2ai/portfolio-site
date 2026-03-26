from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ai-agent-platform"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai-agent-platform"
    redis_url: str = "redis://localhost:6379/0"

    # LLM
    default_llm_provider: str = "gemini"
    default_model: str = "gemini-3.1-pro-preview"
    google_api_key: str = ""
    gemini_api_key: str = ""

    # Tools
    tavily_api_key: str = ""
    exa_api_key: str = ""
    reddit_client_id: str = ""
    reddit_client_secret: str = ""

    # Vector DB
    pgvector_connection: str = ""

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


settings = Settings()
