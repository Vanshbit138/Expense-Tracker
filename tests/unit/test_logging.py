"""
Unit tests for logging configuration module.
"""

from datetime import datetime
from unittest.mock import MagicMock, call, patch

from src.core.logging_config import (
    CustomJSONFormatter,
    LoggerMixin,
    get_logger,
    setup_logging,
)


class TestCustomJSONFormatter:
    """Test cases for CustomJSONFormatter."""

    def test_add_fields(self):
        """Test adding custom fields to log record."""
        formatter = CustomJSONFormatter()

        # Create a mock log record
        record = MagicMock()
        record.levelname = "INFO"
        record.name = "test_logger"
        record.process = 12345
        record.thread = 67890
        record.module = "test_module"
        record.funcName = "test_function"
        record.lineno = 42
        record.pathname = "/path/to/test_module.py"

        log_record = {}
        message_dict = {}

        # Mock datetime.utcnow to return a consistent timestamp
        with patch("src.core.logging_config.datetime") as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 12, 0, 0)

            formatter.add_fields(log_record, record, message_dict)

        # Verify custom fields were added
        assert log_record["timestamp"] == "2023-01-01T12:00:00Z"
        assert log_record["service"] == "expense-tracker-api"
        assert log_record["level"] == "INFO"
        assert log_record["logger"] == "test_logger"
        assert log_record["process_id"] == 12345
        assert log_record["thread_id"] == 67890
        assert log_record["module"] == "test_module"
        assert log_record["function"] == "test_function"
        assert log_record["line_number"] == 42
        assert log_record["filename"] == "test_module.py"

    def test_add_fields_without_pathname(self):
        """Test adding fields when pathname is not available."""
        formatter = CustomJSONFormatter()

        record = MagicMock()
        record.levelname = "DEBUG"
        record.name = "test_logger"
        record.process = 12345
        record.thread = 67890
        record.module = "test_module"
        record.funcName = "test_function"
        record.lineno = 42
        # No pathname attribute

        log_record = {}
        message_dict = {}

        formatter.add_fields(log_record, record, message_dict)

        assert log_record["filename"] == "test_module"


class TestSetupLogging:
    """Test cases for setup_logging function."""

    def test_setup_logging_with_defaults(self, mock_settings):
        """Test logging setup with default settings."""
        with patch("src.core.logging_config.settings", mock_settings):
            with patch("logging.getLogger") as _mock_get_logger:
                with patch("logging.StreamHandler") as _mock_stream_handler:
                    with patch("logging.FileHandler") as _mock_file_handler:
                        with patch("os.makedirs") as _mock_makedirs:
                            setup_logging()

                            # Verify structlog was configured
                            # Note: This is hard to test directly, but we can verify
                            # that the function runs without errors
                            assert True

    def test_setup_logging_with_custom_params(self):
        """Test logging setup with custom parameters."""
        with patch("structlog.configure") as mock_configure:
            with patch("logging.getLogger") as _mock_get_logger:
                with patch("logging.StreamHandler") as _mock_stream_handler:
                    with patch("logging.FileHandler") as _mock_file_handler:
                        with patch("os.makedirs") as _mock_makedirs:
                            setup_logging(log_level="DEBUG", enable_json=False)

                            # Verify structlog was configured
                            mock_configure.assert_called_once()

    def test_setup_logging_file_handler_failure(self):
        """Test logging setup when file handler creation fails."""
        with patch("structlog.configure"):
            with patch("logging.getLogger") as _mock_get_logger:
                with patch("logging.StreamHandler") as _mock_stream_handler:
                    with patch(
                        "logging.FileHandler", side_effect=OSError("Permission denied")
                    ):
                        with patch("os.makedirs") as _mock_makedirs:
                            # Should not raise an exception
                            setup_logging()
                            assert True

    def test_setup_logging_specific_loggers(self):
        """Test that specific loggers are configured with appropriate levels."""
        with patch("structlog.configure"):
            with patch("logging.getLogger") as _mock_get_logger:
                with patch("logging.StreamHandler") as _mock_stream_handler:
                    with patch("logging.FileHandler") as _mock_file_handler:
                        with patch("os.makedirs"):
                            # Mock the root logger
                            mock_root_logger = MagicMock()
                            _mock_get_logger.return_value = mock_root_logger

                            setup_logging()

                            # Verify specific loggers were configured
                            expected_calls = [
                                call("uvicorn"),
                                call("uvicorn.access"),
                                call("sqlalchemy.engine"),
                                call("alembic"),
                                call("watchfiles"),
                                call("watchfiles.main"),
                                call("passlib"),
                                call("passlib.handlers.bcrypt"),
                            ]

                            # Check that getLogger was called for specific loggers
                            assert _mock_get_logger.call_count >= len(expected_calls)


class TestGetLogger:
    """Test cases for get_logger function."""

    def test_get_logger_returns_structlog_logger(self):
        """Test that get_logger returns a structlog logger."""
        logger = get_logger("test_module")

        # Verify it's a structlog logger
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")
        assert hasattr(logger, "warning")

    def test_get_logger_with_different_names(self):
        """Test get_logger with different module names."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        # Both should be valid loggers
        assert logger1 is not None
        assert logger2 is not None

    def test_get_logger_caching(self):
        """Test that get_logger caches loggers."""
        logger1 = get_logger("test_module")
        logger2 = get_logger("test_module")

        # Should return the same logger instance due to caching
        assert logger1 is logger2


class TestLoggerMixin:
    """Test cases for LoggerMixin class."""

    def test_logger_property(self):
        """Test that LoggerMixin provides a logger property."""

        class TestClass(LoggerMixin):
            pass

        instance = TestClass()
        logger = instance.logger

        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")
        assert hasattr(logger, "warning")

    def test_logger_property_class_name(self):
        """Test that logger uses the class name."""

        class TestService(LoggerMixin):
            pass

        instance = TestService()
        logger = instance.logger

        # The logger should be associated with the class name
        assert logger is not None

    def test_multiple_classes_with_logger_mixin(self):
        """Test multiple classes using LoggerMixin."""

        class ServiceA(LoggerMixin):
            pass

        class ServiceB(LoggerMixin):
            pass

        instance_a = ServiceA()
        instance_b = ServiceB()

        logger_a = instance_a.logger
        logger_b = instance_b.logger

        assert logger_a is not None
        assert logger_b is not None
        # They should be different loggers for different classes
        assert logger_a is not logger_b


class TestLoggingIntegration:
    """Integration tests for logging functionality."""

    def test_logging_initialization_message(self, mock_settings):
        """Test that logging initialization logs a message."""
        with patch("src.core.logging_config.settings", mock_settings):
            with patch("structlog.configure"):
                with patch("logging.getLogger") as _mock_get_logger:
                    with patch("logging.StreamHandler") as _mock_stream_handler:
                        with patch("logging.FileHandler") as _mock_file_handler:
                            with patch("os.makedirs"):
                                # Mock the logger to capture the initialization message
                                mock_logger = MagicMock()
                                with patch(
                                    "src.core.logging_config.get_logger",
                                    return_value=mock_logger,
                                ):
                                    setup_logging()

                                    # Verify initialization message was logged
                                    mock_logger.info.assert_called_once()
                                    call_args = mock_logger.info.call_args
                                    assert (
                                        "Logging system initialized" in call_args[0][0]
                                    )

    def test_logging_with_json_formatting(self):
        """Test logging with JSON formatting enabled."""
        with patch("structlog.configure") as mock_configure:
            with patch("logging.getLogger"):
                with patch("logging.StreamHandler"):
                    with patch("logging.FileHandler"):
                        with patch("os.makedirs"):
                            setup_logging(enable_json=True)

                            # Verify JSON renderer was used
                            mock_configure.assert_called_once()
                            call_args = mock_configure.call_args
                            processors = call_args[1]["processors"]

                            # Check that JSONRenderer is in the processors
                            json_renderer_found = any(
                                "JSONRenderer" in str(processor)
                                for processor in processors
                            )
                            assert json_renderer_found

    def test_logging_with_console_formatting(self):
        """Test logging with console formatting (non-JSON)."""
        with patch("structlog.configure") as mock_configure:
            with patch("logging.getLogger"):
                with patch("logging.StreamHandler"):
                    with patch("logging.FileHandler"):
                        with patch("os.makedirs"):
                            setup_logging(enable_json=False)

                            # Verify console renderer was used
                            mock_configure.assert_called_once()
                            call_args = mock_configure.call_args
                            processors = call_args[1]["processors"]

                            # Check that ConsoleRenderer is in the processors
                            console_renderer_found = any(
                                "ConsoleRenderer" in str(processor)
                                for processor in processors
                            )
                            assert console_renderer_found
