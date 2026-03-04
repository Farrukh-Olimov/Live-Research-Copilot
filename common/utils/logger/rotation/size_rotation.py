from logging.handlers import RotatingFileHandler
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from common.constants.size import DataSize

from .base import BaseRotationConfig


class SizeRotationConfig(BaseModel, BaseRotationConfig):
    max_bytes: int = Field(
        default=10 * DataSize.MegaByte,
        description="Maximum size of the log file in bytes",
    )
    backup_count: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of backup files to keep",
    )

    @field_validator("max_bytes")
    @classmethod
    def validate_max_bytes(cls, value: int) -> int:
        """Validate that the maximum size of the log file.

        Raises:
            ValueError: If max_bytes is less than 1 KB or greater than 100 MB.
        """
        if value < DataSize.KiloByte:
            raise ValueError("max_bytes must be at least 1 KB")
        if value > 100 * DataSize.MegaByte:
            raise ValueError("max_bytes must not exceed 100 MB")
        return value

    def validate(self) -> None:
        """Validate configuration."""
        # Pydantic handles validation automatically
        pass

    def create_handler(self, filepath: Path) -> RotatingFileHandler:
        """Create a rotating file handler based on size."""
        filepath.parent.mkdir(parents=True, exist_ok=True)

        handler = RotatingFileHandler(
            filename=str(filepath),
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding="utf-8",
        )
        return handler
