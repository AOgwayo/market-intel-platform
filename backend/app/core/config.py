from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/market_intel"
    
    # API Keys
    polygon_api_key: str = ""
    
    # Ingestion Configuration
    ingest_equity_symbols: str = "AAPL,MSFT,TSLA,GOOGL,AMZN"
    
    # Binance Configuration  
    binance_base_url: str = "wss://stream.binance.com:9443/ws/"
    binance_default_symbol: str = "BTCUSDT"
    
    # Application Settings
    debug: bool = False
    log_level: str = "INFO"
    
    @property
    def equity_symbols_list(self) -> List[str]:
        """Convert comma-separated symbols to list."""
        return [s.strip().upper() for s in self.ingest_equity_symbols.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()