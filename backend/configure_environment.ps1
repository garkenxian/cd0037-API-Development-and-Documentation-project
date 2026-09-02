# Create the virtual environment
python -m venv venv

# Activate it
venv\Scripts\Activate.ps1

# Verify activation (prompt should show "(venv)")
python --version

# Install dependencies
pip install -r requirements.txt