.PHONY: run stop test test-backend test-frontend test-backend-coverage test-cov coverage-report help

# Detect if running on Windows
UNAME_S := $(shell uname -s 2>/dev/null || echo "Windows_NT")
IS_WINDOWS := $(if $(filter Windows_NT MINGW% MSYS% CYGWIN%,$(OS) $(UNAME_S)),1,0)

help:
	@echo "Available targets:"
	@echo "  make run               - Start backend and frontend together"
	@echo "  make stop              - Stop backend and frontend dev servers"
	@echo "  make test              - Run all tests (backend + frontend)"
	@echo "  make test-backend      - Run backend tests only"
	@echo "  make test-frontend     - Run frontend tests only"
	@echo "  make test-backend-coverage - Run backend tests with coverage report"
	@echo "  make test-cov          - Alias for test-backend-coverage"
	@echo "  make coverage-report   - Generate HTML coverage report"

run:
	@echo "Starting backend (errors ignored if already running)..."
ifeq ($(IS_WINDOWS),1)
	-powershell -NoProfile -Command "$${env:FLASK_APP}='flaskr'; $${env:FLASK_ENV}='development'; Start-Process -FilePath 'powershell' -ArgumentList '-NoExit','-Command','cd backend; .\\venv\\Scripts\\python.exe -m flask run --reload'"
else
	-cd backend && FLASK_APP=flaskr FLASK_ENV=development ./venv/bin/python -m flask run --reload >/tmp/trivia-backend.log 2>&1 &
endif
	@echo "Starting frontend..."
	cd frontend && npm start

stop:
	@echo "Stopping frontend/backend dev servers on ports 3000 and 5000..."
ifeq ($(IS_WINDOWS),1)
	-powershell -NoProfile -Command "$${ports}=@(3000,5000); foreach ($${port} in $${ports}) { $${connections}=Get-NetTCPConnection -LocalPort $${port} -State Listen -ErrorAction SilentlyContinue; if ($${connections}) { $${pids}=($${connections} | Select-Object -ExpandProperty OwningProcess -Unique); foreach ($${procId} in $${pids}) { Stop-Process -Id $${procId} -Force -ErrorAction SilentlyContinue; Write-Host \"Stopped PID $${procId} on port $${port}\"; } } else { Write-Host \"No listener found on port $${port}\"; } }"
else
	-(lsof -ti :3000 -sTCP:LISTEN | xargs -r kill; true)
	-(lsof -ti :5000 -sTCP:LISTEN | xargs -r kill; true)
endif
	@echo "Stop command completed."

test: test-backend-coverage test-frontend
	@echo "✓ All tests completed"

test-backend:
	@echo "Running backend tests..."
ifeq ($(IS_WINDOWS),1)
	cd backend && powershell -NoProfile -Command "& '.\run_tests.ps1' -mode no-cov"
else
	cd backend && PYTHONWARNINGS=ignore::ResourceWarning,ignore::DeprecationWarning python -m pytest _tests/ --tb=short -v
endif
	@echo "✓ Backend tests completed"

test-backend-coverage:
	@echo "Running backend tests with coverage..."
ifeq ($(IS_WINDOWS),1)
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
