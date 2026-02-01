from typing import List

from sqlalchemy import select, UUID
from sqlalchemy.ext.asyncio import AsyncSession

from common.database.postgres.models.domain import Domain

from .base_repository import BaseRepository


class DomainRepository(BaseRepository[Domain]):
    """Repository for domain queries."""

    def __init__(self):
        """Initializes a DomainRepository object."""
        super().__init__(Domain)

    async def create(self, domain: Domain, session: AsyncSession) -> Domain:
        """Creates a domain."""
        session.add(domain)
        await session.flush()
        return domain

    async def create_many(
        self, domains: List[Domain], session: AsyncSession
    ) -> List[Domain]:
        """Creates batch of domains."""
        session.add_all(domains)
        await session.flush()
        return domains

    async def get_by_code(
        self, code: str, datasource_uuid: UUID, session: AsyncSession
    ) -> Domain:
        """Returns a domain by code."""
        query = select(Domain).filter_by(code=code, datasource_id=datasource_uuid)
        rows = await session.execute(query)
        return rows.scalar_one_or_none()

    async def get_by_codes(
        self, codes: List[str], datasource_uuid: List[UUID], session: AsyncSession
    ) -> List[Domain]:
        """Returns a list of domains by codes."""
        query = select(Domain).filter(
            Domain.code.in_(codes), Domain.datasource_id.in_(datasource_uuid)
        )
        rows = await session.execute(query)
        return rows.scalars().all()

    async def delete_domain(self, domain: Domain, session: AsyncSession):
        """Deletes a domain."""
        await session.delete(domain)
