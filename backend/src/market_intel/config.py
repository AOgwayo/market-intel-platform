from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    polygon_api_key: str | None = Field(default=None, env="POLYGON_API_KEY")
    binance_base_url: str = "https://api.binance.com"
    polygon_base_url: str = "https://api.polygon.io"
    ingestion_bar_interval_seconds: int = 60
    environment: str = "dev"

    class Config:
        case_sensitive = False

settings = Settings()