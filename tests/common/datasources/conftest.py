import pytest


@pytest.fixture
def reset_datasource_registry():
    """Resets the datasource registry to its initial state.

    This fixture clears the datasource registry before and after each test.
    """
    from common.datasources.schema_registry import DatasourceSchemas

    DatasourceSchemas.clear()
    yield
    DatasourceSchemas.clear()
