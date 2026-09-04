# Python Environment Setup

## Required Python Version

This project requires **Python 3.10** to ensure consistency across development and CI/CD environments.

- **Development**: Python 3.10.x
- **CI/CD (GitHub Actions)**: Python 3.10
- **Minimum**: Python 3.10.0
- **Legacy Note**: Original requirement of 3.7 is no longer supported (end-of-life: June 2023)

## Installing Python 3.10

### Windows Users

1. **Using Microsoft Store (Easiest)**
   ```powershell
   # Search for "Python 3.10" in Microsoft Store and install
   # Or use:
   winget install Python.Python.3.10
   ```

2. **Using python.org**
   - Visit https://www.python.org/downloads/release/python-3109/ (or latest 3.10.x)
   - Download Windows installer
   - Run installer with "Add Python to PATH" option checked
   - Verify: `python --version`

3. **Using Chocolatey**
   ```powershell
   choco install python310
   ```

4. **Using pyenv-win**
   ```powershell
   # Update pyenv database
   cd %USERPROFILE%\.pyenv\pyenv-win
   git pull origin master
   
   # Install Python 3.10
   pyenv install 3.10.13
   pyenv global 3.10.13
   
   # Verify
   pyenv versions
   python --version
   ```

### macOS Users

```bash
# Using Homebrew
brew install python@3.10
brew link python@3.10

# Or using pyenv
pyenv install 3.10.13
pyenv global 3.10.13

# Verify
python3 --version
```

### Linux Users

```bash
# Ubuntu/Debian
sudo apt-get install python3.10 python3.10-venv python3.10-dev

# Or using pyenv
pyenv install 3.10.13
pyenv global 3.10.13

# Verify
python3 --version
```

## Verifying Python 3.10

After installation, verify your Python version:

```powershell
python --version
# Should output: Python 3.10.x
```

## Virtual Environment Setup

Once Python 3.10 is installed:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
.\venv\Scripts\Activate.ps1

# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

## Switching Python Versions (pyenv)

If you have multiple Python versions installed via pyenv:

```bash
# View installed versions
pyenv versions

# Switch to Python 3.10 globally
pyenv global 3.10.13

# Switch for this directory only
pyenv local 3.10.13

# Verify
python --version
```

## Troubleshooting

### "python: command not found"
- Python 3.10 not installed or not in PATH
- Reinstall and ensure "Add to PATH" is checked
- Restart terminal/IDE after installation

### "ModuleNotFoundError" when running tests
- Virtual environment not activated
- Run: `.\venv\Scripts\Activate.ps1` (Windows)
- Or: `source venv/bin/activate` (macOS/Linux)

### GitHub Actions Failures
- PR may have been tested against Python 3.10 requirement
- Ensure local environment matches Python 3.10
- Run tests locally: `cd backend && .\run_tests.ps1`

## CI/CD Alignment

The GitHub Actions workflow (`.github/workflows/tests.yml`) is configured to test against:
- Python 3.10 only
- Ubuntu latest
- All dependencies from `backend/requirements.txt`

Ensure your local environment matches this configuration to avoid "works on my machine" issues.
