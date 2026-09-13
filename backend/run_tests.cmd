@echo off
REM Test runner script for Windows
REM Suppresses ResourceWarnings and DeprecationWarnings from test output

setlocal enabledelayedexpansion

set "PYTHONWARNINGS=ignore::ResourceWarning,ignore::DeprecationWarning"

set "PYTHON_CMD=python"
if exist ".\venv\Scripts\python.exe" set "PYTHON_CMD=.\venv\Scripts\python.exe"

if "%1"=="" (
    echo Running backend tests with coverage...
    %PYTHON_CMD% -W ignore::ResourceWarning -W ignore::DeprecationWarning -m pytest --cov=. --cov-report=term-missing --cov-report=html --tb=short -q
    if errorlevel 1 (
        echo [FAIL] Backend tests failed
        exit /b 1
    )
    echo.
    echo ✓ Backend tests completed with coverage report
    echo HTML report generated: htmlcov/index.html
) else if "%1"=="no-cov" (
    echo Running backend tests...
    %PYTHON_CMD% -W ignore::ResourceWarning -W ignore::DeprecationWarning -m pytest --tb=short -v
    if errorlevel 1 (
        echo [FAIL] Backend tests failed
        exit /b 1
    )
    echo ✓ Backend tests completed
) else if "%1"=="coverage" (
    echo Running backend tests with coverage...
    %PYTHON_CMD% -W ignore::ResourceWarning -W ignore::DeprecationWarning -m pytest --cov=. --cov-report=term-missing --cov-report=html --tb=short
    if errorlevel 1 (
        echo [FAIL] Backend tests failed
        exit /b 1
    )
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
