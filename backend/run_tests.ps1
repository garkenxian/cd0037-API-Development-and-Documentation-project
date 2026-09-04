# Test runner script for Windows PowerShell
# Suppresses ResourceWarnings and DeprecationWarnings from test output

param(
    [string]$mode = "coverage"
)

# Set environment variable for warnings suppression
$env:PYTHONWARNINGS = "ignore::ResourceWarning,ignore::DeprecationWarning"

if ($mode -eq "no-cov") {
    Write-Host "Running backend tests..." -ForegroundColor Cyan
    & python -W ignore::ResourceWarning -W ignore::DeprecationWarning -m pytest _tests/ --tb=short -v 2>&1 | Where-Object { $_ -notmatch 'ResourceWarning|unclosed database|Enable tracemalloc' }
    Write-Host "[OK] Backend tests completed" -ForegroundColor Green
}
elseif ($mode -eq "coverage") {
    Write-Host "Running backend tests with coverage..." -ForegroundColor Cyan
    & python -W ignore::ResourceWarning -W ignore::DeprecationWarning -m pytest _tests/ --cov=. --cov-report=term-missing --cov-report=html --tb=short 2>&1 | Where-Object { $_ -notmatch 'ResourceWarning|unclosed database|Enable tracemalloc' }
    Write-Host ""
    Write-Host "[OK] Backend tests completed with coverage report" -ForegroundColor Green
    Write-Host "HTML report generated: htmlcov/index.html" -ForegroundColor Green
}
else {
    Write-Host "Running backend tests with coverage..." -ForegroundColor Cyan
    & python -W ignore::ResourceWarning -W ignore::DeprecationWarning -m pytest _tests/ --cov=. --cov-report=term-missing --cov-report=html --tb=short -q 2>&1 | Where-Object { $_ -notmatch 'ResourceWarning|unclosed database|Enable tracemalloc' }
    Write-Host ""
    Write-Host "[OK] Backend tests completed with coverage report" -ForegroundColor Green
    Write-Host "HTML report generated: htmlcov/index.html" -ForegroundColor Green
}
