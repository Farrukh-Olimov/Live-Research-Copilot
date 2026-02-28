from enum import Enum


class LogLevel(str, Enum):
    """Logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LOG_MODULES(Enum):
    APP = "app"
    AIRFLOW = "airflow"