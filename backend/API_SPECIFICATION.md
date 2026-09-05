# API Endpoints Specification

## Overview
Complete REST API specification for Trivia application with 17 total endpoints across 5 resource categories.

**Contract Status:** Active source of truth  
**Version:** v1.0  
**Last Updated:** 2026-09-05

---

## 1. CATEGORIES ENDPOINTS

### GET /categories
**Description:** Retrieve all categories

**Method:** GET
**URL:** `/categories`

**Request Parameters:** None

**Response (Success - 200):**
```json
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "success": true
}
```

**Errors:**
- 500: Internal server error

---

### GET /categories/:id
**Description:** Retrieve a single category by ID

**Method:** GET
**URL:** `/categories/<int:id>`
**Example:** `/categories/2`

**Request Parameters:** None (ID in URL path)

**Response (Success - 200):**
```json
{
  "id": 2,
  "type": "Art",
  "success": true
}
```

**Errors:**
- 404: Category not found

---

### POST /categories
**Description:** Create a new category

**Method:** POST
**URL:** `/categories`

**Request Body (JSON):**
```json
{
  "type": "Technology"
}
```

**Required Fields:**
- `type` (string, trimmed, 1-100 chars): Category name

**Response (Success - 201):**
```json
{
  "id": 7,
  "type": "Technology",
  "success": true
}
```

**Errors:**
- 400: Missing or invalid 'type' field
- 422: Category name already exists (duplicate)
- 422: Category name violates validation constraints

---

### PUT /categories/:id
**Description:** Update an existing category

**Method:** PUT
**URL:** `/categories/<int:id>`
**Example:** `/categories/7`

**Request Body (JSON):**
```json
{
  "type": "Modern Tech"
}
```

**Required Fields:**
- `type` (string, non-empty): Updated category name

**Response (Success - 200):**
```json
{
  "id": 7,
  "type": "Modern Tech",
  "success": true
}
```

**Errors:**
- 404: Category not found
- 400: Missing or invalid 'type' field
- 422: New name conflicts with existing category

---

### DELETE /categories/:id
**Description:** Delete a category

**Method:** DELETE
**URL:** `/categories/<int:id>`
**Example:** `/categories/7`

**Request Parameters:** Category ID in URL path

**Response (Success - 200):**
```json
{
  "deleted": 7,
  "success": true
}
```

**Behavior:**
- Delete only if no questions exist in the category
- If category has one or more linked questions, return 422

**Errors:**
- 404: Category not found
- 422: Category has associated questions

---

## 2. QUESTIONS ENDPOINTS

### GET /questions
**Description:** Retrieve paginated questions with optional search filter

**Method:** GET
**URL:** `/questions?page=1&search=water`

**Query Parameters:**
- `page` (integer, optional, default=1): Page number (10 questions per page)
- `search` (string, optional): Partial search term (case-insensitive substring match)

**Response (Success - 200):**
```json
{
  "questions": [
    {
      "id": 1,
      "question": "What is H2O?",
      "category": 1,
      "difficulty": 2,
      "rating": 4.5
    },
    {
      "id": 5,
      "question": "What is H2SO4?",
      "category": 1,
      "difficulty": 3,
      "rating": 3.2
    }
  ],
  "total_questions": 12,
  "current_page": 1,
  "total_pages": 2,
  "categories": {
    "1": "Science",
    "2": "Art"
  },
  "success": true
}
```

**Errors:**
- 404: Page out of range
- 400: Invalid page parameter

---

### GET /categories/:id/questions
**Description:** Retrieve questions filtered by category (paginated)

**Method:** GET
**URL:** `/categories/<int:id>/questions?page=1`
**Example:** `/categories/1/questions?page=1`

**Query Parameters:**
- `page` (integer, optional, default=1): Page number

**Request Parameters:** Category ID in URL path

**Response (Success - 200):**
```json
{
  "questions": [
    {
      "id": 1,
      "question": "What is H2O?",
      "category": 1,
      "difficulty": 2,
      "rating": 4.5
    }
  ],
  "total_questions": 3,
  "current_page": 1,
  "total_pages": 1,
  "current_category": "Science",
  "success": true
}
```

**Errors:**
- 404: Category not found
- 200: Category found but no questions returns empty `questions` with `total_questions: 0`
- 400: Invalid page parameter

---

### POST /questions
**Description:** Create a new question

**Method:** POST
**URL:** `/questions`

**Request Body (JSON):**
```json
{
  "question": "What is the chemical formula for water?",
  "answer": "H2O",
  "category": 1,
  "difficulty": 2,
  "rating": 0
}
```

**Required Fields:**
- `question` (string, trimmed, 1-500 chars): Question text
- `answer` (string, trimmed, 1-500 chars): Answer text
- `category` (integer): Category ID (must exist)
- `difficulty` (integer, 1-5): Difficulty level

**Optional Fields:**
- `rating` (float, default=0, range 0.0-5.0): Initial rating

**Response (Success - 201):**
```json
{
  "id": 25,
  "question": "What is the chemical formula for water?",
  "answer": "H2O",
  "category": 1,
  "difficulty": 2,
  "rating": 0,
  "success": true
}
```

**Errors:**
- 400: Missing required fields
- 422: Invalid category ID (category doesn't exist)
- 422: Invalid difficulty (not 1-5)
- 422: Field value violates validation constraints

---

### GET /questions/:id
**Description:** Retrieve a single question by ID

**Method:** GET
**URL:** `/questions/<int:id>`
**Example:** `/questions/5`

**Request Parameters:** Question ID in URL path

**Response (Success - 200):**
```json
{
  "id": 5,
  "question": "What is H2SO4?",
  "answer": "Sulfuric acid",
  "category": 1,
  "difficulty": 3,
  "rating": 3.2,
  "success": true
}
```

**Errors:**
- 404: Question not found

---

### DELETE /questions/:id
**Description:** Delete a question by ID

**Method:** DELETE
**URL:** `/questions/<int:id>`
**Example:** `/questions/5`

**Request Parameters:** Question ID in URL path

**Response (Success - 200):**
```json
{
  "deleted": 5,
  "success": true
}
```

**Errors:**
- 404: Question not found

---

## 3. GAME ENDPOINTS (Persistent Session with Answer Tracking)

### POST /games
**Description:** Create a new game session and return the first question

**Method:** POST
**URL:** `/games`

**Request Body (JSON):**
```json
{
  "user_id": 1,
  "category_id": 2,
  "number_of_questions": 5
}
```

**Required Fields:**
- `user_id` (integer): User starting the game
- `category_id` (integer): Category ID (0 for all categories)

**Optional Fields:**
- `number_of_questions` (integer, default=5): Number of questions in game (1-20)

**Response (Success - 201):**
```json
{
  "game_session_id": 42,
  "question_number": 1,
  "current_score": {
    "correct": 0,
    "total_answered": 0,
    "total_questions": 5
  },
  "question": {
    "id": 7,
    "question": "What is H2O?",
    "category": 2,
    "difficulty": 2,
    "rating": 4.5
  },
  "success": true
}
```

**Note:** Answer field is NEVER included in response for security reasons

**Errors:**
- 400: Missing required fields
- 404: User not found
- 404: Category not found (if category_id != 0)
- 422: Invalid number_of_questions (must be 1-20)

---

### GET /games/:game_session_id
**Description:** Get current game state and next unanswered question (catch-up endpoint)

**Method:** GET
**URL:** `/games/<int:game_session_id>`
**Example:** `/games/42`

**Response (Success - 200):**
```json
{
  "game_session_id": 42,
  "question_number": 3,
  "current_score": {
    "correct": 2,
    "total_answered": 2,
    "total_questions": 5
  },
  "question": {
    "id": 15,
    "question": "What is the capital of France?",
    "category": 3,
    "difficulty": 1,
    "rating": 4.8
  },
  "success": true
}
```

**Response (Game Completed - 200):**
```json
{
  "game_session_id": 42,
  "status": "completed",
  "current_score": {
    "correct": 4,
    "total_answered": 5,
    "total_questions": 5
  },
  "message": "Game completed",
  "success": true
}
```

**Use Cases:**
- User lost connection, needs to catch up
- Frontend refresh, needs current state
- Check game completion status

**Errors:**
- 404: Game session not found

---

### POST /games/:game_session_id/:question_number
**Description:** Answer a game question and get the next question

**Method:** POST
**URL:** `/games/<int:game_session_id>/<int:question_number>`
**Example:** `/games/42/1`

**Request Body (JSON):**
```json
{
  "user_answer": "water"
}
```

**Required Fields:**
- `user_answer` (string): User's answer text

**Response (Answer Correct, More Questions - 200):**
```json
{
  "game_session_id": 42,
  "answered_question_number": 1,
  "correct": true,
  "correct_answer": "H2O",
  "current_score": {
    "correct": 1,
    "total_answered": 1,
    "total_questions": 5
  },
  "next_question_number": 2,
  "question": {
    "id": 15,
    "question": "What is the capital of France?",
    "category": 3,
    "difficulty": 1,
    "rating": 4.8
  },
  "success": true
}
```

**Response (Answer Correct, Game Complete - 200):**
```json
{
  "game_session_id": 42,
  "answered_question_number": 5,
  "correct": true,
  "correct_answer": "Paris",
  "current_score": {
    "correct": 4,
    "total_answered": 5,
    "total_questions": 5
  },
  "status": "completed",
  "next_question_number": null,
  "question": null,
  "success": true
}
```

**Response (Answer Incorrect - 200):**
```json
{
  "game_session_id": 42,
  "answered_question_number": 2,
  "correct": false,
  "correct_answer": "Paris",
  "current_score": {
    "correct": 1,
    "total_answered": 2,
    "total_questions": 5
  },
  "next_question_number": 3,
  "question": {
    "id": 22,
    "question": "What is 2+2?",
    "category": 1,
    "difficulty": 1,
    "rating": 4.9
  },
  "success": true
}
```

**Answer Matching Logic:**
- Answer is normalized (lowercase, special characters removed)
- User answer is normalized the same way
- Substring matching: all words in correct answer must appear in user answer
- Example: "h2o", "H2O", "water molecule h2o" all match "H2O"

**Auto-completion:**
- When final question (question_number = total_questions) is answered:
  - Game automatically marked as completed
  - User.total_score updated with final correct count
  - User.games_played incremented
  - GameSession and GameSessionAnswer records form the complete audit trail
  - Next question field returns null

**Errors:**
- 400: Missing user_answer field
- 404: Game session not found
- 404: Question not found
- 422: Game already completed
- 422: Question already answered (re-answer attempt)
- 422: Invalid question_number (expected question X, got Y)

---

## 4. USER ENDPOINTS

### POST /users
**Description:** Create a new user

**Method:** POST
**URL:** `/users`

**Request Body (JSON):**
```json
{
  "username": "alice_wonder"
}
```

**Required Fields:**
- `username` (string, trimmed, 3-50 chars): Unique username

**Response (Success - 201):**
```json
{
  "id": 4,
  "username": "alice_wonder",
  "total_score": 0,
  "games_played": 0,
  "created_at": "2026-09-04T15:00:00Z",
  "success": true
}
```

**Errors:**
- 400: Missing or empty 'username'
- 422: Username already exists
- 422: Username violates validation constraints (for example length)

---

### GET /users
**Description:** List all users with their statistics

**Method:** GET
**URL:** `/users`

**Request Parameters:** None

**Query Parameters:**
- `sort` (string, optional, default='created_at'): Sort by 'created_at', 'total_score', or 'games_played'
- `order` (string, optional, default='asc'): Sort order 'asc' or 'desc'

**Response (Success - 200):**
```json
{
  "users": [
    {
      "id": 1,
      "username": "alice_wonder",
      "total_score": 25,
      "games_played": 5,
      "created_at": "2026-01-15T10:30:00Z"
    },
    {
      "id": 2,
      "username": "bob_builder",
      "total_score": 18,
      "games_played": 4,
      "created_at": "2026-02-20T12:45:00Z"
    }
  ],
  "total_users": 4,
  "success": true
}
```

**Errors:**
- 400: Invalid sort or order parameter

---

### GET /users/:id
**Description:** Get user details and game history

**Method:** GET
**URL:** `/users/<int:id>`
**Example:** `/users/1`

**Request Parameters:** User ID in URL path

**Response (Success - 200):**
```json
{
  "id": 1,
  "username": "alice_wonder",
  "total_score": 25,
  "games_played": 5,
  "created_at": "2026-01-15T10:30:00Z",
  "game_sessions": [
    {
      "id": 5,
      "category_id": 2,
      "category_type": "Art",
      "score": 5,
      "questions_answered": 5,
      "correct_answers": 5,
      "date_played": "2026-09-04T14:23:00Z"
    },
    {
      "id": 4,
      "category_id": 1,
      "category_type": "Science",
      "score": 3,
      "questions_answered": 5,
      "correct_answers": 3,
      "date_played": "2026-09-03T10:15:00Z"
    }
  ],
  "success": true
}
```

**Errors:**
- 404: User not found

---

### GET /users/leaderboard
**Description:** Get top users ranked by total score

**Method:** GET
**URL:** `/users/leaderboard`

**Query Parameters:**
- `limit` (integer, optional, default=10): Number of top users to return
- `offset` (integer, optional, default=0): Pagination offset

**Response (Success - 200):**
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "id": 1,
      "username": "alice_wonder",
      "total_score": 25,
      "games_played": 5
    },
    {
      "rank": 2,
      "id": 2,
      "username": "bob_builder",
      "total_score": 18,
      "games_played": 4
    },
    {
      "rank": 3,
      "id": 3,
      "username": "charlie_brown",
      "total_score": 15,
      "games_played": 3
    }
  ],
  "total_users": 4,
  "success": true
}
```

**Errors:**
- 400: Invalid limit or offset

---

## 5. ERROR HANDLERS (All Endpoints)

### 400 Bad Request
**Response:**
```json
{
  "error": 400,
  "message": "Bad Request - {details}",
  "success": false
}
```

**Causes:**
- Missing required fields in POST/PUT
- Invalid parameter types
- Malformed JSON

---

### 404 Not Found
**Response:**
```json
{
  "error": 404,
  "message": "Resource not found - {resource type} with id {id}",
  "success": false
}
```

**Causes:**
- Question/Category/User ID doesn't exist
- Page number out of range
- Category has no questions

---

### 422 Unprocessable Entity
**Response:**
```json
{
  "error": 422,
  "message": "Unprocessable Entity - {details}",
  "success": false
}
```

**Causes:**
- Duplicate category name
- Duplicate username
- Invalid foreign key (category doesn't exist)
- Category cannot be deleted (has questions)
- Invalid difficulty value
- Invalid score value

---

### 500 Internal Server Error
**Response:**
```json
{
  "error": 500,
  "message": "Internal Server Error - {details}",
  "success": false
}
```

**Causes:**
- Database errors
- Unexpected exceptions

---

## ENDPOINT SUMMARY TABLE

| # | Method | Endpoint | Description | Status |
|---|--------|----------|-------------|--------|
| 1 | GET | `/categories` | List all categories | Existing |
| 2 | GET | `/categories/<id>` | Get category details | New |
| 3 | POST | `/categories` | Create category | New |
| 4 | PUT | `/categories/<id>` | Update category | New |
| 5 | DELETE | `/categories/<id>` | Delete category (fails with 422 if linked questions exist) | New |
| 6 | GET | `/questions` | List paginated questions (with search) | Modified |
| 7 | GET | `/categories/<id>/questions` | Get questions by category | Existing |
| 8 | POST | `/questions` | Create question | Modified |
| 9 | GET | `/questions/<id>` | Get question by ID | Existing |
| 10 | DELETE | `/questions/<id>` | Delete question | Existing |
| 11 | POST | `/games` | Create game session, return first question | New |
| 12 | GET | `/games/<id>` | Get current game state (catch-up) | New |
| 13 | POST | `/games/<id>/<question_number>` | Answer question, return next | New |
| 14 | POST | `/users` | Create user | New |
| 15 | GET | `/users` | List all users | New |
| 16 | GET | `/users/<id>` | Get user + game history | New |
| 17 | GET | `/users/leaderboard` | Top users by score | New |

**Total: 17 endpoints**

---

## Key Security Decisions

1. **Answer Never Exposed**: POST /games and GET /games/<id> do NOT return an answer field
2. **Server-Side Validation**: POST /games/<game_session_id>/<question_number> validates all answers
3. **Authoritative Score**: Database score is source of truth, not client state
4. **Audit Trail**: GameSessionAnswer records each served question and submitted answer per game session
5. **No Authentication (Current Phase)**: Username-only, no passwords

---

## Data Flow Example: Complete Game Session

```
1. User creates account
   POST /users {"username": "alice"}
   → {id: 1, username: "alice", total_score: 0, ...}

2. User selects category and starts game
   GET /categories
   → {categories: {1: "Science", 2: "Art", ...}}

3. Create game session, get first question (NO ANSWER RETURNED)
   POST /games {user_id: 1, category_id: 1, number_of_questions: 5}
   → {
       game_session_id: 42,
       question_number: 1,
       current_score: {correct: 0, total_answered: 0, total_questions: 5},
       question: {id: 7, question: "What is H2O?", ...}
     }

4. User answers Question 1
   POST /games/42/1 {user_answer: "water"}
   → {
       correct: true,
       correct_answer: "H2O",
     current_score: {correct: 1, total_answered: 1, total_questions: 5},
     next_question_number: 2,
       question: {id: 15, question: "What is the capital of France?", ...}
     }

5. User answers Question 2 (incorrect)
   POST /games/42/2 {user_answer: "london"}
   → {
       correct: false,
       correct_answer: "Paris",
     current_score: {correct: 1, total_answered: 2, total_questions: 5},
     next_question_number: 3,
       question: {id: 22, question: "What is 2+2?", ...}
     }

6. Repeat for questions 3, 4...

7. User answers final Question 5 (correct)
  POST /games/42/5 {user_answer: "4"}
   → {
       correct: true,
       correct_answer: "4",
       current_score: {correct: 4, total_answered: 5, total_questions: 5},
     status: "completed",
     next_question_number: null,
       question: null
     }
   
   Backend automatically:
  - Marks game_session as completed
  - Persists final score (4 correct answers)
   - Updates User: total_score = 0 + 4 = 4, games_played = 0 + 1 = 1

8. Frontend can optionally catch up (if connection lost)
  GET /games/42
   → Shows current score and next unanswered question (or completion status)

9. View user stats
   GET /users/1
   → {id: 1, username: "alice", total_score: 4, games_played: 1, game_sessions: [...]}

10. View leaderboard
  GET /users/leaderboard
    → {leaderboard: [{rank: 1, username: "alice", total_score: 4}, ...]}
```

**Key Points:**
- Game session is persistent (can catch-up with GET)
- Answer validation is server-side (user never sees answer)
- Score tracks correct/total_answered/total_questions (UI calculates %)
- Auto-completion: final question answer triggers GameSession creation and User stats update
- Each answer creates audit record in game_session_answer table


---

## Testing Strategy by Endpoint Category

### Categories (5 endpoints)
- ✅ Test GET all → returns all 6 seed categories
- ✅ Test GET by ID → returns specific category
- ✅ Test POST create → creates new, increments ID
- ✅ Test PUT update → updates name
- ✅ Test DELETE → succeeds if no questions, fails if has questions
- ✅ Test POST duplicate → 422 error
- ✅ Test error cases: 404 (not found), 400 (bad data)

### Questions (4 endpoints)
- ✅ Test GET paginated → returns 10 per page
- ✅ Test GET search → filters by substring
- ✅ Test GET by category → returns only category questions
- ✅ Test POST create → creates question, links to category
- ✅ Test DELETE → removes question
- ✅ Test error cases: 404, 422 (bad category ID), 400 (missing fields)

### Games (3 endpoints)
- ✅ Test GET game state → returns question WITHOUT answer
- ✅ Test GET game state excludes already answered questions
- ✅ Test POST answer validation → correct/incorrect logic
- ✅ Test answer matching → handles case, special chars, word order
- ✅ Test POST game session create → creates record, updates user stats
- ✅ Test error cases: 404 (user/category), 422 (invalid data)

### Users (4 endpoints)
- ✅ Test POST create → creates user with stats
- ✅ Test GET all → returns all users
- ✅ Test GET by ID → returns user + game history
- ✅ Test GET leaderboard → returns sorted by score
- ✅ Test duplicate username → 422 error
- ✅ Test error cases: 404 (not found), 400 (bad data)

---

## Database Schema

**Existing Tables (No Changes):**
- `categories`: id, type
- `questions`: id, question, answer, category_id (FK), difficulty, rating
- `users`: id, username, email, total_score, games_played, created_at

**Required Tables:**

## Normative Data Validation Constraints

These constraints are part of the API contract and MUST be enforced at the database layer (PostgreSQL), in addition to service-layer validation.

### users
- `username`:
  - NOT NULL
  - CHECK `char_length(btrim(username)) BETWEEN 3 AND 50`
  - UNIQUE (case-insensitive uniqueness recommended via unique index on `lower(btrim(username))`)
- `total_score`:
  - NOT NULL
  - CHECK `total_score >= 0`
- `games_played`:
  - NOT NULL
  - CHECK `games_played >= 0`

### categories
- `type`:
  - NOT NULL
  - CHECK `char_length(btrim(type)) BETWEEN 1 AND 100`
  - UNIQUE (case-insensitive uniqueness recommended via unique index on `lower(btrim(type))`)

### questions
- `question`:
  - NOT NULL
  - CHECK `char_length(btrim(question)) BETWEEN 1 AND 500`
- `answer`:
  - NOT NULL
  - CHECK `char_length(btrim(answer)) BETWEEN 1 AND 500`
- `difficulty`:
  - NOT NULL
  - CHECK `difficulty BETWEEN 1 AND 5`
- `rating`:
  - CHECK `rating BETWEEN 0.0 AND 5.0`
- `category`:
  - NOT NULL
  - FOREIGN KEY to `categories(id)`

### game_sessions
- `user_id`:
  - NOT NULL
  - FOREIGN KEY to `users(id)`
- `score`:
  - NOT NULL
  - CHECK `score >= 0`
- `number_of_questions`:
  - NOT NULL
  - CHECK `number_of_questions BETWEEN 1 AND 20`
- `category_id`:
  - NULL allowed for all-category games
  - If non-null, FOREIGN KEY to `categories(id)`

### game_session_answer
- `game_session_id`:
  - NOT NULL
  - FOREIGN KEY to `game_sessions(id)` with CASCADE DELETE
- `question_number`:
  - NOT NULL
  - CHECK `question_number >= 1`
  - UNIQUE composite constraint with `game_session_id`
- `question_id`:
  - NOT NULL
  - FOREIGN KEY to `questions(id)`
- `question_text`, `user_answer`, `correct_answer`:
  - NOT NULL
  - CHECK `char_length(btrim(<field>)) >= 1`
- `is_correct`:
  - NOT NULL boolean

**Design Rationale:**
The game_sessions table alone cannot track which questions have been answered. Without `game_session_answer`:
- No way to prevent duplicate questions in same session
- No way to find "next unanswered question" for `GET /games/:id`
- No way to validate sequential answering in `POST /games/:id/:question_number`
- No persistent audit trail for incomplete/abandoned games

**Future Enhancements (Non-normative):**
- Status tracking (in_progress, completed, abandoned) - requires v2 data migration
- Admin replay/analytics dashboard
- Question difficulty weighting
- User performance analytics

---

## Implementation Notes

- All timestamps use ISO 8601 format: `2026-09-04T14:23:45Z`
- All IDs are positive integers
- All text fields trimmed (no leading/trailing whitespace)
- Database constraints are authoritative for data integrity; service validation should mirror them for clearer client error messages.
- Pagination: 10 items per page (configurable)
- Answer matching: case-insensitive, special chars stripped, substring matching
- Score format: `{correct: int, total_answered: int, total_questions: int}` (UI calculates percentage)
- Auto-completion: When user answers question_number = total_questions, game marked complete + User stats updated
- Concurrent games: User can have multiple active game_sessions
- Game recovery: GET /games/id always returns next unanswered question or completion status
