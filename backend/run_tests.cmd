@echo off
REM Test runner script for Windows
REM Suppresses ResourceWarnings and DeprecationWarnings from test output

setlocal enabledelayedexpansion

set "PYTHONWARNINGS=ignore::ResourceWarning,ignore::DeprecationWarning"

if "%1"=="" (
    echo Running backend tests with coverage...
    python -m pytest _tests/ --cov=. --cov-report=term-missing --cov-report=html --tb=short -q
    echo.
    echo ✓ Backend tests completed with coverage report
    echo HTML report generated: htmlcov/index.html
) else if "%1"=="no-cov" (
    echo Running backend tests...
    python -m pytest _tests/ --tb=short -v
    echo ✓ Backend tests completed
) else if "%1"=="coverage" (
    echo Running backend tests with coverage...
    python -m pytest _tests/ --cov=. --cov-report=term-missing --cov-report=html --tb=short
    echo.
    echo ✓ Backend tests completed with coverage report
    echo HTML report generated: htmlcov/index.html
) else (
    echo Usage: run_tests.cmd [no-cov^|coverage]
    echo.
    echo Options:
    echo   (default)  - Run tests with coverage
    echo   no-cov     - Run tests without coverage
    echo   coverage   - Run tests with coverage (verbose)
)
