# pragma: no cover
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, AsyncIterable, ClassVar, Dict, Generic, Optional, TypeVar
from uuid import UUID
from httpx import AsyncClient

from common.datasources.schema import (
    BasePaperSchema,
    DomainSchema,
    PaperMetadataRecord,
    SubjectSchema,
)

PaperSchemaType = TypeVar("PaperSchemaType", bound=BasePaperSchema)


class CategoryFetcher(ABC):
    TIMEOUT: int = 30

    DATASOURCE_NAME: ClassVar[str]

    def __init__(self, client: AsyncClient, datasource_uuid: UUID):
        """Initialize the category fetcher.

        Args:
            client: The httpx client to use for fetching categories.
            datasource_uuid: The uuid of the datasource.
        """
        self._client = client
        self._datasource_uuid = datasource_uuid

    @abstractmethod
    async def fetch_subjects(self) -> AsyncIterable[SubjectSchema]:
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
    def parse(
        self, raw_data: Any, primary_subject_code: str, domain_code: str
    ) -> PaperSchemaType:
        """Parses raw data from the datasource into a PaperSchemaType object.

        Args:
            raw_data (Any): The raw data to parse.
            primary_subject_code (str): The primary subject code of the record.
            domain_code (str): The domain code of the record.

        Returns:
            PaperSchemaType: The parsed paper metadata object.
        """
        pass

    @abstractmethod
    def get_resumption_token(self, raw_data: str) -> Optional[str]:
        """Extracts the resumption token from an arXiv API response XML.

        Args:
            raw_data (str): The XML text of the arXiv API response.

        Returns:
            Optional[str]: The resumption token if present, otherwise None.
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

    @staticmethod
    @abstractmethod
    def get_domain_code(subject_code: str) -> str:
        """Returns the domain code from a subject code."""
        pass

    @abstractmethod
    async def fetch_paper_metadata(
        self,
        subject_code: str,
        from_date: datetime,
        until_date: datetime,
    ) -> AsyncIterable[PaperSchemaType]:
        """Fetches paper metadata from the datasource.

        Args:
            subject_code (str): The subject code to query.
            from_date (datetime): The from date to query.
            until_date (datetime): The until date to query.

        Returns:
            AsyncIterable[PaperSchemaT]: An asynchronous iterable
                of paper metadata objects.
        """
        pass


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
        self, subject: str, from_date: datetime, until_date: datetime
    ) -> AsyncIterable[PaperMetadataRecord]:
        """Runs the paper metadata ingestion given subject and date range.

        Args:
            subject (str): The subject to ingest.
            from_date (datetime): The from date to ingest.
            until_date (datetime): The until date to ingest.

        Returns:
            AsyncIterable[PaperMetadataRecord]: An asynchronous iterable of
                paper metadata records.
        """
        pass
