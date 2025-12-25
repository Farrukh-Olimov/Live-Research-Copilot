from functools import lru_cache

import httpx

from common.constants.path import APP_ROOT
from common.datasources.arxiv.category_fetcher import ArxivCategoryFetcher
from tests.helpers.load_data import load_text_file

DATA_DIR = APP_ROOT.joinpath("tests", "data", "common", "datasources", "arxiv")


@lru_cache(maxsize=2)
def load_response(filepath: str):
    """Load the contents of a file from the DATA_DIR directory.

    The file is determined by the filepath parameter.

    If the file has a ".txt" extension, its contents are loaded
    using the load_text_file function. Otherwise, a
    NotImplementedError is raised.

    The function is decorated with lru_cache to ensure that
    the contents of the file are only loaded once and then cached.
    """
    extension = filepath.split(".")[-1]
    if extension in ["txt"]:
        return load_text_file(DATA_DIR.joinpath(filepath))
    raise NotImplementedError(f"Loading {extension} not implemented")


def lazy_arxiv_router():
    """Return a mock handler function for arXiv routes.

    This function returns a handler that will return a 200 response with
    the contents of the "category.txt" file when called with a GET request
    to the "/oai" endpoint with the "verb" parameter set to "ListSets".
    All other requests will raise a NotImplementedError.

    """

    async def handler(request: httpx.Request) -> httpx.Response:
        """Mock handler function for arXiv routes."""
        params = dict(request.url.params)

        param = next(iter(ArxivCategoryFetcher.PARAMS))
        if param in params:
            return httpx.Response(
                200,
                text=load_response(DATA_DIR.joinpath("category.txt").as_posix()),
            )

        raise NotImplementedError(
            f"Mocking {request.method} {request.url} not implemented"
        )

    return handler
