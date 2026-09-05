# Business Decisions - API Design Overhaul

## Overview
Redesigning trivia API to implement server-side answer validation, secure score tracking, and complete user management. This document captures 5 major departures from the original starter code design.

---

## Decision 1: Question Search via GET (Not POST)

**Change:** Move search functionality from POST /questions to query parameter on GET /questions

**Original Design:** 
- POST /questions with `searchTerm` field for searching
- POST /questions without `searchTerm` creates new question

**New Design:**
- `GET /questions?page=1&search=partial_term` - Search questions
- `POST /questions` - Create new question only

**Rationale:**
- Better REST semantics (GET for retrieval, POST for creation)
- Avoids ambiguous request body interpretation
- Enables proper pagination on search results

**Endpoints Affected:**
- `GET /questions?page=1&search=searchTerm` (change from POST)
- `POST /questions` (simplify: only creates)

---

## Decision 2: Category CRUD Operations

**Change:** Add full CRUD for categories (Create, Read, Update, Delete)

**New Endpoints:**
- `GET /categories` - List all categories (existing, unchanged)
- `GET /categories/<int:id>` - Get single category details
- `POST /categories` - Create new category (admin)
- `PUT /categories/<int:id>` - Update category name (admin)
- `DELETE /categories/<int:id>` - Delete category (with optional cascade)

**Delete Behavior:**
- Default: `DELETE /categories/7` → Fails (422) if category has associated questions (safe)
- Force cascade: `DELETE /categories/7?force=true` → Deletes category AND all associated questions, returns count
- This allows data cleanup without losing functionality, while protecting against accidental deletes

**Rationale:**
- Meets "Stand Out" requirement: "Add capability to create new categories"
- Allows dynamic category management beyond hardcoded seed data
- Follows RESTful CRUD pattern
- Cascade delete with `force` parameter provides flexibility while maintaining safe defaults

---

## Decision 3: Quiz Endpoint Redesign (Persistent Session with Answer Audit Trail)

### Problem with Original Design
- Answer exposed in GET response (F12 key reveals answer)
- Score tracked only in React state (user can fake it)
- No backend validation of answers
- No persistent quiz session (can't catch-up if connection lost)
- No audit trail for quiz attempts
- Violates security principle: never trust client data

### New Secure Design: Persistent Quiz Session

**Three-Endpoint Quiz Session Flow:**

#### Step 1: Create Quiz Session (POST /quizzes)
```
POST /quizzes
{
  "user_id": 1,
  "category_id": 2,
  "number_of_questions": 5
}

Response (201):
{
  "game_session_id": 42,
  "question_number": 1,
  "current_score": {"correct": 0, "total_answered": 0, "total_questions": 5},
  "question": {"id": 7, "question": "What is H2O?", ...}
  // NO ANSWER FIELD!
}
```

#### Step 2: Answer Question (POST /quizzes/42/1)
```
POST /quizzes/42/1
{
  "user_answer": "water"
}

Response (200):
{
  "correct": true,
  "correct_answer": "H2O",
  "current_score": {"correct": 1, "total_answered": 1, "total_questions": 5},
  "question_number": 2,
  "question": {...next question, no answer}
}
```

#### Step 3: Repeat for Each Question (or Catch-Up)
```
GET /games/42 - Returns next unanswered question + current score (recovery/catch-up)
POST /games/42/5 - Answer final question, game auto-completes
```

#### Auto-Completion
When user answers final question (question_number = total_questions):
- Game marked as `completed` in game_sessions table
- GameSession record created with final score
- User.total_score updated += correct_count
- User.games_played incremented
- Next question field returns null

**New Database Tables:**

1. **game_sessions**: Tracks game sessions
   - id, user_id, category_id, number_of_questions, status, created_at, completed_at

2. **game_session_answer**: Audit trail - each answer in a game (CRITICAL - Phase 1b)
   - id, game_session_id, question_number, question_id, question_text (snapshot), user_answer, correct_answer, is_correct, answered_at

**Critical Architectural Dependency:**
The `game_session_answer` table is **NOT optional** — it is required for the game endpoints to function correctly:

- **Question Deduplication**: When `POST /games/:id/:question_number` is called, the endpoint must check `game_session_answer` to see which questions have already been answered in this session. Without this, the same question can be asked twice.

- **Question Tracking**: The game session doesn't store which questions were assigned. Only `game_session_answer` records which questions were asked and answered. This is the source of truth.

- **Next Question Logic**: When returning the next question, the endpoint queries `game_session_answer` to exclude already-answered questions. Without this table, there's no way to prevent duplicates.

- **Catch-Up Capability**: `GET /games/:id` must return the next *unanswered* question. This requires querying `game_session_answer` to find which questions have been answered.

- **Validation**: The endpoint must validate that `question_number` matches the expected sequence (e.g., if 2 questions answered, next must be 3). This data exists only in `game_session_answer`.

**CRUD Operations Required:**

1. **CREATE (POST /games/:id/:question_number)**
   - When user answers a question, insert a new record into `game_session_answer`
   - Stores: question_number, question_id, question_text (snapshot), user_answer, correct_answer, is_correct, answered_at

2. **READ (GET /games/:id for next question)**
   - Query `game_session_answer` to find max(question_number) already answered
   - Exclude question_ids that have been answered in this session
   - Return next question with question_number = max + 1

3. **READ (Validation)**
   - Before accepting an answer, check if this question_number was already answered (prevent re-answers)
   - Check if user is answering in sequence (expected question_number matches)

4. **UPDATE (Not typically needed)**
   - Could update if allowing answer revisions, but current design is append-only

5. **DELETE (Optional cleanup)**
   - Delete all records for a game_session when session is abandoned or deleted

**Benefits:**
- ✅ Answer never exposed to frontend
- ✅ Backend validates every answer
- ✅ Server-side score is authoritative
- ✅ Persistent audit trail (complete question/answer record)
- ✅ Prevents duplicate questions in same game
- ✅ Enables catch-up after connection loss
- ✅ Complete analytics capability (can replay quiz attempts)
- ✅ Question snapshots (if question deleted later, game history still valid)
- ✅ Catch-up capability (GET /games/id recovers lost connection)
- ✅ Supports concurrent quizzes per user
- ✅ Complete analytics data (can replay quiz attempts)

**Error Handling:**
- Re-answering same question → 422 "Question already answered"
- Posting out of sequence → 422 "Expected question X, received Y"
- Quiz already completed → 422 "Quiz session complete"
- Invalid user/category → 404 errors

**Score Format:**
```json
{
  "correct": 3,
  "total_answered": 4,
  "total_questions": 5
}
```
UI calculates percentage (3/5 = 60%) from this data, giving frontend flexibility

---

## Decision 4: User Endpoints (Simple, No Auth)

**Scope:** Username + UserID only, no passwords or authentication for now

**New Endpoints:**
- `GET /users` - List all users with their stats
  ```json
  {
    "users": [
      {
        "id": 1,
        "username": "alice_wonder",
        "total_score": 25,
        "games_played": 5,
        "created_at": "2026-01-15T10:30:00Z"
      }
    ]
  }
  ```

- `GET /users/<int:id>` - Get user details + game history
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
        "score": 5,
        "date_played": "2026-09-04T14:23:00Z"
      }
    ]
  }
  ```

- `POST /users` - Create new user
  ```json
  Request: {"username": "charlie_brown"}
  Response:
  {
    "id": 4,
    "username": "charlie_brown",
    "total_score": 0,
    "games_played": 0,
    "created_at": "2026-09-04T15:00:00Z"
  }
  ```

- `GET /leaderboard` - Top users by total_score
  ```json
  {
    "leaderboard": [
      {"id": 1, "username": "alice_wonder", "total_score": 25},
      {"id": 2, "username": "bob_builder", "total_score": 18},
      {"id": 3, "username": "diana_prince", "total_score": 15}
    ]
  }
  ```

**Rationale:**
- Supports "INTENSE" feature: track user game scores
- Simple design for now (no auth, no passwords)
- Allows score persistence to User.total_score when GameSession created
- User ID becomes required for POST /games (starting a game session)
- Frontend will eventually need to create/select user before quiz

---

## Decision 5: Python Runtime Baseline (3.10+)

**Change:** Standardize project runtime on Python 3.10+ instead of 3.7.

**Context:**
- Assignment starter materials referenced Python 3.7.
- Python 3.7 is end-of-life and no longer maintained.

**Decision:**
- Use Python 3.10 as the minimum supported runtime for local development and CI.
- Do not target Python 3.7 compatibility in this project pass.

**Rationale:**
- 3.10 is the lowest currently supported baseline that keeps dependencies and tooling stable.
- Reduces risk from unsupported runtime behavior and package incompatibilities.
- Keeps environment expectations clear for contributors and reviewers.

**Operational Impact:**
- Documentation and setup instructions must explicitly call out Python 3.10+.
- CI and test commands should run against Python 3.10 as the required baseline.

---

## Complete Quiz Flow (User Perspective)

### Current Flow (Vulnerable)
- Frontend: GET /games → receives answer (SECURITY ISSUE)
2. Frontend: Evaluate answer locally (cheatable)
3. Frontend: Track score in React state (mutable)
4. Frontend: After quiz, show final score (no server validation)

### New Flow (Secure with Persistent Sessions)
1. **Setup:** User selects/creates account
   - POST /users → get user_id
   - GET /categories → select category
   
2. **Create Quiz Session:**
   - POST /games with user_id, category_id, number_of_questions
   - Backend returns quiz_session_id + first question (no answer)
   - Creates quiz_session record in DB
   
3. **Quiz Loop (each question):**
   - User sees question (no answer exposed)
   - User types answer
   - Frontend: POST /games/<session_id>/<question_number> with user_answer
   - Backend: Validates against DB answer, creates quiz_session_answer record
   - Backend: Returns {correct: true/false, correct_answer, current_score: {...}, next_question}
   - Frontend: Display current score (informational only, server is authoritative)
   
4. **Quiz Completion (auto on final question):**
   - When user answers question_number = total_questions:
     - Quiz marked as completed
     - GameSession record created with final correct_count
     - User.total_score updated, User.games_played incremented
     - Next question field returns null
   
5. **Connection Loss Recovery:**
   - Frontend: GET /games/<session_id>
   - Backend: Returns next unanswered question + current score
   - User can catch up mid-quiz

6. **View Stats:**
   - Frontend: GET /users/<user_id> or GET /leaderboard
   - Display user stats + game history with audit trail

---

## Endpoint Summary (All Changes)

### Existing (Unchanged)
- ✅ `GET /categories` - Return all categories

### Modified
- ⚠️ `GET /questions?page=1&search=term` (was POST, now GET with query params)
- ⚠️ `POST /questions` (now create-only, removed search logic)

### New (Added)
- 🆕 `GET /categories/<int:id>` - Get category details
- 🆕 `POST /categories` - Create category
- 🆕 `PUT /categories/<int:id>` - Update category
- 🆕 `DELETE /categories/<int:id>` - Delete category

- 🆕 `POST /games` - Create game session (returns first question, no answer)
- 🆕 `GET /games/<int:game_session_id>` - Get current game state (catch-up)
- 🆕 `POST /games/<int:game_session_id>/<int:question_number>` - Answer question, return next

- 🆕 `GET /users` - List all users
- 🆕 `GET /users/<int:id>` - Get user details + history
- 🆕 `POST /users` - Create user
- 🆕 `GET /leaderboard` - Top users by score

### Existing (Unchanged)
- ✅ `GET /questions/<int:id>` - Get single question
- ✅ `DELETE /questions/<int:id>` - Delete question
- ✅ `GET /categories/<int:id>/questions` - Get questions by category

---

## Implementation Order (Recommended)

### Phase 3a: Core Endpoints (GET/DELETE - Safe)
1. GET /categories (verify existing works)
2. GET /questions (verify existing works with search param)
3. DELETE /questions/<id> (verify existing works)
4. GET /categories/<id>/questions (verify existing works)

### Phase 3b: Category Management (CRUD)
5. GET /categories/<id>
6. POST /categories
7. PUT /categories/<id>
8. DELETE /categories/<id> (with optional force cascade delete)

### Phase 3c: User Endpoints (Simple CRUD)
9. POST /users - Create user
10. GET /users - List users
11. GET /users/<id> - Get user details
12. GET /leaderboard - Top users

### Phase 3d: Question Creation
13. POST /questions - Create new question

### Phase 1b: Game Session Answer Audit Table (CRITICAL PREREQUISITE)
**Blocked By:** Phase 1 (users, categories, questions exist)
**Blocks:** All game/quiz endpoints (POST /games, GET /games/:id)
**What:** Create game_session_answer model, repository, service, and CRUD operations
**Why:** Required for question deduplication, next-question logic, and catch-up capability

### Phase 2: Game/Quiz Endpoints (Now with audit tracking)
**Depends On:** Phase 1b (game_session_answer table)
**What:** Implement POST /games, GET /games/:id, POST /games/:id/:question_number
**Enhanced By:** Audit trail prevents duplicates and enables validation

### Phase 3e: Persistent Quiz Session (New Design)
14. POST /games - Create game session, return first question
15. GET /games/<id> - Catch-up endpoint (get current state)
16. POST /games/<id>/<question_number> - Answer question, return next + score

### Phase 3f: Error Handlers (All Phases)
- 404, 422, 400, 500 error handlers

---

## Frontend Impact (To Be Done Later)

- Game component uses persistent session architecture (game_session_id persisted)
- No longer has access to answer in state (security win!)
- Must create user before quiz (new flow)
- Score displayed locally from API response `{correct: 3, total_answered: 4, total_questions: 5}` (UI calculates %)
- Server score is authoritative (not React state)
- Connection recovery: GET /games/<session_id> catches up mid-game
- After final question answered, quiz auto-completes (no additional call needed)
- New user select/create UI before quiz start
- New leaderboard view (GET /leaderboard)
- User profile view (GET /users/<id> with game history)
- Quiz history/replay capability (quiz_session_answer table has all answers)

---

## Database Impact

**Existing Tables (No Changes):**
- Question (has id, question, answer, category, difficulty, rating)
- Category (has id, type)
- User (has id, username, email, total_score, games_played, created_at)

**New Tables for Quiz Sessions:**
- quiz_session: id, user_id, category_id, number_of_questions, status, created_at, completed_at
- quiz_session_answer: id, quiz_session_id, question_number, question_id, question_text (snapshot), user_answer, correct_answer, is_correct, answered_at

**Relationships:**
- quiz_session.user_id → User.id
- quiz_session.category_id → Category.id
- quiz_session_answer.quiz_session_id → quiz_session.id
- quiz_session_answer.question_id → Question.id

**Why New Tables:**
- ✅ Persistent quiz session (can catch-up if connection lost)
- ✅ Complete audit trail (every answer recorded)
- ✅ Question snapshots (if question deleted later, quiz history preserved)
- ✅ Analytics capable (can analyze quiz attempts, correct/incorrect patterns)
- ✅ No duplicate answers (FK constraint prevents re-answering)

---

## Testing Strategy

**Backend Tests (pytest):**
- Quiz endpoints: 
  - POST /games creates session with first question (no answer)
  - GET /games/<id> returns current state and next unanswered question
  - POST /games/<id>/<number> validates answers, prevents re-answers
  - Auto-completion when final question answered
  - Catch-up recovery works
- User endpoints: CRUD operations, unique constraint
- Category CRUD: Create, update, delete (with cascade test)
- GameSession: Auto-created on quiz completion, User stats updated

**Frontend Tests:** (Later phase)
- Quiz flow: Create quiz, answer questions, see validated responses
- User creation/selection before quiz
- Connection loss recovery (GET /games/<id>)
- Score display calculation from {correct, total_answered, total_questions}
- Leaderboard and user profile views

---

## Security Decisions Made

1. **Never return answer in GET requests** - Answer validation only server-side
2. **Score calculated server-side** - Frontend cannot manipulate score
3. **GameSession persists validated score** - Audit trail exists
4. **No authentication yet** - Simple username only (scope limitation)

---

## Known Scope Limitations

- No authentication/authorization (future enhancement)
- No password or login required (simple for now)
- User can create quiz under any username (not restricted)
- No admin designation yet for category CRUD (assumed future enhancement)
