from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    groq_api_key: str = Field(validation_alias="GROQ_API_KEY")
    gemini_api_key: str = Field(validation_alias="GEMINI_API_KEY")
    pinecone_api_key: str= Field(validation_alias="PINECONE_API_KEY")
    pinecone_index_name: str= Field(validation_alias="PINECONE_INDEX_NAME")

    # optional: route youtube_transcript_api requests through a proxy to work
    # around YouTube IP-blocking. Webshare (rotating residential) takes
    # priority if set; otherwise falls back to a generic http/https proxy URL.
    webshare_proxy_username: str | None = Field(default=None, validation_alias="WEBSHARE_PROXY_USERNAME")
    webshare_proxy_password: str | None = Field(default=None, validation_alias="WEBSHARE_PROXY_PASSWORD")
    transcript_proxy_url: str | None = Field(default=None, validation_alias="TRANSCRIPT_PROXY_URL")


settings = Settings()
