.PHONY: help run test test-pytest test-all db-reset db-reset-test db-seed db-refresh db-refresh-test clean install lint format

VENV := venv
ifeq ($(OS),Windows_NT)
	PYTHON := $(VENV)\Scripts\python.exe
	PIP := $(VENV)\Scripts\pip.exe
	ACTIVATE := $(VENV)\Scripts\activate.bat
else
	PYTHON := $(VENV)/bin/python
	PIP := $(VENV)/bin/pip
	ACTIVATE := . $(VENV)/bin/activate
endif

help:
	@echo "Available targets:"
	@echo "  run              - Run Flask development server"
	@echo "  test             - Run unittest tests"
	@echo "  test-pytest      - Run pytest tests with coverage"
	@echo "  test-all         - Run both test suites"
	@echo "  db-reset         - Drop and recreate dev database"
	@echo "  db-reset-test    - Drop and recreate test database"
	@echo "  db-seed          - Seed database with test data"
	@echo "  db-refresh       - Reset and seed dev database"
	@echo "  db-refresh-test  - Reset and seed test database"
	@echo "  clean            - Remove cache files and artifacts"
	@echo "  install          - Install Python dependencies"
	@echo "  lint             - Run pylint code checks"
	@echo "  format           - Format code with black"

install:
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) -m flask run --reload

test:
	$(PYTHON) test_flaskr.py

test-pytest:
	$(PYTHON) -m pytest --cov=flaskr --cov-report=html --cov-report=term

test-all: test test-pytest

db-reset:
	dropdb trivia || true
	createdb trivia
	psql trivia < trivia.psql

db-reset-test:
	dropdb trivia_test || true
	createdb trivia_test
	psql trivia_test < trivia.psql

db-seed:
	$(PYTHON) _helpers/db_seed.py

db-refresh: db-reset db-seed

db-refresh-test: db-reset-test db-seed

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage || true

lint:
	$(PYTHON) -m pylint flaskr/ test_flaskr.py || true

format:
	$(PYTHON) -m black flaskr/ test_flaskr.py tests/ || true
