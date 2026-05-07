.PHONY: install test lint format clean

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest tests/

lint:
	python -m ruff check src/ tests/
	python -m mypy src/doc2md

format:
	python -m ruff check src/ tests/ --fix

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov dist build *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -f .coverage
