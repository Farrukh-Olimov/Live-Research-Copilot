import httpx
import pytest
import pytest_asyncio

from common.utils.logger.constants import LogLevel
from common.utils.logger.logger_config import LoggerManager
from common.utils.logger.rotation import RotationType
from tests.mocks.arxiv_routes import lazy_arxiv_router


@pytest.fixture(autouse=True, scope="session")
def setup_logger():
    """Configure the logger before running any tests."""
    LoggerManager.configure(
        level=LogLevel.DEBUG,
        rotation_type=RotationType.TIME,
        console_colors=True,
        structured_format=False,
        sanitize_sensitive=True,
    )
    yield


@pytest_asyncio.fixture(
    scope="session",
)
async def httpx_async_client():
    """Returns an httpx AsyncClient object.

    MockTransport that handles requests according to
    the lazy_arxiv_router handler.
    """
    handler = lazy_arxiv_router()
    transport = httpx.MockTransport(handler=handler)
    async with httpx.AsyncClient(transport=transport) as client:
        yield client
