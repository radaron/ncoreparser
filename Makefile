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
	# stop the lint if there are Python syntax errors or undefined names
	$(ACTIVATE) && flake8 ncoreparser --count --select=E9,F63,F7,F82 --show-source --statistics
	# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
	$(ACTIVATE) && flake8 ncoreparser --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

test: reqs-dev
	$(ACTIVATE) && python -m pytest tests/

manual-test:
	$(ACTIVATE) && python -m tests.manual --user ${NCORE_USERNAME} \
		--passw "${NCORE_PASSWORD}" --rss-feed "${RSS_URL}"

build:
	$(ACTIVATE) && pip install --upgrade build
	$(ACTIVATE) && python -m build

clean:
	rm -rf .venv
