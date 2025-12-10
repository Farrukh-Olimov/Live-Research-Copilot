import logging
import re


class SensitiveDataFilter(logging.Filter):
    """Filter to sanitize sensitive information from logs."""

    PATTERNS = [
        (
            re.compile(r'password["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', re.IGNORECASE),
            "password=***",
        ),
        (
            re.compile(r'token["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', re.IGNORECASE),
            "token=***",
        ),
        (
            re.compile(
                r'api[_-]?key["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', re.IGNORECASE
            ),
            "api_key=***",
        ),
        (
            re.compile(r'secret["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', re.IGNORECASE),
            "secret=***",
        ),
        # Credit cards
        (
            re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),
            "****-****-****-****",
        ),
        # Emails (optional)
        (
            re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            "***@***.***",
        ),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """Sanitize sensitive data from log message."""
        if isinstance(record.msg, str):
            for pattern, replacement in self.PATTERNS:
                record.msg = pattern.sub(replacement, record.msg)
        return True
