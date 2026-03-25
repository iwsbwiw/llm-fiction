"""Application configuration loaded from environment variables."""

from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for LLM Fiction."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    llm_provider: Literal["openai", "claude", "deepseek"] = "openai"
    llm_model: str = "gpt-4o-mini"
    chapter_length: int = 2000
    data_dir: str = "data/stories"

    openai_api_key: str | None = None
    openai_base_url: str | None = None
    anthropic_api_key: str | None = None
    deepseek_api_key: str | None = None

    @model_validator(mode="after")
    def validate_provider_key(self) -> "Settings":
        """Require the API key matching the selected provider."""
        key_map = {
            "openai": self.openai_api_key,
            "claude": self.anthropic_api_key,
            "deepseek": self.deepseek_api_key,
        }
        if not key_map.get(self.llm_provider):
            raise ValueError(f"API key required for provider: {self.llm_provider}")
        return self


settings = Settings()
