.PHONY: lint
lint:
	. .venv/bin/activate; \
	pre-commit run --all-files

.PHONY: test
test:
	. .venv/bin/activate; \
	poetry install; \
	pytest tests

.PHONY: install
install:
	python -m venv .venv
	. .venv/bin/activate; \
	poetry install --no-root --only=main

.PHONY: install-dev
install-dev:
	. .venv/bin/activate; \
	poetry install --no-root --only=dev; \
	pre-commit install

.PHONY: dev
dev: install install-dev
