import logging
from threading import Lock
from typing import ClassVar

from common.constants import LOG_DIR

from .constants import LogLevel
from .filters import RateLimitFilter, SensitiveDataFilter
from .formatter import ConsoleFormatter, StructuredFormatter
from .rotation import (
    RotationType,
    SizeRotationConfig,
    TimeRotationConfig,
)
from .rotation.base import BaseRotationConfig


class LoggerManager:
    """Centralized logger configuration manager."""

    _configured: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    @classmethod
    def configure(
        cls,
        level: LogLevel | str = LogLevel.INFO,
        rotation_type: RotationType = RotationType.TIME,
        rotation_config: BaseRotationConfig | None = None,
        log_to_console: bool = True,
        log_to_file: bool = True,
        console_colors: bool = True,
        structured_format: bool = False,
        sanitize_sensitive: bool = True,
        rate_limit: bool = False,
    ):
        """Configure the logging system.

        Args:
            level: Minimum log level
            rotation_type: Type of file rotation
            rotation_config: Custom rotation configuration
            log_to_console: Enable console logging
            log_to_file: Enable file logging
            console_colors: Enable colored console output
            structured_format: Use JSON format (for production)
            sanitize_sensitive: Filter sensitive data
            rate_limit: Enable rate limiting to prevent flooding
        """
        if cls._configured:
            logging.info("Logger already configured, skipping reconfiguration")
            return
        if not cls._configured:
            with cls._lock:
                if cls._configured:
                    logging.info("Logger already configured, skipping reconfiguration")
                    return
                # get root logger
                root_logger = logging.getLogger()
                root_logger.setLevel(
                    getattr(logging, level if isinstance(level, str) else level.value)
                )

                # remove existing handlers
                root_logger.handlers.clear()

                # Create formatters
                if structured_format:
                    formatter = StructuredFormatter()
                else:
                    console_fmt = ConsoleFormatter(
                        use_colors=console_colors, include_location=True
                    )
                    file_fmt = StructuredFormatter()

                # Console Handlers
                if log_to_console:
                    console_hander = logging.StreamHandler()
                    console_hander.setLevel(logging.DEBUG)
                    console_hander.setFormatter(
                        console_fmt if not structured_format else formatter
                    )
                    root_logger.addHandler(console_hander)

                # File Handlers
                if log_to_file:
                    # Create rotation config if not provided
                    if rotation_config is None:
                        if rotation_type == RotationType.SIZE:
                            rotation_config = SizeRotationConfig()
                        else:
                            rotation_config = TimeRotationConfig()

                # All logs file
                all_logs_path = LOG_DIR.joinpath("app.log")
                all_handler = rotation_config.create_handler(all_logs_path)
                all_handler.setLevel(logging.DEBUG)
                all_handler.setFormatter(
                    file_fmt if not structured_format else formatter
                )
                root_logger.addHandler(all_handler)

                # Error logs file
                error_logs_path = LOG_DIR.joinpath("error.log")
                error_handler = rotation_config.create_handler(error_logs_path)
                error_handler.setLevel(logging.ERROR)
                error_handler.setFormatter(
                    file_fmt if not structured_format else formatter
                )
                root_logger.addHandler(error_handler)

                if sanitize_sensitive:
                    sensitive_filter = SensitiveDataFilter()
                    for handler in root_logger.handlers:
                        handler.addFilter(sensitive_filter)

                if rate_limit:
                    rate_filter = RateLimitFilter(rate=100, per=60.0)
                    for handler in root_logger.handlers:
                        handler.addFilter(rate_filter)

                cls._configured = True
                logging.info("Logging system configured successfully")

    @classmethod
    def get_logger(cls, name: str | None = None) -> logging.Logger:
        """Get a logger instance.

        Args:
            name: Logger name (typically __name__ of the module)

        Returns:
            Configured logger instance
        """
        if not cls._configured:
            cls.configure()

        return logging.getLogger(name)

    @classmethod
    def reset(cls) -> None:
        """Reset configuration (useful for testing)."""
        with cls._lock:
            root_logger = logging.getLogger()
            root_logger.handlers.clear()
            cls._configured = False


if __name__ == "__main__":

    # Configure logger (do this once at application startup)
    LoggerManager.configure(
        level=LogLevel.DEBUG,
        rotation_type=RotationType.TIME,
        console_colors=True,
        structured_format=False,
        sanitize_sensitive=True,
    )

    # Get logger in your modules
    logger = LoggerManager.get_logger(__name__)

    # Basic logging
    logger.debug("Debug message")
    logger.info("Application started")
    logger.warning("This is a warning")

    # Logging with extra context
    logger.info(
        "User logged in",
        extra={"user_id": 12345, "ip_address": "192.168.1.1", "session_id": "abc123"},
    )

    # Logging sensitive data (will be sanitized)
    logger.info("Login attempt with password=secret123 and token=abc123def")

    # Exception logging
    try:
        result = 1 / 0
    except Exception:
        logger.exception("An error occurred during calculation")

    # Different modules can have their own loggers
    api_logger = LoggerManager.get_logger("api")
    db_logger = LoggerManager.get_logger("database")

    api_logger.info("API request received")
    db_logger.info("Database connection established")
