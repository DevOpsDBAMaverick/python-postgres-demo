.PHONY: install lint test

install:
	python -m pip install --upgrade pip
	pip install uv
	pip install -e .[dev]

lint:
	ruff check src tests

test:
	pytest -q
