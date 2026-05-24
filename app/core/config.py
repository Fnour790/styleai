from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = "postgresql://styleai:styleai@localhost:5432/styleai"

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "wardrobe_items"

    # Anthropic
    anthropic_api_key: str = ""

    # HuggingFace
    hf_token: str = ""

    # App
    app_env: str = "development"
    secret_key: str = "change-this-in-production"
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 10

    # Weather
    weather_cache_ttl_seconds: int = 1800

    @property
    def is_dev(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
