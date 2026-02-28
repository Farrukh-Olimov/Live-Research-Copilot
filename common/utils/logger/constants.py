from enum import Enum
import logging


class LogLevel(int, Enum):
    """Logging levels."""

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class LOG_MODULES(Enum):
    APP = "app"
    AIRFLOW = "airflow"
