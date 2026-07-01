from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    service_key: str = Field(default="", alias="SERVICE_KEY")
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5433/complaint_service",
        alias="DATABASE_URL"
    )
    public_api_base: str = "https://apis.data.go.kr/B551982/cso_v2"
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    kakao_rest_key: str = Field(default="", alias="KAKAO_REST_KEY")
    vite_kakao_maps_key: str = Field(default="", alias="VITE_KAKAO_MAPS_KEY")
    frontend_url: str = Field(default="", alias="FRONTEND_URL")  # Vercel 프론트엔드 URL (CORS용)

    @field_validator("database_url", mode="before")
    @classmethod
    def fix_database_url(cls, v: str) -> str:
        if isinstance(v, str) and v.startswith("postgresql://") and "+asyncpg" not in v:
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @property
    def kakao_key(self) -> str:
        """KAKAO_REST_KEY 우선, 없으면 VITE_KAKAO_MAPS_KEY 사용"""
        return self.kakao_rest_key or self.vite_kakao_maps_key

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


settings = Settings()