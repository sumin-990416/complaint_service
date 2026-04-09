from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    service_key: str = ""
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/complaint_service"
    public_api_base: str = "https://apis.data.go.kr/B551982/cso_v2"
    openrouter_api_key: str = ""
    kakao_rest_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


@field_validator("database_url", mode="before")
@classmethod
def fix_database_url(cls, v: str) -> str:
    if v.startswith("postgresql://") and "+asyncpg" not in v:
        v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
    return v