# Backend - Trivia API

## Setting up the Backend

### Install Dependencies

1. **Python 3.10+** - Follow instructions to install Python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)
   - Note: The project is tested with Python 3.10 to match CI/CD configuration. See [PYTHON_VERSION.md](PYTHON_VERSION.md) for detailed setup instructions.

2. **Virtual Environment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virtual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

3. **PIP Dependencies** - Once your virtual environment is setup and running, install the required dependencies by navigating to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

#### Key Pip Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we use to handle the database. Models are defined in `models/` directory.

- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) is the Flask extension that integrates SQLAlchemy with Flask.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we use to handle cross-origin requests from our frontend server.

- [pytest](https://pytest.org/) and [pytest-cov](https://pytest-cov.readthedocs.io/) are used for testing and coverage reporting.

### Set up the Database

The backend uses SQLAlchemy ORM with SQLite for development (and PostgreSQL for production).

#### Option 1: Quick Setup (SQLite - Development)

Create and seed the database with sample data:

```bash
# Navigate to backend directory
cd backend

# Initialize database with seed data
python _helpers/db_init.py --seed
```

This creates all database tables and populates them with:
- **6 Categories**: Science, Art, Geography, History, Entertainment, Sports
- **20 Sample Questions**: Diverse questions across all categories
- **5 Test Users**: alice_wonder, bob_builder, charlie_brown, diana_prince, eve_scientist
- **15 Game Sessions**: Realistic game data with scores and timestamps

#### Option 2: Reset Database (Start Fresh)

To drop all tables and recreate from scratch:

```bash
# Drop all tables and recreate with seed data
python _helpers/db_init.py --force --seed
```

#### Option 3: Manual Seeding Only

If tables already exist and you just want to add sample data:

```bash
# Just run the seeding script
python _helpers/db_seed.py
```

#### Production Setup (PostgreSQL)

Set these environment variables in `.env`:

```bash
SQLALCHEMY_DATABASE_URI=postgresql://username:password@localhost:5432/trivia
SQLALCHEMY_TRACK_MODIFICATIONS=False
```

Then initialize:

```bash
python _helpers/db_init.py --seed
```

### Database Schema

The database includes the following tables:

- **users**: Player profiles with usernames, emails, and game statistics
- **categories**: Question categories (6 predefined)
- **questions**: Trivia questions with answers, categories, and difficulty levels
- **game_sessions**: Records of played games with user, score, and category

See [API_SPECIFICATION.md](API_SPECIFICATION.md) for detailed schema documentation.

### Run the Server

From within the `./backend` directory, ensure you're using your created virtual environment.

To run the server, execute:

```bash
flask run
```

Or using the development server with reload:

```bash
flask run --reload
```

The development server runs on `http://localhost:5000` by default.

## API Endpoints

The API is organized using Flask blueprints for modular, maintainable code. See [API_SPECIFICATION.md](API_SPECIFICATION.md) for complete endpoint documentation.

### Available Endpoints

- **POST /users** - Create a new user account
- **POST /categories** - Create a new category
- **POST /questions** - Create a new question
- **POST /games** - Create a new game session
- **GET /games/<id>** - Get game session state
- **POST /games/<id>/<question_number>** - Answer a question in a game

### Architecture

The backend follows a layered architecture:

```
controllers/     ← API endpoints (Flask blueprints)
  ├── users.py
  ├── categories.py
  ├── questions.py
  └── games.py

services/        ← Business logic layer
  ├── user_service.py
  ├── category_service.py
  ├── question_service.py
  └── game_session_service.py

data_access/     ← Data access layer (repositories)
  ├── user_repository.py
  ├── category_repository.py
  ├── question_repository.py
  └── game_session_repository.py

models/          ← ORM models
  ├── user.py
  ├── category.py
  ├── question.py
  └── game_session.py
```

## Testing

The project uses **pytest** with comprehensive test coverage (94%+).

### Run Tests

```bash
cd backend

# Run all tests
./run_tests.ps1                    # Windows
./run_tests.cmd                    # Windows (alt)
make test                          # macOS/Linux

# Run specific test file
pytest _tests/test_users_endpoint.py

# Run with coverage report
pytest --cov=. --cov-report=html

# View HTML coverage report
open htmlcov/index.html            # macOS
xdg-open htmlcov/index.html        # Linux
start htmlcov/index.html           # Windows
```

### Test Statistics

- **Total Tests**: 181+
- **Coverage**: 94.09%
- **Test Suites**:
  - Endpoint integration tests (`test_*_endpoint.py`)
  - Unit tests for services, repositories, models (`test_*_unit.py`)
  - Optimized query tests (`test_optimized_queries.py`)

### Test Data

When tests run, an in-memory SQLite database is automatically created with seed data. Each test is isolated and runs against a clean database state.

For development, use the seed data described in the "Set up the Database" section above.

## Development Workflow

1. **Create database and seed data**:
   ```bash
   python _helpers/db_init.py --force --seed
   ```

2. **Run development server**:
   ```bash
   flask run --reload
   ```

3. **Run tests** (in another terminal):
   ```bash
   ./run_tests.ps1
   ```

4. **View test coverage**:
   ```bash
   pytest --cov=. --cov-report=html
   open htmlcov/index.html
   ```

## Troubleshooting

### Python Version Issues

If tests fail with "ImportError: cannot import name 'UTC' from 'datetime'":
- This means Python < 3.11 is being used, which doesn't have `datetime.UTC`
- Solution: Install Python 3.10+ (see [PYTHON_VERSION.md](PYTHON_VERSION.md))

### Database Locked

If you see "database is locked" errors:
```bash
# Kill any hanging pytest processes
pkill -f pytest

# Reinitialize the database
python _helpers/db_init.py --force --seed
```

### Import Errors

If Python can't find modules:
```bash
# Ensure you're in the backend directory
cd backend

# Verify virtual environment is activated
python --version  # Should show 3.10+

# Reinstall dependencies
pip install -r requirements.txt
```

## Documentation Files

- [API_SPECIFICATION.md](API_SPECIFICATION.md) - Complete API specification with request/response formats
- [TESTING.md](TESTING.md) - Detailed testing documentation
- [BUSINESS_DECISIONS.md](BUSINESS_DECISIONS.md) - Architecture and design decisions
- [PYTHON_VERSION.md](PYTHON_VERSION.md) - Python version setup and compatibility
- [../PROJECT_PLAN.md](../PROJECT_PLAN.md) - Project overview and status
