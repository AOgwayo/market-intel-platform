"""Configuration loading and validation for the market intelligence platform.

This module provides centralized configuration management with environment variable
loading, validation, and fail-fast behavior for invalid or missing required values.
"""

import os
from typing import Optional

from pydantic import BaseModel, Field, ValidationError, field_validator


class ConfigError(Exception):
    """Raised when configuration is invalid or missing required values."""
    pass


class Config(BaseModel):
    """Application configuration schema with validation."""
    
    # Environment configuration
    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Database configuration
    db_dsn: str = Field(..., alias="DB_DSN")  # Required field
    
    # Ingestion configuration
    ingest_poll_interval_seconds: int = Field(default=60, alias="INGEST_POLL_INTERVAL_SECONDS")
    ingest_batch_size: int = Field(default=500, alias="INGEST_BATCH_SIZE")
    
    # Retry configuration
    retry_max_attempts: int = Field(default=5, alias="RETRY_MAX_ATTEMPTS")
    retry_base_delay: float = Field(default=0.5, alias="RETRY_BASE_DELAY")
    retry_max_delay: float = Field(default=30.0, alias="RETRY_MAX_DELAY")
    
    # Optional bars configuration
    bars_timeframe_default: Optional[str] = Field(default=None, alias="BARS_TIMEFRAME_DEFAULT")
    
    @field_validator("ingest_poll_interval_seconds")
    @classmethod
    def validate_poll_interval(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("INGEST_POLL_INTERVAL_SECONDS must be > 0")
        return v
    
    @field_validator("ingest_batch_size")
    @classmethod
    def validate_batch_size(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("INGEST_BATCH_SIZE must be > 0")
        return v
    
    @field_validator("retry_max_attempts")
    @classmethod
    def validate_max_attempts(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("RETRY_MAX_ATTEMPTS must be > 0")
        return v
    
    @field_validator("retry_base_delay")
    @classmethod
    def validate_base_delay(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("RETRY_BASE_DELAY must be > 0")
        return v
    
    @field_validator("retry_max_delay")
    @classmethod
    def validate_max_delay(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("RETRY_MAX_DELAY must be > 0")
        return v
    
    def model_post_init(self, __context) -> None:
        """Additional validation after model initialization."""
        if self.retry_max_delay < self.retry_base_delay:
            raise ValueError("RETRY_MAX_DELAY must be >= RETRY_BASE_DELAY")


def load_config() -> Config:
    """Load and validate configuration from environment variables.
    
    Returns:
        Config: Validated configuration instance.
        
    Raises:
        ConfigError: If configuration is invalid or missing required values.
    """
    try:
        # Create config from environment variables
        config = Config(**dict(os.environ))
        return config
    except ValidationError as e:
        # Convert pydantic ValidationError to ConfigError for consistent error handling
        error_messages = []
        for error in e.errors():
            field = error.get("loc", ["unknown"])[0]
            msg = error.get("msg", "validation error")
            error_messages.append(f"{field}: {msg}")
        
        raise ConfigError(f"Configuration validation failed: {'; '.join(error_messages)}")
    except Exception as e:
        raise ConfigError(f"Failed to load configuration: {str(e)}")