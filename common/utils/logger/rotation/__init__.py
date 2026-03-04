from enum import Enum

from .size_rotation import SizeRotationConfig
from .time_rotation import TimeRotationConfig


class RotationType(str, Enum):
    """Rotation types."""

    SIZE = "SIZE"
    TIME = "TIME"


__all__ = ["RotationType", "SizeRotationConfig", "TimeRotationConfig"]
