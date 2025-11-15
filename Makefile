define LOAD_ENV
    @set -a; [ -f .env ] && source .env; set +a;
endef

install:
	uv sync --dev

lint:
	uv run ruff check src/ncoreparser
	uv run ruff check --select I .
	uv run mypy src/ncoreparser

format:
	uv run ruff check --select I --fix .
	uv run ruff format .

test:
	uv run pytest

module-test:
	$(LOAD_ENV) \
	NCORE_USERNAME="${NCORE_USERNAME}" \
	NCORE_PASSWORD="${NCORE_PASSWORD}" \
	RSS_URL="${RSS_URL}" \
	cd ./tests/test_module &&  && pytest

manual-test:
	$(LOAD_ENV) uv run python -m tests.manual --user ${NCORE_USERNAME} \
		--passw "${NCORE_PASSWORD}" --rss-feed "${RSS_URL}"

bump-version:
	uv version --bump minor
