import pytest

from common.utils.logger.constants import LogLevel
from common.utils.logger.logger_config import LoggerManager
from common.utils.logger.rotation import RotationType


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
