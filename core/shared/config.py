from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "portfolio-site"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # LLM
    default_llm_provider: str = "gemini"
    default_model: str = "gemini-2.5-flash"
    google_api_key: str = ""
    gemini_api_key: str = ""

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


settings = Settings()
