from datetime import datetime
import logging


class ConsoleFormatter(logging.Formatter):
    """Human-readable colored formatter for console output."""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"

    def __init__(self, use_colors: bool = True, include_location: bool = True):
        """Initialize the formatter."""
        super().__init__()
        self.use_colors = use_colors
        self.include_location = include_location
        # fmt: off
        self.reserved_attrs = {
            'name', 'msg', 'args', 'created', 'filename', 'funcName', 'levelname',
            'levelno', 'lineno', 'module', 'msecs', 'message', 'pathname', 'process',
            'processName', 'relativeCreated', 'thread', 'threadName', 'exc_info',
            'exc_text', 'stack_info', 'asctime'
        }
        # fmt: on

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors and readable structure."""
        # Get color codes
        color = self.COLORS.get(record.levelname, "") if self.use_colors else ""
        reset = self.RESET if self.use_colors else ""
        bold = self.BOLD if self.use_colors else ""

        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")

        # Build message parts
        parts = [
            f"{timestamp}",
            f"{color}{record.levelname:8}{reset}",
            f"{bold}{record.name}{reset}",
        ]

        if self.include_location:
            parts.append(f"{record.filename}:{record.lineno}")

        parts.append(record.getMessage())

        message = " | ".join(parts)

        # Add extra fields
        extra_fields = []
        for key, value in record.__dict__.items():
            if key not in self.reserved_attrs and not key.startswith("_"):
                extra_fields.append(f"{key}={value}")

        if extra_fields:
            message += " | " + " ".join(extra_fields)

        # Add exception info
        if record.exc_info:
            message += "\n" + "=" * 80
            message += f"\n{color}EXCEPTION{reset}"
            message += "\n" + "=" * 80
            message += "\n" + self.formatException(record.exc_info)

        return message
