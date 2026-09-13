# Test runner script for Windows PowerShell
# Suppresses ResourceWarnings and DeprecationWarnings from test output

param(
    [string]$mode = "coverage"
)

# Set environment variable for warnings suppression
$env:PYTHONWARNINGS = "ignore::ResourceWarning,ignore::DeprecationWarning"

$pythonCmd = "python"
if (Test-Path ".\venv\Scripts\python.exe") {
    $pythonCmd = ".\venv\Scripts\python.exe"
}

if ($mode -eq "no-cov") {
    Write-Host "Running backend tests..." -ForegroundColor Cyan
    & $pythonCmd -W ignore::ResourceWarning -W ignore::DeprecationWarning -m pytest --tb=short -v
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] Backend tests failed" -ForegroundColor Red
        exit $LASTEXITCODE
    }
    Write-Host "[OK] Backend tests completed" -ForegroundColor Green
}
elseif ($mode -eq "coverage") {
    Write-Host "Running backend tests with coverage..." -ForegroundColor Cyan
    & $pythonCmd -W ignore::ResourceWarning -W ignore::DeprecationWarning -m pytest --cov=. --cov-report=term-missing --cov-report=html --tb=short
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] Backend tests failed" -ForegroundColor Red
        exit $LASTEXITCODE
    }
    Write-Host ""
    Write-Host "[OK] Backend tests completed with coverage report" -ForegroundColor Green
    Write-Host "HTML report generated: htmlcov/index.html" -ForegroundColor Green
}
else {
    Write-Host "Running backend tests with coverage..." -ForegroundColor Cyan
    & $pythonCmd -W ignore::ResourceWarning -W ignore::DeprecationWarning -m pytest --cov=. --cov-report=term-missing --cov-report=html --tb=short -q
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] Backend tests failed" -ForegroundColor Red
        exit $LASTEXITCODE
    }
    Write-Host ""
    Write-Host "[OK] Backend tests completed with coverage report" -ForegroundColor Green
    Write-Host "HTML report generated: htmlcov/index.html" -ForegroundColor Green
}
