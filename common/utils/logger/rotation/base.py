from abc import ABC, abstractmethod
from logging import Handler
from pathlib import Path


class BaseRotationConfig(ABC):
    """Base class for rotation configuration."""

    @abstractmethod
    def create_handler(self, filepath: Path) -> Handler:
        """Create a handler for the given file path."""
        pass

    @abstractmethod
    def validate(self) -> None:
        """Validate configuration parameters."""
        pass
