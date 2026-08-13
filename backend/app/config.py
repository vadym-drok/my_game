"""Application configuration loaded from environment variables."""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    day_progress_mode: Literal["reload", "calendar"] = "reload"

    model_config = SettingsConfigDict(extra="ignore")


settings = Settings()
