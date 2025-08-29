"""Structured logging setup using structlog with JSON output.

This module configures structlog for consistent JSON logging across development
and production environments with proper context processors and formatting.
"""

import logging
import logging.config
import sys
from datetime import datetime
from typing import Any, Dict

import structlog


def add_timestamp(logger: Any, name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add UTC ISO8601 timestamp to log events."""
    event_dict["timestamp"] = datetime.utcnow().isoformat() + "Z"
    return event_dict


def add_env_context(app_env: str):
    """Create a processor that adds environment context to log events."""
    def processor(logger: Any, name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        event_dict["env"] = app_env
        return event_dict
    return processor


def add_component_binding(component: str):
    """Create a processor that adds component binding to log events."""
    def processor(logger: Any, name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        event_dict["component"] = component
        return event_dict
    return processor


def configure_logging(app_env: str = "development", log_level: str = "INFO") -> None:
    """Configure structured logging with JSON output.
    
    Args:
        app_env: Application environment (development, staging, production)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            # Add standard context
            add_timestamp,
            add_env_context(app_env),
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            # JSON renderer for consistent output
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )


def get_logger(component: str = "main") -> structlog.stdlib.BoundLogger:
    """Get a structured logger with component binding.
    
    Args:
        component: Component name to bind to logger (e.g., "ingestion", "config", "retry")
        
    Returns:
        Configured structlog logger with component context
    """
    return structlog.get_logger().bind(component=component)


# Common log events for consistency across the platform
class LogEvents:
    """Standard log event names for consistent logging."""
    
    SERVICE_START = "service_start"
    SERVICE_STOP = "service_stop"
    CONFIG_LOADED = "config_loaded"
    CONFIG_ERROR = "config_error"
    
    RETRY_ATTEMPT = "retry_attempt_fetch"
    RETRY_BACKOFF = "retry_backoff_fetch"
    RETRY_FAILED = "retry_failed"
    
    INGEST_BATCH_START = "ingest_batch_start"
    INGEST_BATCH_SUCCESS = "ingest_batch_success"
    INGEST_BATCH_FAILED = "ingest_batch_failed"
    INGEST_CYCLE_FAILED = "ingest_cycle_failed"
    
    DB_OPERATION_START = "db_operation_start"
    DB_OPERATION_SUCCESS = "db_operation_success"
    DB_OPERATION_FAILED = "db_operation_failed"