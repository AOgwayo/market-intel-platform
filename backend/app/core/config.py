from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    debug: bool = Field(default=False, env="DEBUG")
    secret_key: str = Field(..., env="SECRET_KEY")
    
    # Database Settings
    database_url: str = Field(..., env="DATABASE_URL")
    database_url_test: Optional[str] = Field(None, env="DATABASE_URL_TEST")
    
    # Redis Settings
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Trading Settings
    alpaca_api_key: Optional[str] = Field(None, env="ALPACA_API_KEY")
    alpaca_secret_key: Optional[str] = Field(None, env="ALPACA_SECRET_KEY")
    alpaca_base_url: str = Field(
        default="https://paper-api.alpaca.markets", env="ALPACA_BASE_URL"
    )
    
    # Data Sources
    binance_api_key: Optional[str] = Field(None, env="BINANCE_API_KEY")
    binance_secret_key: Optional[str] = Field(None, env="BINANCE_SECRET_KEY")
    
    # External Services
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()