from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Sistema Pokedex Digital"
    app_version: str = "2.0.0"
    database_url: str = "sqlite:///./pokedex.db"
    secret_key: str = Field(
        default="dev-only-change-this-secret-key-1",
        min_length=32,
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=60, gt=0)
    pokeapi_base_url: str = "https://pokeapi.co/api/v2"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()