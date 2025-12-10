from datetime import datetime
import logging


class RateLimitFilter(logging.Filter):
    """Filter to prevent log flooding."""

    def __init__(self, rate: int = 100, period: float = 60.0):
        """Initialize the rate limit filter.

        Args:
        rate: Maximum number of messages
        period: Time period in seconds
        """
        super().__init__()
        self.rate = rate
        self.period = period
        self.allowance = rate
        self.last_check = datetime.now().timestamp()

    def filter(self, record: logging.LogRecord) -> bool:
        """Rate limit log messages."""
        current = datetime.now().timestamp()
        time_passed = current - self.last_check
        self.last_check = current

        self.allowance += time_passed * (self.rate / self.period)
        if self.allowance > self.rate:
            self.allowance = self.rate

        if self.allowance < 1.0:
            return False

        self.allowance -= 1.0
        return True
