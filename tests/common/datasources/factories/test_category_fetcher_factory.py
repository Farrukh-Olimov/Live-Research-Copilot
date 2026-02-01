import pytest
from uuid import uuid4
from common.constants import DataSource
from common.datasources.arxiv import ArxivCategoryFetcher
from common.datasources.factories import CategoryFetcherFactory


def test_category_fetcher_factory_error():
    """Tests that the CategoryFetcherFactory raises a KeyError."""
    with pytest.raises(KeyError):
        CategoryFetcherFactory.create("NoValue", uuid4(), None)


def test_category_fetcher_factory_arxiv():
    """Tests that the CategoryFetcherFactory creates an ArxivCategoryFetcher."""
    category_fetcher = CategoryFetcherFactory.create(DataSource.ARXIV, uuid4(), None)
    assert isinstance(category_fetcher, ArxivCategoryFetcher)
