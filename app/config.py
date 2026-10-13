from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    gemini_api_key: str | None = None
    openai_api_key: str | None = None
    llm_provider: str = "gemini"
    llm_model: str = "gemini-2.5-flash"
    database_path: str = "store.db"
    max_retries: int = 3

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()