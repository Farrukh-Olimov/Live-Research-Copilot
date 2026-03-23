from enum import Enum


class S3Bucket(str, Enum):
    RESEARCH_PAPERS = "research-papers"

    def __str__(self):
        return self.value


class S3Prefix(str, Enum):
    PDF = "pdf"

    def __str__(self):
        return self.value


class S3PrefixConfig(Enum):
    # Bucket, Prefix, Expiration Date
    PAPER_PDF = (S3Bucket.RESEARCH_PAPERS, S3Prefix.PDF, 1)

    @property
    def bucket(self):
        return self.value[0]

    @property
    def prefix(self):
        return self.value[1]

    @property
    def expiration_days(self):
        return self.value[2]

