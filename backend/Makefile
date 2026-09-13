.PHONY: help run test test-cov test-all db-init db-seed db-refresh clean install lint format ensure-venv bootstrap

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
	@echo "  test             - Run all tests (auto-discoverable)"
	@echo "  test-cov         - Run tests with coverage report"
	@echo "  db-init          - Initialize database using SQLAlchemy"
	@echo "  db-seed          - Seed database with sample data"
	@echo "  db-refresh       - Initialize and seed database"
	@echo "  clean            - Remove cache files and artifacts"
	@echo "  install          - Install Python dependencies"
	@echo "  lint             - Run pylint code checks"
	@echo "  format           - Format code with black"

install:
	$(PYTHON) -m pip install -r requirements.txt

ensure-venv:
ifeq ($(OS),Windows_NT)
	powershell -NoProfile -Command "if (-not (Test-Path '.\\venv\\Scripts\\python.exe')) { if (Get-Command py -ErrorAction SilentlyContinue) { py -3 -m venv venv } else { python -m venv venv } }"
else
	@test -x "$(PYTHON)" || python3 -m venv $(VENV)
endif

bootstrap: ensure-venv install

run:
	"$(MAKE)" ensure-venv
	$(PYTHON) -m flask run --reload

test:
	"$(MAKE)" bootstrap
ifeq ($(OS),Windows_NT)
	powershell -NoProfile -Command "& '.\run_tests.ps1' -mode no-cov"
else
	$(PYTHON) -W ignore::ResourceWarning -W ignore::DeprecationWarning -m pytest --tb=short -v
endif

test-cov:
	"$(MAKE)" bootstrap
ifeq ($(OS),Windows_NT)
	powershell -NoProfile -Command "& '.\run_tests.ps1'"
else
	$(PYTHON) -W ignore::ResourceWarning -W ignore::DeprecationWarning -m pytest --cov=. --cov-report=term-missing --cov-report=html --tb=short
endif

test-all: test

db-init:
	$(PYTHON) _helpers/db_init.py --force

db-seed:
	$(PYTHON) _helpers/db_seed.py

db-refresh: db-init db-seed

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage || true

lint:
	$(PYTHON) -m pylint flaskr/ _tests/ _helpers/ || true

format:
	$(PYTHON) -m black flaskr/ _tests/ _helpers/
