from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    environment: str = Field("dev", description="Runtime environment")
    database_url: str = Field("postgresql+psycopg2://postgres:postgres@db:5432/market_intel", alias="DATABASE_URL")
    alpaca_api_key: str | None = Field(None, alias="ALPACA_API_KEY")
    alpaca_api_secret: str | None = Field(None, alias="ALPACA_API_SECRET")
    alpaca_paper: bool = Field(True, alias="ALPACA_PAPER")

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()