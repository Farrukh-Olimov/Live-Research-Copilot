from enum import Enum


class DataSource(str, Enum):
    ARXIV = "arxiv"

    def __str__(self):
        """Return the string."""
        return self.value
