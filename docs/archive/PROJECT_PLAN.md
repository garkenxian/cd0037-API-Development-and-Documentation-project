# Plan: Trivia API - Complete Implementation

**TL;DR:** Build a fully functional Trivia API from scratch (~15% currently complete). The project requires implementing 7 REST API endpoints, comprehensive testing (pytest + unittest), local PostgreSQL database setup, and three "stand out" enhancements (question ratings, user tracking with game scores, and category creation). Implementation follows a phased approach: local setup → core API → testing → enhancements → documentation.

---

## Phase 1: Local Development Environment Setup

**Steps:**
1. Create Python virtual environment using pyenv: `pyenv install 3.10.11` (or 3.11.x), then `python -m venv venv`
   - **Note:** Original project docs mention Python 3.7, but it's EOL (2023). Use Python 3.10+ for modern, supported version.
2. Activate virtual environment: `venv\Scripts\activate` (Windows)
3. Upgrade pip: `python -m pip install --upgrade pip`
4. Install backend dependencies: `cd backend && pip install -r requirements.txt`
5. Add pytest dependencies to `backend/requirements.txt`: pytest, pytest-cov, requests
6. Install pytest dependencies: `pip install pytest pytest-cov requests`
7. Create `.env` file in backend/ with database credentials (DATABASE_URL, FLASK_APP, FLASK_ENV)
8. Create `.env.example` template file for reference
9. Update `.gitignore` to exclude `venv/`, `.env`, `__pycache__/`, `.pytest_cache/`, `*.pyc`, `htmlcov/`, `.coverage`
10. Verify PostgreSQL is running locally (Windows services or `pg_ctl status`)
11. Test database connection: `psql -U postgres -d postgres` 
12. Create trivia databases: `createdb trivia` and `createdb trivia_test`
13. Create `Makefile` in backend/ with common tasks *(parallel with step 14)*
14. Create `db_seed.py` script in backend/ for seeding test data *(parallel with step 13)*

**Relevant Files:**
- `.env` — Local environment variables (not committed)
- `.env.example` — Template showing required variables
- `.gitignore` — Exclude virtual env and secrets
- `backend/requirements.txt` — Add pytest dependencies
- `backend/Makefile` — Task automation for common operations
- `backend/db_seed.py` — Database seeding script

**Makefile Targets to Create:**
```makefile
# Run the Flask development server
run:
	flask run --reload

# Run all tests (unittest)
test:
	python test_flaskr.py

# Run pytest tests with coverage
test-pytest:
	pytest --cov=flaskr --cov-report=html --cov-report=term

# Run all tests (both unittest and pytest)
test-all:
	python test_flaskr.py && pytest --cov=flaskr --cov-report=html

# Drop and recreate the development database
db-reset:
	dropdb trivia || true
	createdb trivia
	psql trivia < trivia.psql

# Drop and recreate the test database
db-reset-test:
	dropdb trivia_test || true
	createdb trivia_test
	psql trivia_test < trivia.psql

# Seed the database with test data
db-seed:
	python db_seed.py

# Full database refresh (drop, create, seed)
db-refresh:
	$(MAKE) db-reset
	$(MAKE) db-seed

# Full test database refresh
db-refresh-test:
	$(MAKE) db-reset-test
	$(MAKE) db-seed

# Clean up Python cache files and test artifacts
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage

# Install dependencies
install:
	pip install -r requirements.txt

# Check code style with pylint
lint:
	pylint flaskr/ test_flaskr.py

# Format code with black
format:
	black flaskr/ test_flaskr.py tests/

# Show help
help:
	@echo "Available targets:"
	@echo "  run              - Run Flask development server"
	@echo "  test             - Run unittest tests"
	@echo "  test-pytest      - Run pytest tests with coverage"
	@echo "  test-all         - Run both test suites"
	@echo "  db-reset         - Drop and recreate dev database"
	@echo "  db-reset-test    - Drop and recreate test database"
	@echo "  db-seed          - Seed database with test data"
	@echo "  db-refresh       - Reset and seed dev database"
	@echo "  db-refresh-test  - Reset and seed test database"
	@echo "  clean            - Remove cache files"
	@echo "  install          - Install Python dependencies"
	@echo "  lint             - Run pylint code checks"
	@echo "  format           - Format code with black"
```

**db_seed.py Script Structure:**
- Import models (Question, Category, User, GameSession)
- Create database connection
- Define seed data (additional questions, users, sample game sessions)
- Insert seed data with error handling
- Print confirmation messages
- Support for both dev and test databases via command-line arg

**Verification:**
1. `python --version` - shows expected Python version
2. `pip list` - shows Flask, SQLAlchemy, pytest, etc.
3. `psql -U postgres -l` - lists databases including trivia and trivia_test
4. `.env` file exists with DATABASE_URL="postgresql://postgres:password@localhost:5432/trivia"
5. Virtual environment activated (prompt shows `(venv)`)
6. `make help` - displays all available Makefile targets
7. `make db-reset` - successfully recreates database
8. `make db-seed` - adds seed data without errors
9. `make run` - Flask server starts on port 5000
10. `make test` - runs tests successfully

---

## Phase 2: Database & Models Enhancement

**Steps:**
1. Update `backend/models.py` to use environment variables (os.getenv) instead of hardcoded credentials *(depends on Phase 1, step 4)*
2. Extend Question model with `rating` field (Integer, nullable, default=0) for stand out feature
3. Create new `User` model with fields: id, username, email, total_score, games_played
4. Create `GameSession` model to track individual game results: id, user_id, score, category_id, date_played
5. Update database initialization to create all tables
6. Create database migration scripts (or document manual SQL for schema updates)
7. Update `trivia.psql` to include sample data for ratings, users, game sessions
8. Test database setup with both `trivia` and `trivia_test` databases

**Relevant Files:**
- `backend/models.py` — Add User, GameSession models; extend Question with rating
- `backend/trivia.psql` — Add sample data for new models
- `.env.example` — Document DATABASE_URL format

**Verification:**
1. Run `createdb trivia && psql trivia < trivia.psql` - no errors, all tables created
2. Query new tables - `SELECT * FROM users;` returns sample data
3. Test model methods - `User.format()`, `GameSession.format()` work correctly
4. Verify environment variable loading - app connects using DATABASE_URL from .env

---

## Phase 3: Core API Implementation (Basic Endpoints)

**Steps:**
1. Configure CORS in `backend/flaskr/__init__.py` with `after_request` decorator *(parallel with step 2)*
2. Implement error handlers (404, 422, 400, 500) with JSON responses *(parallel with step 1)*
3. Create helper function for pagination (returns formatted questions for page)
4. Implement `GET /categories` - return all categories as {id: type} dictionary
5. Implement `GET /questions?page=<int>` - return paginated questions (10 per page), total, categories, current_category
6. Implement `DELETE /questions/<int:id>` - delete question by ID, return 200 or 404
7. Implement `POST /questions` with conditional logic:
   - If payload has `searchTerm` → search questions (case-insensitive substring)
   - Else → create new question (validate all required fields)
8. Implement `GET /categories/<int:id>/questions` - return questions filtered by category
9. Implement `POST /games` - return random question from category, excluding previous_questions list
10. Add input validation for all POST endpoints (validate required fields, types, ranges)

**Relevant Files:**
- `backend/flaskr/__init__.py` — All endpoint implementations
- `backend/models.py` — Reference for Question.format(), Category.format()

**Verification:**
1. Use curl/Postman to test each endpoint manually
2. Test pagination - page 1, page 2, invalid page number
3. Test error cases - invalid IDs, missing fields, malformed JSON
4. Test search - partial matches, case-insensitive, no results
5. Test quiz logic - excludes previous questions, handles category filtering
6. Verify CORS headers present in responses

---

## Phase 4: Testing Infrastructure

**Steps:**
1. Add pytest dependencies to `backend/requirements.txt` (pytest, pytest-cov, requests) *(parallel with step 2)*
2. Create `backend/pytest.ini` for pytest configuration (test discovery, output format) *(parallel with step 1)*
3. Create `backend/conftest.py` with fixtures (test_client, test_db, sample_data)
4. Implement tests in `backend/test_flaskr.py` using unittest (for rubric compliance):
   - Test each endpoint success case
   - Test each endpoint error case (404, 422, 400)
   - Test pagination edge cases
   - Test search functionality
   - Test quiz randomization and exclusion logic
5. Create `backend/tests/` folder for pytest-based API tests *(parallel with step 4)*
6. Implement pytest API tests with better fixtures and parametrization:
   - `test_api_categories.py` - GET /categories tests
   - `test_api_questions.py` - GET/POST/DELETE /questions tests
   - `test_api_game.py` - POST /games tests
   - `test_api_errors.py` - Error handler tests
7. Set up test coverage reporting (pytest-cov, coverage.xml, htmlcov/)
8. Create test data seeding script for trivia_test database

**Relevant Files:**
- `backend/test_flaskr.py` — Unittest tests (rubric requirement)
- `backend/pytest.ini` — Pytest configuration
- `backend/conftest.py` — Shared pytest fixtures
- `backend/tests/test_api_*.py` — Organized pytest test suites
- `backend/requirements.txt` — Add pytest, pytest-cov, requests

**Verification:**
1. Run `python test_flaskr.py` - all unittest tests pass
2. Run `pytest` - all pytest tests pass
3. Run `pytest --cov=flaskr --cov-report=html` - coverage report generated, >80% coverage
4. Review `htmlcov/index.html` - identify untested code paths
5. Verify test database is properly cleaned up after test runs

---

## Phase 5: Stand Out Features - Enhanced Functionality

**Steps:**
1. **Question Ratings Feature:**
   - Implement `POST /questions/<int:id>/rate` endpoint to update question rating (1-5 scale) *(parallel with step 2.1)*
   - Update frontend API calls to fetch and display ratings *(parallel with step 2.2)*
2. **User & Game Tracking Feature:**
   - Implement `POST /users` to create new user (username, email) *(parallel with step 2.3)*
   - Implement `GET /users` to list all users with scores *(parallel with step 2.4)*
   - Implement `GET /users/<int:id>` to get user details and game history *(parallel with step 2.5)*
   - Implement `POST /game-sessions` to record completed quiz results (user_id, score, category) *(parallel with step 2.6)*
   - Update `POST /games` to optionally accept user_id for tracking
   - Implement `GET /leaderboard` to show top users by total_score
3. **Category Management Feature:**
   - Implement `POST /categories` to create new category (requires type/name)
   - Implement `PUT /categories/<int:id>` to update category name
   - Implement `DELETE /categories/<int:id>` to delete category (if no associated questions)
   - Add validation to prevent duplicate category names
4. Write tests for all new endpoints (both unittest and pytest) *(depends on steps 1-3)*
5. Update database models if needed for new relationships or constraints

**Relevant Files:**
- `backend/flaskr/__init__.py` — New endpoints for ratings, users, categories
- `backend/models.py` — User, GameSession models already defined in Phase 2
- `backend/test_flaskr.py` — Add tests for new features
- `backend/tests/test_api_users.py` — New pytest test file for user endpoints
- `backend/tests/test_api_ratings.py` — New pytest test file for rating endpoints
- `backend/tests/test_api_category_mgmt.py` — New pytest test file for category management

**Verification:**
1. Test rating a question - rating persists and returns updated value
2. Test user creation - new users appear in database with score 0
3. Test game session recording - user's total_score increments correctly
4. Test leaderboard - returns users ordered by total_score descending
5. Test category creation - new category appears in GET /categories
6. Test category deletion - fails if questions exist, succeeds if empty
7. Run all tests - new tests pass, existing tests still pass

---

## Phase 6: API Documentation

**Steps:**
1. Create `API_DOCUMENTATION.md` in backend/ folder with comprehensive endpoint documentation *(parallel with step 2)*
2. Update `backend/README.md` with complete API documentation using rubric format: *(depends on step 1)*
   - Each endpoint: METHOD URL, Request parameters, Response body, Example requests/responses
   - Document both success and error responses
   - Include curl examples for each endpoint
3. Document environment variables required (.env setup instructions)
4. Document database setup steps (createdb, psql import, migrations if any)
5. Document testing procedures (unittest and pytest commands)
6. Add code comments and docstrings to all endpoint functions (Google-style docstrings)
7. Update root `README.md` with project overview, setup instructions, features implemented

**Relevant Files:**
- `backend/API_DOCUMENTATION.md` — Detailed endpoint specifications
- `backend/README.md` — API documentation with examples
- `README.md` — Project overview and setup guide
- `backend/flaskr/__init__.py` — Add docstrings to functions

**Verification:**
1. Review documentation - all endpoints documented with examples
2. Follow setup instructions from scratch - verify they work step-by-step
3. Copy curl commands from docs - all execute successfully
4. Check code quality - all functions have clear docstrings
5. Run `pylint backend/flaskr/__init__.py` - minimal warnings, follows PEP 8

---

## Phase 7: Code Quality & Final Validation

**Steps:**
1. Run `pylint` on all Python files, fix issues to meet PEP 8 standards *(parallel with step 2)*
2. Run `black` formatter on all Python code for consistent style *(parallel with step 1)*
3. Review all endpoint names - ensure they're logical and RESTful
4. Review all variable/function names - ensure they're descriptive
5. Add comments to complex logic (pagination, quiz randomization, search)
6. Verify `.gitignore` excludes all secrets (.env, __pycache__, logs, etc.)
7. Test full user workflow end-to-end:
   - Browse questions by page and category
   - Search for questions
   - Add new question
   - Delete question  
   - Play quiz game
   - Create user and record game score
   - Rate questions
   - Create new category
8. Run final test suite - all tests pass with >80% coverage
9. Review rubric checklist - ensure all requirements met

**Relevant Files:**
- All `backend/**/*.py` files — Code quality checks
- `.gitignore` — Verify exclusions
- `PROJECT_RUBRIC.md` — Final checklist

**Verification:**
1. Run `pylint backend/` - score >8.0/10
2. Run `black --check backend/` - no files need formatting
3. Run full test suite - 100% pass rate, >80% coverage
4. Manual testing - all workflows complete successfully
5. Code review - readable, well-documented, follows best practices
6. Rubric checklist - all criteria marked complete

---

## Decisions

### Database Configuration
- **Decision:** Move credentials to environment variables immediately (Phase 1)
- **Rationale:** Rubric explicitly requires this for security; fixing later risks forgetting

### Testing Strategy
- **Decision:** Implement both unittest (rubric compliance) AND pytest (best practice)
- **Rationale:** Unittest ensures rubric pass; pytest provides better developer experience for ongoing work

### Implementation Order  
- **Decision:** Core API first (Phase 3), enhancements later (Phase 5)
- **Rationale:** Establishes working baseline quickly; easier to test and validate incrementally

### Stand Out Features
- **Decision:** Implement all three enhancements (ratings, users/scores, category management)
- **Rationale:** User wants to maximize project impact; features have synergies (users need ratings, categories need management)

### Local Development Approach
- **Decision:** Use local virtual environment (venv) + local PostgreSQL instead of dev containers
- **Rationale:** User has pyenv and PostgreSQL already installed; simpler for Windows development; faster iteration without container overhead

---

## Further Considerations

### Frontend Integration
After backend completion, consider updating frontend components to:
- Display question ratings with star UI
- Show user login/registration flow
- Display leaderboard page
- Allow admins to create categories

*Note: Frontend changes are optional per project requirements, but enhance demo value*

### Deployment Considerations
The current setup is development-only. For production deployment, consider:
- Separate Dockerfile optimized for production
- Environment-specific configs (dev/staging/prod)
- Database migration strategy
- HTTPS/SSL termination
- CORS origin restrictions (currently wide open)

### Performance Optimization
Current implementation prioritizes correctness over performance. Future optimizations:
- Database query optimization (indexes on category, difficulty)
- Caching for GET /categories (rarely changes)
- Pagination efficiency with cursor-based approach
- Rate limiting for API endpoints

---

## Project Scope Boundaries

**In Scope:**
✅ All 7 core API endpoints  
✅ Comprehensive error handling  
✅ Full test coverage (unittest + pytest)  
✅ Local PostgreSQL setup  
✅ Three stand out features (ratings, users/scores, category management)  
✅ Complete API documentation  
✅ PEP 8 compliant code  
✅ Environment-based configuration  

**Out of Scope:**
❌ Frontend modifications (will work with existing frontend as-is)  
❌ Authentication/authorization (users are tracked but no login required)  
❌ Production deployment configuration  
❌ Database migration framework (manual schema changes documented)  
❌ API rate limiting  
❌ Caching layer  
❌ WebSocket support for real-time features  

---

## Success Criteria

**Rubric Requirements Met:**
- ✅ PEP 8 compliant, well-documented code
- ✅ Clear variable/function names, logical endpoints
- ✅ Comprehensive README with setup and API documentation
- ✅ Secrets as environment variables
- ✅ RESTful principles followed
- ✅ Routes perform CRUD operations
- ✅ Multiple HTTP methods (GET, POST, DELETE, PUT)
- ✅ Error handlers with JSON responses
- ✅ Unittest tests for expected behavior and errors
- ✅ Tests validate CRUD persistence

**Stand Out Features:**
- ✅ Question rating field added
- ✅ Users and game score tracking
- ✅ Category creation capability

**Additional Quality Markers:**
- ✅ Modern testing approach (pytest)
- ✅ Local development environment with Makefile automation
- ✅ >80% test coverage
- ✅ Comprehensive API documentation
