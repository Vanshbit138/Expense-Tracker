"""
Structured logging configuration for the Expense Tracker API.
"""

import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict

import structlog
from pythonjsonlogger import jsonlogger

from src.core.config import settings


class CustomJSONFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields."""

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)

        # Add timestamp
        log_record["timestamp"] = datetime.utcnow().isoformat() + "Z"

        # Add service name
        log_record["service"] = "expense-tracker-api"

        # Add log level
        log_record["level"] = record.levelname

        # Add logger name
        log_record["logger"] = record.name

        # Add process and thread info
        log_record["process_id"] = record.process
        log_record["thread_id"] = record.thread

        # Add module and function info
        log_record["module"] = record.module
        log_record["function"] = record.funcName
        log_record["line_number"] = record.lineno

        # Add filename (extract from path)
        if hasattr(record, "pathname"):
            log_record["filename"] = os.path.basename(record.pathname)
        else:
            log_record["filename"] = record.module


def setup_logging(log_level: str = None, enable_json: bool = None) -> None:
    """Set up structured logging configuration based on environment settings."""

    # Use settings if not provided
    if log_level is None:
        log_level = settings.log_level
    if enable_json is None:
        enable_json = settings.enable_json_logging

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            (
                structlog.processors.JSONRenderer()
                if enable_json
                else structlog.dev.ConsoleRenderer()
            ),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure root logger with dynamic level
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler with dynamic level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))

    if enable_json:
        # Use JSON formatter
        json_formatter = CustomJSONFormatter(
            "%(timestamp)s %(level)s %(logger)s %(module)s %(function)s %(line_number)s %(message)s"
        )
        console_handler.setFormatter(json_formatter)
    else:
        # Use simple formatter for development
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s:%(lineno)d - %(message)s"
        )
        console_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)

    # Create file handler for persistent logs with dynamic level
    try:
        # Ensure logs directory exists
        os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)

        file_handler = logging.FileHandler(settings.log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))

        if enable_json:
            file_formatter = CustomJSONFormatter(
                "%(timestamp)s %(level)s %(logger)s %(module)s %(function)s %(line_number)s %(message)s"
            )
        else:
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s:%(lineno)d - %(message)s"
            )

        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    except Exception as e:
        # If file logging fails, continue with console logging only
        print(f"Warning: Could not set up file logging: {e}")

    # Configure specific loggers with appropriate levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.INFO)

    # Suppress noisy file watcher logs
    logging.getLogger("watchfiles").setLevel(logging.WARNING)
    logging.getLogger("watchfiles.main").setLevel(logging.WARNING)

    # Suppress passlib warnings
    logging.getLogger("passlib").setLevel(logging.WARNING)
    logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.WARNING)

    # Log the initialization
    logger = get_logger(__name__)
    logger.info(
        "Logging system initialized",
        log_level=log_level,
        json_logging=enable_json,
        log_file=settings.log_file,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""

    @property
    def logger(self) -> structlog.BoundLogger:
        """Get logger for this class."""
        return get_logger(self.__class__.__name__)


# Global logger instance
logger = get_logger(__name__)
