# API Development and Documentation Final Project

## Trivia App

Udacity is invested in creating bonding experiences for its employees and students. A bunch of team members got the idea to hold trivia on a regular basis and created a webpage to manage the trivia app and play the game, but their API experience is limited and still needs to be built out.

That's where you come in! Help them finish the trivia app so they can start holding trivia and seeing who's the most knowledgeable of the bunch. The application must:

1. Display questions - both all questions and by category. Questions should show the question, category and difficulty rating by default and can show/hide the answer.
2. Delete questions.
3. Add questions and require that they include question and answer text.
4. Search for questions based on a text query string.
5. Play the quiz game, randomizing either all questions or within a specific category.

Completing this trivia app will give you the ability to structure plan, implement, and test an API - skills essential for enabling your future applications to communicate with others.

## Starting and Submitting the Project

[Fork](https://help.github.com/en/articles/fork-a-repo) the project repository and [clone](https://help.github.com/en/articles/cloning-a-repository) your forked repository to your machine. Work on the project locally and make sure to push all your changes to the remote repository before submitting the link to your repository in the Classroom.

## About the Stack

We started the full stack application for you. It is designed with some key functional areas:

### Backend

The [backend](./backend/README.md) directory contains a partially completed Flask and SQLAlchemy server. You will work primarily in `__init__.py` to define your endpoints and can reference models.py for DB and SQLAlchemy setup. These are the files you'd want to edit in the backend:

1. `backend/flaskr/__init__.py`
2. `backend/test_flaskr.py`

> View the [Backend README](./backend/README.md) for more details.

### Frontend

The [frontend](./frontend/README.md) directory contains a complete React frontend to consume the data from the Flask server. If you have prior experience building a frontend application, you should feel free to edit the endpoints as you see fit for the backend you design. If you do not have prior experience building a frontend application, you should read through the frontend code before starting and make notes regarding:

1. What are the end points and HTTP methods the frontend is expecting to consume?
2. How are the requests from the frontend formatted? Are they expecting certain parameters or payloads?

Pay special attention to what data the frontend is expecting from each API response to help guide how you format your API. The places where you may change the frontend behavior, and where you should be looking for the above information, are marked with `TODO`. These are the files you'd want to edit in the frontend:

1. `frontend/src/components/QuestionView.js`
2. `frontend/src/components/FormView.js`
3. `frontend/src/components/QuizView.js`

By making notes ahead of time, you will practice the core skill of being able to read and understand code and will have a simple plan to follow to build out the endpoints of your backend API.

> View the [Frontend README](./frontend/README.md) for more details.

## Security Implementation (Phase 6)

This project includes security hardening measures to protect against common API vulnerabilities:

### CORS Configuration
- **Development**: CORS allows all origins (`*`) for local development
- **Production**: CORS restricted to configured origins via `CORS_ALLOWED_ORIGINS` environment variable
- **Default Production**: `http://localhost:3000`
- **Configuration**: Set `FLASK_ENV=production` and `CORS_ALLOWED_ORIGINS=https://yourdomain.com` in production

### Rate Limiting
- Answer submission endpoint (`POST /games/<id>/<question_number>`) rate limited to **30 requests per 60 seconds per IP**
- Returns `429 Too Many Requests` when limit exceeded
- Prevents abuse and brute-force attempts on game endpoints
- Implemented via lightweight in-memory rate limiter (`utils/rate_limit.py`)

### Input Validation
All user input is validated and normalized:
- **Usernames**: 3-50 characters, trimmed, case-sensitive
- **Emails**: Trimmed, converted to lowercase for consistency
- **Questions/Answers**: 1-500 characters, trimmed
- **Categories**: 1-100 characters, trimmed
- **Difficulty**: Integer range 1-5
- **Rating**: Float range 0.0-5.0
- **Game size**: 1-20 questions per game session

Database-level CHECK constraints enforce validation rules as authoritative source of truth.

### Answer Security
- Answers are **never leaked** before user submission
- Questions returned in `/games` and `/games/<id>` endpoints contain no answer field
- Correct answer revealed only after `POST /games/<id>/<question_number>` submission
- Audit trail (`game_session_answers` table) records all answers with immutable snapshots

### Dependency Security
- Backend: All Python dependencies pinned to specific tested versions (no `>=` ranges)
- Frontend: jQuery updated to 3.7.0+ to address XSS vulnerabilities (CVE-2020-11022, CVE-2020-11023)
- Regular audits via `pip audit` (backend) and `npm audit` (frontend)
- Run audits before deployment: 
  ```bash
  # Backend
  cd backend && pip audit
  # Frontend
  cd frontend && npm audit
  ```

### Testing
Security-focused tests validate all hardening measures:
```bash
cd backend
python -m pytest _tests/test_security_phase6.py -v
```

Tests cover:
- CORS configuration by environment
- Rate limiting per-IP and per-resource
- Input validation and normalization
- Answer leakage prevention
- Rate limit headers and retry-after calculations

