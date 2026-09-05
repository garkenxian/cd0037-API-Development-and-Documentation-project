.PHONY: test test-backend test-frontend test-backend-coverage test-cov coverage-report help

# Detect if running on Windows
UNAME_S := $(shell uname -s 2>/dev/null || echo "Windows_NT")
IS_WINDOWS := $(findstring Windows_NT,$(UNAME_S))

help:
	@echo "Available targets:"
	@echo "  make test              - Run all tests (backend + frontend)"
	@echo "  make test-backend      - Run backend tests only"
	@echo "  make test-frontend     - Run frontend tests only"
	@echo "  make test-backend-coverage - Run backend tests with coverage report"
	@echo "  make test-cov          - Alias for test-backend-coverage"
	@echo "  make coverage-report   - Generate HTML coverage report"

test: test-backend-coverage test-frontend
	@echo "✓ All tests completed"

test-backend:
	@echo "Running backend tests..."
ifeq ($(IS_WINDOWS),Windows_NT)
	cd backend && powershell -NoProfile -Command "& '.\run_tests.ps1' -mode no-cov"
else
	cd backend && PYTHONWARNINGS=ignore::ResourceWarning,ignore::DeprecationWarning python -m pytest _tests/ --tb=short -v
endif
	@echo "✓ Backend tests completed"

test-backend-coverage:
	@echo "Running backend tests with coverage..."
ifeq ($(IS_WINDOWS),Windows_NT)
	cd backend && powershell -NoProfile -Command "& '.\run_tests.ps1'"
else
	cd backend && PYTHONWARNINGS=ignore::ResourceWarning,ignore::DeprecationWarning python -m pytest _tests/ --cov=. --cov-report=term-missing --cov-report=html --tb=short
endif

test-cov: test-backend-coverage
	@echo "✓ Coverage tests completed"

coverage-report:
	@echo "Generating coverage HTML report..."
	cd backend && python -m coverage report
	cd backend && python -m coverage html
	@echo "✓ Coverage report generated at backend/htmlcov/index.html"

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm run test:ci
	@echo "✓ Frontend tests completed"
