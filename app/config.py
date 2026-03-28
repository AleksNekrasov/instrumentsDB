from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


"""Файл для импортирования логина и пароля из .env"""

class Settings(BaseSettings):
    database_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()
