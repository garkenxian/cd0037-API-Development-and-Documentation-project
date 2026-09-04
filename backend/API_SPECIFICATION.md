# API Endpoints Specification

## Overview
Complete REST API specification for Trivia Quiz Application with 16 total endpoints across 5 resource categories.

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
- `type` (string, non-empty): Category name

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
**Description:** Delete a category (with optional cascade delete of associated questions)

**Method:** DELETE
**URL:** `/categories/<int:id>`
**Example:** `/categories/7` or `/categories/7?force=true`

**Query Parameters:**
- `force` (boolean, optional, default=false): If true, cascade delete all associated questions

**Request Parameters:** Category ID in URL path

**Response (Success - 200):**
```json
{
  "deleted": 7,
  "success": true
}
```

**Response (Force Delete with Cascading - 200):**
```json
{
  "deleted": 7,
  "questions_deleted": 3,
  "success": true
}
```

**Behavior:**
- If `force=false` (default): Delete only if no questions exist
- If `force=true`: Delete category AND all associated questions

**Errors:**
- 404: Category not found
- 422: Category has associated questions AND force=false

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
- 404: Category not found or no questions in category
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
- `question` (string, non-empty): Question text
- `answer` (string, non-empty): Answer text
- `category` (integer): Category ID (must exist)
- `difficulty` (integer, 1-5): Difficulty level

**Optional Fields:**
- `rating` (float, default=0): Initial rating

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

## 3. QUIZ ENDPOINTS (Persistent Session with Answer Tracking)

### POST /quizzes
**Description:** Create a new quiz session and return the first question

**Method:** POST
**URL:** `/quizzes`

**Request Body (JSON):**
```json
{
  "user_id": 1,
  "category_id": 2,
  "number_of_questions": 5
}
```

**Required Fields:**
- `user_id` (integer): User starting the quiz
- `category_id` (integer): Category ID (0 for all categories)

**Optional Fields:**
- `number_of_questions` (integer, default=5): Number of questions in quiz (1-20)

**Response (Success - 201):**
```json
{
  "quiz_session_id": 42,
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

### GET /quizzes/:quiz_session_id
**Description:** Get current quiz state and next unanswered question (catch-up endpoint)

**Method:** GET
**URL:** `/quizzes/<int:quiz_session_id>`
**Example:** `/quizzes/42`

**Response (Success - 200):**
```json
{
  "quiz_session_id": 42,
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

**Response (Quiz Completed - 200):**
```json
{
  "quiz_session_id": 42,
  "status": "completed",
  "current_score": {
    "correct": 4,
    "total_answered": 5,
    "total_questions": 5
  },
  "message": "Quiz completed",
  "success": true
}
```

**Use Cases:**
- User lost connection, needs to catch up
- Frontend refresh, needs current state
- Check quiz completion status

**Errors:**
- 404: Quiz session not found
- 422: Quiz session already completed

---

### POST /quizzes/:quiz_session_id/:question_number
**Description:** Answer a quiz question and get the next question

**Method:** POST
**URL:** `/quizzes/<int:quiz_session_id>/<int:question_number>`
**Example:** `/quizzes/42/1`

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
  "quiz_session_id": 42,
  "question_number": 1,
  "correct": true,
  "correct_answer": "H2O",
  "current_score": {
    "correct": 1,
    "total_answered": 1,
    "total_questions": 5
  },
  "question_number": 2,
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

**Response (Answer Correct, Quiz Complete - 200):**
```json
{
  "quiz_session_id": 42,
  "question_number": 5,
  "correct": true,
  "correct_answer": "Paris",
  "current_score": {
    "correct": 4,
    "total_answered": 5,
    "total_questions": 5
  },
  "quiz_status": "completed",
  "question_number": 6,
  "question": null,
  "success": true
}
```

**Response (Answer Incorrect - 200):**
```json
{
  "quiz_session_id": 42,
  "question_number": 2,
  "correct": false,
  "correct_answer": "Paris",
  "current_score": {
    "correct": 1,
    "total_answered": 2,
    "total_questions": 5
  },
  "question_number": 3,
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
  - Quiz automatically marked as completed
  - User.total_score updated with final correct count
  - User.games_played incremented
  - GameSession record created with complete audit trail
  - Next question field returns null

**Errors:**
- 400: Missing user_answer field
- 404: Quiz session not found
- 404: Question not found
- 422: Quiz already completed
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
- `username` (string, non-empty): Unique username

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
      "quiz_category": 2,
      "quiz_category_type": "Art",
      "score": 5,
      "questions_answered": 5,
      "correct_answers": 5,
      "date_played": "2026-09-04T14:23:00Z"
    },
    {
      "id": 4,
      "quiz_category": 1,
      "quiz_category_type": "Science",
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

### GET /leaderboard
**Description:** Get top users ranked by total score

**Method:** GET
**URL:** `/leaderboard`

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
| 5 | DELETE | `/categories/<id>` | Delete category (with force cascade) | New |
| 6 | GET | `/questions` | List paginated questions (with search) | Modified |
| 7 | GET | `/categories/<id>/questions` | Get questions by category | Existing |
| 8 | POST | `/questions` | Create question | Modified |
| 9 | DELETE | `/questions/<id>` | Delete question | Existing |
| 10 | POST | `/quizzes` | Create quiz session, return first question | New |
| 11 | GET | `/quizzes/<id>` | Get current quiz state (catch-up) | New |
| 12 | POST | `/quizzes/<id>/<question_number>` | Answer question, return next | New |
| 13 | POST | `/users` | Create user | New |
| 14 | GET | `/users` | List all users | New |
| 15 | GET | `/users/<id>` | Get user + game history | New |
| 16 | GET | `/leaderboard` | Top users by score | New |

**Total: 16 endpoints** (7 new, 2 modified, 7 existing)

---

## Key Security Decisions

1. **Answer Never Exposed**: GET /quizzes does NOT return answer field
2. **Server-Side Validation**: POST /quiz-answer validates all answers
3. **Authoritative Score**: Database score is source of truth, not client state
4. **Audit Trail**: GameSession records every quiz with score
5. **No Authentication (Current Phase)**: Username-only, no passwords

---

## Data Flow Example: Complete Quiz Session

```
1. User creates account
   POST /users {"username": "alice"}
   → {id: 1, username: "alice", total_score: 0, ...}

2. User selects category and starts quiz
   GET /categories
   → {categories: {1: "Science", 2: "Art", ...}}

3. Create quiz session, get first question (NO ANSWER RETURNED)
   POST /quizzes {user_id: 1, category_id: 1, number_of_questions: 5}
   → {
       quiz_session_id: 42,
       question_number: 1,
       current_score: {correct: 0, total_answered: 0, total_questions: 5},
       question: {id: 7, question: "What is H2O?", ...}
     }

4. User answers Question 1
   POST /quizzes/42/1 {user_answer: "water"}
   → {
       correct: true,
       correct_answer: "H2O",
       current_score: {correct: 1, total_answered: 1, total_questions: 5},
       question_number: 2,
       question: {id: 15, question: "What is the capital of France?", ...}
     }

5. User answers Question 2 (incorrect)
   POST /quizzes/42/2 {user_answer: "london"}
   → {
       correct: false,
       correct_answer: "Paris",
       current_score: {correct: 1, total_answered: 2, total_questions: 5},
       question_number: 3,
       question: {id: 22, question: "What is 2+2?", ...}
     }

6. Repeat for questions 3, 4...

7. User answers final Question 5 (correct)
   POST /quizzes/42/5 {user_answer: "4"}
   → {
       correct: true,
       correct_answer: "4",
       current_score: {correct: 4, total_answered: 5, total_questions: 5},
       quiz_status: "completed",
       question_number: 6,
       question: null
     }
   
   Backend automatically:
   - Marks quiz_session as completed
   - Creates game_session record with final score (4)
   - Updates User: total_score = 0 + 4 = 4, games_played = 0 + 1 = 1

8. Frontend can optionally catch up (if connection lost)
   GET /quizzes/42
   → Shows current score and next unanswered question (or completion status)

9. View user stats
   GET /users/1
   → {id: 1, username: "alice", total_score: 4, games_played: 1, game_sessions: [...]}

10. View leaderboard
    GET /leaderboard
    → {leaderboard: [{rank: 1, username: "alice", total_score: 4}, ...]}
```

**Key Points:**
- Quiz session is persistent (can catch-up with GET)
- Answer validation is server-side (user never sees answer)
- Score tracks correct/total_answered/total_questions (UI calculates %)
- Auto-completion: final question answer triggers GameSession creation and User stats update
- Each answer creates audit record in quiz_session_answer table


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

### Quiz (3 endpoints)
- ✅ Test GET quiz → returns question WITHOUT answer
- ✅ Test GET quiz excludes previous → doesn't repeat questions
- ✅ Test POST answer validation → correct/incorrect logic
- ✅ Test answer matching → handles case, special chars, word order
- ✅ Test POST game-session → creates record, updates user stats
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

**New Tables for Quiz Sessions:**

### quiz_session
Tracks overall quiz session information
```
- id (PK)
- user_id (FK → users)
- category_id (FK → categories)
- number_of_questions (integer)
- status (enum: 'in_progress', 'completed', 'abandoned')
- created_at (timestamp)
- completed_at (timestamp, nullable)
```

### quiz_session_answer
Audit trail - each question answered in a quiz
```
- id (PK)
- quiz_session_id (FK → quiz_session)
- question_number (integer) - which question in sequence (1-5, etc)
- question_id (FK → questions)
- question_text (text) - snapshot of question at time of quiz (if deleted later, history preserved)
- user_answer (text)
- correct_answer (text)
- is_correct (boolean)
- answered_at (timestamp)
```

**Relationships:**
- quiz_session.user_id → users.id
- quiz_session.category_id → categories.id (can be NULL for all categories)
- quiz_session_answer.quiz_session_id → quiz_session.id
- quiz_session_answer.question_id → questions.id

**Why This Design:**
- ✅ Persistent audit trail (user can replay quiz)
- ✅ Question snapshots (deleted questions don't break quiz history)
- ✅ Complete answer tracking (for analytics, re-review)
- ✅ Session recovery (GET /quizzes/id catches user up)
- ✅ No duplicate answers (can't re-answer same question)

---

## Implementation Notes

- All timestamps use ISO 8601 format: `2026-09-04T14:23:45Z`
- All IDs are positive integers
- All text fields trimmed (no leading/trailing whitespace)
- Pagination: 10 items per page (configurable)
- Answer matching: case-insensitive, special chars stripped, substring matching
- Score format: `{correct: int, total_answered: int, total_questions: int}` (UI calculates percentage)
- Auto-completion: When user answers question_number = total_questions, quiz marked complete + User stats updated
- Concurrent quizzes: User can have multiple active quiz_sessions
- Quiz recovery: GET /quizzes/id always returns next unanswered question or completion status
