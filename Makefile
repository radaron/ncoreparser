define LOAD_ENV
    @set -a; [ -f .env ] && source .env; set +a;
endef

install:
	uv sync --dev

lint:
	uv run pylint ncoreparser
	uv run mypy ncoreparser

check-format:
	uv run black --check .

format:
	uv run black .

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

git-tag:
	git tag v$(uv version -s)
	git push --tags
