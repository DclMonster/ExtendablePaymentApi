.PHONY: all clean install dev test docs build docs-html docs-markdown docs-serve docs-publish docs-wiki docs-all

# Python settings
PYTHON := python
VENV := venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
FLASK := $(VENV)/bin/flask
BLACK := $(VENV)/bin/black
ISORT := $(VENV)/bin/isort
FLAKE8 := $(VENV)/bin/flake8
MYPY := $(VENV)/bin/mypy
PYLINT := $(VENV)/bin/pylint
SPHINX := $(VENV)/bin/sphinx-build
PRE_COMMIT := $(VENV)/bin/pre-commit
INTERROGATE := $(VENV)/bin/interrogate
DOCSTR_COVERAGE := $(VENV)/bin/docstr-coverage

# Directories
SRC_DIR := app
TEST_DIR := tests
DOCS_DIR := docs
DIST_DIR := dist
BUILD_DIR := build
COVERAGE_DIR := htmlcov
DOCSTR_COVERAGE_DIR := docs/docstring_coverage

# Development
install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install -r requirements.txt
	$(PIP) install -r docs/requirements.txt
	$(PRE_COMMIT) install

dev:
	$(FLASK) run --debug

clean:
	rm -rf $(DIST_DIR) $(BUILD_DIR) $(COVERAGE_DIR) .pytest_cache .coverage .benchmarks
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +

# Testing
test: test-unit test-integration test-regression test-performance

test-unit:
	$(PYTEST) $(TEST_DIR)/unit -v -m "unit" --cov=$(SRC_DIR) --cov-report=xml --cov-report=html

test-integration:
	$(PYTEST) $(TEST_DIR)/integration -v -m "integration"

test-regression:
	$(PYTEST) $(TEST_DIR)/regression -v -m "regression"

test-performance:
	$(PYTEST) $(TEST_DIR)/performance -v -m "performance" --benchmark-only

test-watch:
	$(PYTEST) -f $(TEST_DIR)

test-coverage:
	$(PYTEST) --cov=$(SRC_DIR) --cov-report=html
	@echo "Coverage report available at htmlcov/index.html"

# Code Quality
format:
	$(BLACK) .
	$(ISORT) .

lint:
	$(FLAKE8) $(SRC_DIR) $(TEST_DIR)
	$(PYLINT) $(SRC_DIR)/**/*.py $(TEST_DIR)/**/*.py
	$(MYPY) .

validate: format lint spell-check type-check docs-coverage

spell-check:
	npx cspell "**/*.{py,yml,yaml,md}"

type-check:
	$(MYPY) .

# Documentation
docs: docs-html docs-coverage

docs-html:
	$(SPHINX) -b html $(DOCS_DIR)/source $(DOCS_DIR)/build/html

docs-markdown:
	$(SPHINX) -b markdown $(DOCS_DIR)/source $(DOCS_DIR)/build/markdown

docs-serve:
	$(PYTHON) -m http.server 8000 --directory $(DOCS_DIR)/build/html

docs-publish:
	ghp-import -n -p -f $(DOCS_DIR)/build/html

docs-wiki:
	$(PYTHON) scripts/publish_wiki.py

docs-coverage:
	@echo "Running docstring coverage checks..."
	$(INTERROGATE) -v $(SRC_DIR) -f 100 -e "*.pyc" -e "*/tests/*" --generate-badge docs/_static/interrogate_badge.svg
	$(DOCSTR_COVERAGE) $(SRC_DIR) -e "*.pyc" -e "*/tests/*" --skip-magic --skip-file-doc --badge docs/_static/docstr_coverage_badge.svg
	@echo "Docstring coverage report generated in $(DOCSTR_COVERAGE_DIR)"

docs-all: clean docs-html docs-markdown docs-publish docs-wiki

# Benchmarking
benchmark: test-performance

benchmark-compare:
	$(PYTEST) $(TEST_DIR)/performance -v --benchmark-only --benchmark-compare

benchmark-save:
	$(PYTEST) $(TEST_DIR)/performance -v --benchmark-only --benchmark-save=benchmark.json

# Database
db-migrate:
	$(PYTHON) scripts/migrate.py

db-seed:
	$(PYTHON) scripts/seed.py

db-reset:
	$(PYTHON) scripts/reset.py

# Docker
docker-build:
	docker build -t extendable-payment-api-python .

docker-run:
	docker run -p 5000:5000 extendable-payment-api-python

# CI/CD
ci-install:
	$(PIP) install -r requirements.txt
	$(PIP) install -r docs/requirements.txt

ci-validate: validate docs-coverage

ci-test: test

ci-coverage: test-coverage

ci-docs: docs

ci-benchmark: benchmark

# Pre-commit hooks
pre-commit:
	$(PRE_COMMIT) run --all-files

# Release
build:
	$(PYTHON) -m build

release-major: clean build
	bump2version major
	$(PYTHON) -m twine upload dist/*

release-minor: clean build
	bump2version minor
	$(PYTHON) -m twine upload dist/*

release-patch: clean build
	bump2version patch
	$(PYTHON) -m twine upload dist/*

# Help
help:
	@echo "Available commands:"
	@echo "Development:"
	@echo "  make install         - Install dependencies and set up development environment"
	@echo "  make dev            - Run development server"
	@echo "  make clean          - Clean build artifacts"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run all tests"
	@echo "  make test-unit      - Run unit tests"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-regression - Run regression tests"
	@echo "  make test-performance - Run performance tests"
	@echo "  make test-coverage  - Generate coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format         - Format code with black and isort"
	@echo "  make lint           - Run linting tools"
	@echo "  make validate       - Run all code quality checks"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs           - Build documentation"
	@echo "  make docs-serve     - Serve documentation locally"
	@echo ""
	@echo "Database:"
	@echo "  make db-migrate     - Run database migrations"
	@echo "  make db-seed        - Seed database"
	@echo "  make db-reset       - Reset database"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run Docker container"
	@echo ""
	@echo "Release:"
	@echo "  make release-major  - Release major version"
	@echo "  make release-minor  - Release minor version"
	@echo "  make release-patch  - Release patch version"

# Add docstring coverage to pre-commit checks
.git/hooks/pre-commit: $(PRE_COMMIT)
	$(PRE_COMMIT) install
	@echo "#!/bin/sh" > .git/hooks/pre-commit
	@echo "make docs-coverage" >> .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit 