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

    # Validate log level
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level.upper() not in valid_levels:
        print(f"Warning: Invalid log level '{log_level}'. Using 'INFO' instead.")
        log_level = "INFO"
    else:
        log_level = log_level.upper()

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

    # Remove existing handlers first
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set the root logger level
    root_logger.setLevel(getattr(logging, log_level))

    # Create console handler with dynamic level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))

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
        file_handler.setLevel(getattr(logging, log_level))

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

    # Configure specific loggers to use root logger handlers
    # This ensures all logs go through our custom formatters
    third_party_loggers = [
        "uvicorn",
        "uvicorn.access",
        "sqlalchemy.engine",
        "alembic",
        "watchfiles",
        "watchfiles.main",
        "passlib",
        "passlib.handlers.bcrypt",
    ]

    for logger_name in third_party_loggers:
        logger = logging.getLogger(logger_name)
        logger.handlers = []  # Remove existing handlers
        logger.propagate = True  # Use root logger handlers
        # Let them inherit the root logger level

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


def update_log_level(new_level: str) -> None:
    """Update the log level for all loggers dynamically."""
    # Validate log level
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if new_level.upper() not in valid_levels:
        print(f"Warning: Invalid log level '{new_level}'. Using 'INFO' instead.")
        new_level = "INFO"
    else:
        new_level = new_level.upper()

    # Update root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, new_level))

    # Update all handlers
    for handler in root_logger.handlers:
        handler.setLevel(getattr(logging, new_level))

    # Update specific loggers
    loggers_to_update = [
        "uvicorn",
        "uvicorn.access",
        "sqlalchemy.engine",
        "alembic",
        "watchfiles",
        "watchfiles.main",
        "passlib",
        "passlib.handlers.bcrypt",
    ]

    for logger_name in loggers_to_update:
        logger = logging.getLogger(logger_name)
        if logger_name in [
            "sqlalchemy.engine",
            "watchfiles",
            "watchfiles.main",
            "passlib",
            "passlib.handlers.bcrypt",
        ]:
            # These should be more restrictive
            logger.setLevel(max(getattr(logging, new_level), logging.WARNING))
        else:
            # These can follow the main level but not go below INFO
            logger.setLevel(max(getattr(logging, new_level), logging.INFO))

    # Log the change
    logger = get_logger(__name__)
    logger.info(f"Log level updated to {new_level}")


def get_current_log_level() -> str:
    """Get the current log level of the root logger."""
    root_logger = logging.getLogger()
    level_name = logging.getLevelName(root_logger.level)
    return level_name


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""

    @property
    def logger(self) -> structlog.BoundLogger:
        """Get logger for this class."""
        return get_logger(self.__class__.__name__)


# Global logger instance
logger = get_logger(__name__)
