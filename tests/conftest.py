import httpx
import pytest
import pytest_asyncio

from common.utils.logger import LoggerManager, LogLevel
from common.utils.logger.rotation import RotationType


@pytest.fixture(autouse=True, scope="session")
def setup_logger():
    """Configure the logger before running any tests."""
    LoggerManager.configure(
        level=LogLevel.CRITICAL,
        rotation_type=RotationType.TIME,
        log_to_console=True,
        log_to_file=False,
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
    from tests.mocks.arxiv_routes import lazy_arxiv_router

    handler = lazy_arxiv_router()
    transport = httpx.MockTransport(handler=handler)
    async with httpx.AsyncClient(transport=transport) as client:
        yield client
