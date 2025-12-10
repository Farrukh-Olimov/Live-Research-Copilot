check:
	@poetry run black --check --diff .
	@poetry run ruff check .

clear_cache: 
	@poetry cache clear pypi --all --no-interaction
	@poetry cache clear --all PyPI -n 
	@poetry cache clear --all _default_cache -n
	@poetry run pip cache purge

fix:
	@poetry run toml-sort --in-place pyproject.toml 
	@poetry sort 
	@poetry run black .
	@poetry run ruff check --fix .

test: 
	@poetry run pytest . --cov=. --cov-report=

test-coverage:
	@poetry run pytest --cov-report=term-missing  --cov=.

.PHONY: check clear_cache fix 