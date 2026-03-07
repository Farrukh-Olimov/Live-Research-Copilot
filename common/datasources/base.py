# pragma: no cover
from abc import ABC, abstractmethod
from datetime import datetime
from typing import (
    Any,
    AsyncIterator,
    ClassVar,
    Dict,
    Generic,
    List,
    TypeVar,
)
from uuid import UUID

from httpx import AsyncClient

from common.datasources.schema import (
    BasePaperSchema,
    DomainSchema,
    PaperMetadataRecord,
    SubjectSchema,
)

PaperSchemaType = TypeVar("PaperSchemaType", bound=BasePaperSchema)


class SubjectsFetcher(ABC):
    TIMEOUT: int = 30

    DATASOURCE_NAME: ClassVar[str]

    def __init__(self, client: AsyncClient, datasource_uuid: UUID):
        """Initialize the subjects fetcher.

        Args:
            client: The httpx client to use for fetching categories.
            datasource_uuid: The uuid of the datasource.
        """
        self._client = client
        self._datasource_uuid = datasource_uuid

    @abstractmethod
    async def fetch_subjects(self) -> AsyncIterator[SubjectSchema]:
        """Return all subjects supported by the datasource."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _parse_set(
        set_spec: str, set_name: str, domains: Dict[str, DomainSchema]
    ) -> SubjectSchema:
        """Parse a single set specification into a SubjectSchema object."""
        raise NotImplementedError


class PaperMetadataParser(Generic[PaperSchemaType], ABC):
    DATASOURCE_NAME: ClassVar[str]

    @abstractmethod
    def get_max_records(self, raw_data: str) -> int:
        """Gets the maximum number of records from an API response XML.

        Args:
            raw_data (str): The XML text of the API response.

        Returns:
            int: The maximum number of records in the API response.
        """
        pass

    @abstractmethod
    def parse(self, raw_data: Any, domain_code: str) -> List[PaperSchemaType]:
        """Parses raw data from the datasource into a PaperSchemaType object.

        Args:
            raw_data (Any): The raw data to parse.
            domain_code (str): The domain code of the record.

        Returns:
            PaperSchemaType: The parsed paper metadata object.
        """
        pass


class PaperMetadataNormalizer(Generic[PaperSchemaType], ABC):
    DATASOURCE_NAME: ClassVar[str]

    @abstractmethod
    def normalize(self, paper_record: PaperSchemaType) -> PaperMetadataRecord:
        """Normalizes a datasource paper metadata object into a PaperMetadataRecord.

        Args:
            paper_record (PaperSchemaType): The paper metadata object to normalize.

        Returns:
            PaperMetadataRecord: The normalized paper metadata object.
        """
        pass


class PaperMetadataFetcher(Generic[PaperSchemaType], ABC):
    TIMEOUT: int = 30
    RETRIES: int = 3
    DELAY: int = 3

    DATASOURCE_NAME: ClassVar[str]

    def __init__(
        self,
        client: AsyncClient,
        paper_parser: PaperMetadataParser[PaperSchemaType],
    ):
        """Initialize the category fetcher.

        Args:
            client: The httpx client to use for fetching categories.
            paper_parser: The paper parser to use for parsing paper metadata.
        """
        self._client = client
        self._paper_parser = paper_parser

    @abstractmethod
    async def fetch_paper_metadata(
        self,
        domain_code: str,
        subject_code: str,
        from_date: datetime,
        until_date: datetime,
    ) -> AsyncIterator[PaperSchemaType]:
        """Fetches paper metadata from the datasource.

        Args:
            domain_code (str): The domain code to query.
            subject_code (str): The subject code to query.
            from_date (datetime): The from date to query.
            until_date (datetime): The until date to query.

        Returns:
            AsyncIterator[PaperSchemaT]: An asynchronous iterator
                of paper metadata objects.
        """
        yield PaperSchemaType


class PaperMetadataIngestion(Generic[PaperSchemaType], ABC):
    def __init__(
        self,
        fetcher: PaperMetadataFetcher[PaperSchemaType],
        normalizer: PaperMetadataNormalizer[PaperSchemaType],
    ):
        """Initializes the paper metadata ingestion process.

        Args:
            fetcher (PaperMetadataFetcher): The paper metadata fetcher to use.
            normalizer (PaperMetadataNormalizer): The paper metadata normalizer to use.
        """
        self._fetcher = fetcher
        self._normalizer = normalizer

    @abstractmethod
    async def run(
        self, domain_code: str, subject: str, from_date: datetime, until_date: datetime
    ) -> AsyncIterator[PaperMetadataRecord]:
        """Runs the paper metadata ingestion given subject and date range.

        Args:
            domain_code (str): The domain_code to ingest.
            subject (str): The subject to ingest.
            from_date (datetime): The from date to ingest.
            until_date (datetime): The until date to ingest.

        Returns:
            AsyncIterable[PaperMetadataRecord]: An asynchronous iterable of
                paper metadata records.
        """
        pass
