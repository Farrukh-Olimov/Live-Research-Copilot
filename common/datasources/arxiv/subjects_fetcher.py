from typing import AsyncIterator, ClassVar, Dict, Optional
import xml.etree.ElementTree as ET

from common.datasources.arxiv.const import CATEGORY_NAMESPACE, DATASOURCE_NAME
from common.datasources.base import SubjectsFetcher
from common.datasources.schema import DomainSchema, SubjectSchema
from common.utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class ArxivSubjectsFetcher(SubjectsFetcher):
    DATASOURCE_NAME: ClassVar[str] = DATASOURCE_NAME

    PARAMS = {"verb": "ListSets"}
    TIMEOUT = 30
    URL = "https://oaipmh.arxiv.org/oai"

    async def fetch_subjects(self) -> AsyncIterator[SubjectSchema]:
        """Fetches all subjects supported by the arXiv datasource.

        Yields an asynchronous iterable of SubjectSchema objects,
        each representing a subject supported by arXiv.

        Returns:
            AsyncIterator[SubjectSchema]: An asynchronous iterator
                of all subjects supported by arXiv.
        """
        logger.info("Fetching categories from arXiv")
        all_domains: Dict[str, DomainSchema] = {}
        subject_counts = 0

        response = await self._client.get(
            self.URL, params=self.PARAMS, timeout=self.TIMEOUT
        )
        response.raise_for_status()

        xml_bytes = await response.aread()

        root = ET.fromstring(xml_bytes)
        for set_el in root.findall(".//oai:set", CATEGORY_NAMESPACE):
            set_spec = (
                set_el.find("oai:setSpec", CATEGORY_NAMESPACE).text.strip().lower()
            )
            set_name = set_el.find("oai:setName", CATEGORY_NAMESPACE).text
            subject = self._parse_set(set_spec, set_name, all_domains)
            if subject:
                subject_counts += 1
                yield subject

        logger.info(
            "Fetched arXiv categories",
            extra={
                "domains": len(all_domains),
                "subjects": subject_counts,
            },
        )

    def _parse_set(
        self, set_spec: str, set_name: str, domains: Dict[str, DomainSchema]
    ) -> Optional[SubjectSchema]:
        """Parse a single set specification from arXiv into a SubjectSchema.

        Args:
            set_spec (str): The set specification from arXiv.
            set_name (str): The name of the set.
            domains (Dict[str, DomainSchema]): A dictionary of domains.

        Returns:
            Optional[SubjectSchema]: The parsed subject schema object,
              or None if the subject could not be parsed
              (e.g., because the domain is missing).
        """
        specs = set_spec.split(":")
        # Not domain nor subject
        if len(specs) < 2:
            return None
        # Domain
        domain_code = ".".join(specs[:2])
        if len(specs) == 2:
            domain = DomainSchema(
                code=domain_code,
                name=set_name,
                datasource_uuid=self._datasource_uuid,
            )
            domains[domain_code] = domain

        domain = domains.get(domain_code, None)
        specs[-1] = specs[-1].upper() if len(specs[-1]) <= 2 else specs[-1]
        subject_code = ".".join(specs[-2:])
        if domain is None:  # pragma: no cover
            logger.warning(
                "Skipping subject with missing domain",
                extra={
                    "domain_code": domain_code,
                    "subject_code": subject_code,
                    "subject_name": set_name,
                },
            )
            return None
        return SubjectSchema(code=subject_code, name=set_name, domain=domain)


# if __name__ == "__main__":


#     async def main():
#         client = httpx.AsyncClient(
#             timeout=httpx.Timeout(
#                 connect=5.0,
#                 read=30.0,
#                 write=5.0,
#                 pool=5.0,
#             ),
#             limits=httpx.Limits(
#                 max_connections=10,
#                 max_keepalive_connections=5,
#             ),
#             headers={"User-Agent": "ResearchCopilot/1.0"},
#         )
