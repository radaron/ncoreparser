ACTIVATE = . .venv/bin/activate

define LOAD_ENV
    @set -a; [ -f .env ] && source .env; set +a;
endef

.venv:
	rm -rf .venv
	python3 -m venv .venv
	$(ACTIVATE) && pip install --upgrade pip

venv: .venv

reqs: .venv
	$(ACTIVATE) && pip install .[dev]

lint:
	$(ACTIVATE) && pylint ncoreparser
	$(ACTIVATE) && mypy ncoreparser

format:
	$(ACTIVATE) && black .

test:
	$(ACTIVATE) && tox

module-test:
	$(LOAD_ENV) $(ACTIVATE) && cd ./tests/test_module && NCORE_USERNAME="${NCORE_USERNAME}" NCORE_PASSWORD="${NCORE_PASSWORD}" RSS_URL="${RSS_URL}" tox

manual-test:
	$(LOAD_ENV) $(ACTIVATE) && python -m tests.manual --user ${NCORE_USERNAME} \
		--passw "${NCORE_PASSWORD}" --rss-feed "${RSS_URL}"

git-tag:
	git tag v$(shell grep 'version' pyproject.toml | cut -d '"' -f2)
	git push --tags
