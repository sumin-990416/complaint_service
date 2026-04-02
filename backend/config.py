from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_key: str = ""
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/complaint_service"
    public_api_base: str = "https://apis.data.go.kr/B551982/cso_v2"
    openrouter_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
