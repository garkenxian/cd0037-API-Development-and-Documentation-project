# Test Coverage Setup

This project uses **Codecov** to track and report test coverage for both backend (Python/Flask) and frontend (React) code.

## Coverage Reports

### Backend Coverage
- **Location:** `/backend/htmlcov/index.html` (generated locally after running tests)
- **Tool:** pytest-cov
- **Command:** `make test-pytest` or `pytest --cov=flaskr --cov-report=html`

### Frontend Coverage
- **Location:** `/frontend/coverage` (generated locally after running tests)
- **Tool:** Jest (via react-scripts)
- **Command:** `cd frontend && npm test -- --coverage --watchAll=false`

## Codecov Integration

### Getting Started with Codecov

1. **Sign up for Codecov** (if you haven't already):
   - Visit https://codecov.io
   - Click "Sign up" and authenticate with GitHub
   - Authorize Codecov to access your repositories

2. **Find your Codecov Repository Token**:
   - Go to your repository settings on Codecov
   - Look for the "Repository Upload Token" (usually auto-detected for public repos)
   - Copy the token (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

3. **Add the token to GitHub Secrets**:
   - Go to your GitHub repo → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `CODECOV_TOKEN`
   - Value: Paste your Codecov token
   - Click "Add secret"

### For Public Repositories
If your repository is public, Codecov can auto-detect it and you may not need to add a token. The GitHub Actions workflow will automatically upload coverage reports.

## GitHub Actions Workflow

The `.github/workflows/tests.yml` file runs both backend and frontend tests:

### Backend Tests
- Runs on Python 3.10, 3.11, 3.12, 3.13
- Generates coverage with pytest-cov
- Uploads to Codecov with `flags: backend`

### Frontend Tests
- Runs on Node.js 16
- Generates coverage with Jest
- Uploads to Codecov with `flags: frontend`

## Viewing Coverage

### Local Coverage Reports

**Backend:**
```bash
cd backend
make test-pytest
# Then open: htmlcov/index.html in your browser
```

**Frontend:**
```bash
cd frontend
npm test -- --coverage --watchAll=false
# Then open: coverage/lcov-report/index.html in your browser
```

### Codecov Dashboard

1. Visit https://codecov.io/gh/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME
2. View coverage by:
   - Overall coverage percentage
   - By file/folder
   - By commit (in PRs)
   - By branch
   - Coverage trends over time

### Coverage Badges

Add coverage badges to your README.md:

**Backend:**
```markdown
[![Backend Coverage](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO/branch/develop/graph/badge.svg?flag=backend)](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO)
```

**Frontend:**
```markdown
[![Frontend Coverage](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO/branch/develop/graph/badge.svg?flag=frontend)](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO)
```

## Coverage Targets

Aim for the following coverage levels:

| Component | Target Coverage | Current |
|-----------|-----------------|---------|
| Backend   | 80%+            | TBD     |
| Frontend  | 80%+            | TBD     |

## Troubleshooting

### Coverage not uploading?

1. **Check GitHub Actions logs:**
   - Go to your repo → Actions → select the workflow run
   - Look for errors in "Upload coverage to Codecov" step

2. **Verify token is set:**
   - GitHub Settings → Secrets → Check CODECOV_TOKEN exists

3. **Check coverage file exists:**
   - Backend: `backend/coverage.xml`
   - Frontend: `frontend/coverage/lcov.info`

4. **For public repos, try running without token:**
   - Remove the token reference from the workflow
   - Codecov auto-detects public repos

### Still having issues?

- Visit Codecov docs: https://docs.codecov.com
- Check GitHub Actions documentation for debugging
- Verify coverage files are being generated locally first

## Coverage Best Practices

1. **Write tests as you code** - Don't leave testing until the end
2. **Aim for meaningful coverage** - 100% coverage ≠ good tests
3. **Test error cases** - Not just the happy path
4. **Keep coverage targets realistic** - Start with 50-60%, grow to 80%+
5. **Review coverage in PRs** - Use Codecov's PR comments to catch drops

## More Information

- Codecov Docs: https://docs.codecov.com
- Jest Coverage: https://jestjs.io/docs/coverage
- Pytest Coverage: https://pytest-cov.readthedocs.io
