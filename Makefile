ACTIVATE = . .venv/bin/activate

.venv:
	python3.9 -m venv .venv

venv: .venv

reqs: .venv
	$(ACTIVATE) && pip install -r requirements.txt

reqs-dev: reqs
	$(ACTIVATE) && pip install -r dev-requirements.txt

lint: reqs-dev
	$(ACTIVATE) && pylint ncoreparser

test: reqs-dev
	$(ACTIVATE) && python -m pytest tests/

manual-test:
	$(ACTIVATE) && python -m tests.manual --user ${NCORE_USERNAME} \
		--passw "${NCORE_PASSWORD}" --rss-feed "${RSS_URL}"

build:
	$(ACTIVATE) && pip install --upgrade build
	$(ACTIVATE) && python -m build

git-tag:
	git tag v$(shell grep 'version' pyproject.toml | cut -d '"' -f2)
	git push --tags

clean:
	rm -rf .venv
