from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    gemini_api_key: str = Field(validation_alias="GEMINI_API_KEY")
    groq_api_key: str = Field(validation_alias="GROQ_API_KEY")
    # which model powers the CrewAI agents: "groq" or "gemini"
    agent_llm: str = Field(default="gemini", validation_alias="AGENT_LLM")
    pinecone_api_key: str = Field(validation_alias="PINECONE_API_KEY")
    # comma separated list of frontend origins allowed to call this API
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173",
        validation_alias="CORS_ORIGINS",
    )
    pinecone_index_name: str = Field(validation_alias="PINECONE_INDEX_NAME")


settings = Settings()
