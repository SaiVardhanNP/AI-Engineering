from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    groq_api_key: str = Field(validation_alias="GROQ_API_KEY")
    gemini_api_key: str = Field(validation_alias="GEMINI_API_KEY")


settings = Settings()
