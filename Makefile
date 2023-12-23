ACTIVATE = . .venv/bin/activate

.venv:
	python3.9 -m venv .venv

venv: .venv

lock:
	$(ACTIVATE) && pip install --upgrade pip pip-tools
	$(ACTIVATE) && pip-compile --generate-hashes --output-file=requirements.txt --resolver=backtracking --no-emit-index-url pyproject.toml
	$(ACTIVATE) && pip-compile --generate-hashes --output-file=dev-requirements.txt --resolver=backtracking --no-emit-index-url --extra dev pyproject.toml

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
	git tag $(shell grep 'version' pyproject.toml | cut -d '"' -f2)
	git push --tags

clean:
	rm -rf .venv
