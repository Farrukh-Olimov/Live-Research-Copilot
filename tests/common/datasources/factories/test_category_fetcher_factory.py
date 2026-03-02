from uuid import uuid4

import pytest

from common.constants import DataSource
from common.datasources.arxiv import ArxivSubjectsFetcher
from common.datasources.factories import SubjectsFetcherFactory


def test_category_fetcher_factory_error():
    """Tests that the CategoryFetcherFactory raises a KeyError."""
    with pytest.raises(KeyError):
        SubjectsFetcherFactory.get("NoValue", uuid4(), None)


def test_category_fetcher_factory_arxiv():
    """Tests that the CategoryFetcherFactory creates an ArxivCategoryFetcher."""
    category_fetcher = SubjectsFetcherFactory.get(DataSource.ARXIV, uuid4(), None)
    assert isinstance(category_fetcher, ArxivSubjectsFetcher)
