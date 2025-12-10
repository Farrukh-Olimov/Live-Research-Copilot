from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from .base import BaseRotationConfig


class TimeRotationConfig(BaseModel, BaseRotationConfig):
    """Configuration for time-based log rotation."""

    when: Literal[
        "S", "M", "H", "D", "W0", "W1", "W2", "W3", "W4", "W5", "W6", "midnight"
    ] = Field(
        default="midnight",
        description=(
            "When to rotate: S=seconds, M=minutes, "
            "H=hours, D=days, W0-W6=weekday, midnight"
        ),
    )
    interval: int = Field(
        default=1, ge=1, le=365, description="Interval between rotations"
    )
    backup_count: int = Field(
        default=7, ge=1, le=365, description="Number of backup files to keep"
    )
    at_time: str | None = Field(
        default=None,
        description=(
            "Time of day for rotation (HH:MM:SS format), "
            "only valid with 'midnight' or 'W' when"
        ),
    )

    def validate(self) -> None:
        """Validate configuration parameters."""
        if self.at_time and self.when not in ["midnight"] + [f"W{i}" for i in range(7)]:
            raise ValueError("at_time only valid with 'midnight' or weekday rotation")

    def create_handler(self, filepath: Path) -> TimedRotatingFileHandler:
        """Create a time-based rotating file handler."""
        filepath.parent.mkdir(parents=True, exist_ok=True)

        handler = TimedRotatingFileHandler(
            filename=str(filepath),
            when=self.when,
            interval=self.interval,
            backupCount=self.backup_count,
            encoding="utf-8",
        )
        return handler
