from datetime import datetime, timezone
import json
import logging
import traceback


class StructuredFormatter(logging.Formatter):
    """JSON Formatter for logging."""

    def __init__(self, include_extra: bool = True):
        """Initialize the formatter."""
        super().__init__()
        self.include_extra = include_extra
        # fmt: off
        self.reserved_attrs = {
            'name', 'msg', 'args', 'created', 'filename', 'funcName', 'levelname',
            'levelno', 'lineno', 'module', 'msecs', 'message', 'pathname', 'process',
            'processName', 'relativeCreated', 'thread', 'threadName', 'exc_info',
            'exc_text', 'stack_info', 'asctime'
        }
        # fmt: on

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        # Build base structure
        log_data = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "location": {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
            },
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add extra fields
        if self.include_extra:
            extra = {}
            for key, value in record.__dict__.items():
                if key not in self.reserved_attrs and not key.startswith("_"):
                    extra[key] = value

            if extra:
                log_data["extra"] = extra

        return json.dumps(log_data, default=str, ensure_ascii=False)
