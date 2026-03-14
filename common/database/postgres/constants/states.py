from enum import Enum


class PaperProcessingStatus(str, Enum):
    METADATA_INGESTED = "metadata_ingested"

    def __str__(self):
        """Returns the string representation of the paper processing status.

        Returns:
            str: The string representation of the paper processing status.
        """
        return self.value
