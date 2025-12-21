from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.database.postgres.models.domain import Domain

from .base_repository import BaseRepository


class DomainRepository(BaseRepository[Domain]):
    """Repository for domain queries."""

    def __init__(self, session: AsyncSession):
        """Initializes a DomainRepository object.

        Args:
            session (AsyncSession): The session to use for database operations.
        """
        super().__init__(Domain, session)

    async def create(self, domain: Domain) -> Domain:
        """Creates a domain."""
        self.session.add(domain)
        await self.session.flush()
        return domain

    async def create_many(self, domains: List[Domain]) -> List[Domain]:
        """Creates batch of domains."""
        self.session.add_all(domains)
        await self.session.flush()
        return domains

    async def get_by_code(self, code: str) -> Domain:
        """Returns a domain by code."""
        query = select(Domain).filter_by(code=code)
        rows = await self.session.execute(query)
        return rows.scalar_one_or_none()

    async def get_by_codes(self, codes: List[str]) -> List[Domain]:
        """Returns a list of domains by codes."""
        query = select(Domain).filter(Domain.code.in_(codes))
        rows = await self.session.execute(query)
        return rows.scalars().all()
