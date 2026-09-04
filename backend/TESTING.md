# Running Backend Tests

This directory contains the backend Flask application with comprehensive test coverage. The test runner has been configured to suppress expected warnings (ResourceWarning, DeprecationWarning) for clean output.

## Running Tests on Windows (PowerShell)

Use the `run_tests.ps1` script:

```powershell
# Run with coverage (default)
.\run_tests.ps1

# Run without coverage
.\run_tests.ps1 -mode no-cov

# Run with coverage (verbose)
.\run_tests.ps1 -mode coverage
```

### Or run pytest directly with environment variables:

```powershell
$env:PYTHONWARNINGS = "ignore::ResourceWarning,ignore::DeprecationWarning"
python -m pytest _tests/ --cov=. --cov-report=html --cov-report=term-missing
```

## Running Tests on Unix/Linux/macOS

```bash
# Run with coverage
PYTHONWARNINGS=ignore::ResourceWarning,ignore::DeprecationWarning python -m pytest _tests/ --cov=. --cov-report=html --cov-report=term-missing

# Or using Make (if available)
make test-backend-coverage
```

## Test Results

- **Total Tests**: 115
- **Coverage**: 72.63%
- **Warnings**: 0 (suppressed by configuration)

## Coverage Report

After running tests with coverage, view the HTML report:

```
htmlcov/index.html
```

## Configuration Files

- **pytest.ini** - pytest configuration with warning filters
- **conftest.py** - pytest hooks for warning suppression
- **.coveragerc** - coverage measurement configuration
- **run_tests.ps1** - PowerShell script for Windows users

## Test Structure

Tests are organized by layer:

- `_tests/test_models.py` - ORM model tests
- `_tests/test_repositories_unit.py` - Repository layer unit tests
- `_tests/test_services_unit.py` - Service layer unit tests
- `_tests/test_endpoints_unit.py` - Endpoint layer unit tests
- `_tests/test_*_endpoint.py` - Integration tests for each endpoint
- `_tests/test_optimized_queries.py` - Database optimization verification

## What Warnings Are Suppressed?

1. **ResourceWarning** - Expected from in-memory SQLite databases in tests
2. **DeprecationWarning** - From SQLAlchemy internal code (not our application)

These warnings are harmless and don't affect test results.
