define LOAD_ENV
    @set -a; [ -f .env ] && source .env; set +a;
endef

install:
	uv sync --dev

lint:
	uv run pylint src/ncoreparser
	uv run mypy src/ncoreparser

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

bump-version:
	uv version --bump minor
