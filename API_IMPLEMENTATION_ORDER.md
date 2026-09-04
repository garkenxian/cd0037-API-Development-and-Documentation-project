# API Implementation Order (Test-Driven, Full Stack)

## Strategy
Each endpoint is implemented in sequence with full end-to-end testing:
1. **Backend:** Implement endpoint + database model + pytest tests
2. **Frontend:** Create/update component to use endpoint
3. **Integration:** Test complete flow from React → API → Database → React response

**Order:** Creates (POST) → Deletes (DELETE) → Reads (GET)

---

## Implementation Sequence

### PHASE 1: CREATE OPERATIONS (POST)

---

## 1️⃣ POST /users - Create User

**Backend Work:**
- Endpoint: `POST /users`
- Request: `{"username": "alice_wonder"}`
- Response: `{id, username, total_score, games_played, created_at, success: true}`
- Database: Insert into users table
- Validation: Check username uniqueness, non-empty
- Error codes: 400 (missing), 422 (duplicate)
- Tests: Success case, duplicate username error, missing field error

**Frontend Work:**
- Component: UserSelector.js (new)
- Feature: Create user input field + submit button
- State: newUsername, loading
- API call: POST /users
- Display: Show success, show error, disable form on error

**Integration Test:**
```
1. User enters "alice_wonder" in UserSelector
2. Frontend POSTs /users {username: "alice_wonder"}
3. Backend creates user in DB
4. Backend returns {id: 1, username: "alice_wonder", total_score: 0, ...}
5. Frontend stores user and proceeds to quiz
```

**Dependencies:** None
**Estimated complexity:** Easy
**Why first:** All other features need users

---

## 2️⃣ POST /categories - Create Category

**Backend Work:**
- Endpoint: `POST /categories`
- Request: `{"type": "Science"}`
- Response: `{id, type, success: true}`
- Database: Insert into categories table
- Validation: Check type non-empty, uniqueness
- Error codes: 400 (missing), 422 (duplicate)
- Tests: Success case, duplicate category error, missing field error

**Frontend Work:**
- Component: CategoryManager.js (new) OR extend FormView
- Feature: Form to create new category
- API call: POST /categories
- Display: Success message, error handling

**Integration Test:**
```
1. Admin submits form: {"type": "Technology"}
2. Frontend POSTs /categories
3. Backend creates category, returns {id: 7, type: "Technology"}
4. Frontend adds to categories list
5. Category appears in dropdown for quiz selection
```

**Dependencies:** None
**Estimated complexity:** Easy
**Why second:** Needed before creating questions and quizzes

---

## 3️⃣ POST /questions - Create Question

**Backend Work:**
- Endpoint: `POST /questions`
- Request: `{question, answer, category, difficulty, rating (optional)}`
- Response: `{id, question, answer, category, difficulty, rating, success: true}`
- Database: Insert into questions table with foreign key to categories
- Validation: Check all required fields, category exists, difficulty 1-5
- Error codes: 400 (missing), 422 (bad category, bad difficulty)
- Tests: Success case, missing field error, invalid category error, invalid difficulty error

**Frontend Work:**
- Component: FormView.js (update existing)
- Feature: Update form to accept category dropdown, difficulty slider
- API call: POST /questions (same as before, just verify it works with new data)
- Display: Success message ("Question added"), error handling

**Integration Test:**
```
1. User fills out form (question, answer, category, difficulty)
2. Frontend POSTs /questions
3. Backend validates category exists (FK constraint)
4. Backend creates question in DB
5. Backend returns {id: 25, question, answer, ...}
6. Frontend clears form, shows success
7. Verify question appears in GET /questions list
```

**Dependencies:** POST /categories (need categories to exist)
**Estimated complexity:** Medium
**Why third:** Questions needed for quizzes

---

## 4️⃣ POST /quizzes - Create Quiz Session

**Backend Work:**
- Endpoint: `POST /quizzes`
- Request: `{user_id, category_id, number_of_questions}`
- Response: `{game_session_id, question_number, current_score: {correct, total_answered, total_questions}, question: {...no answer}, success: true}`
- Database: Insert into quiz_session table, randomly select first question
- Validation: Check user exists, category exists (0 = all), number_of_questions valid (1-20)
- Error codes: 400 (missing), 404 (user/category), 422 (invalid count)
- Tests: Success case, invalid user error, invalid category error, invalid count error

**Frontend Work:**
- Component: QuizView.js (rewrite)
- Feature: Category selection + quiz start button
- API call: POST /quizzes
- Display: Store game_session_id, show first question (no answer shown)

**Integration Test:**
```
1. User logged in as alice_wonder (user_id: 1)
2. User selects "Science" category (category_id: 1)
3. Frontend POSTs /games {user_id: 1, category_id: 1, number_of_questions: 5}
4. Backend creates quiz_session record (id: 42)
5. Backend randomly selects first science question (id: 7)
6. Backend returns {game_session_id: 42, question_number: 1, question: {...}, current_score: {correct: 0, total_answered: 0, total_questions: 5}}
7. Frontend displays question 1/5, shows no answer field
8. Verify quiz_session exists in DB
```

**Dependencies:** POST /users, POST /categories (need data to exist)
**Estimated complexity:** Medium-Hard
**Why fourth:** Foundation for quiz flow

---

## 5️⃣ POST /quizzes/:id/:num - Answer Question

**Backend Work:**
- Endpoint: `POST /quizzes/<quiz_session_id>/<question_number>`
- Request: `{user_answer: "water"}`
- Response: `{correct: true/false, correct_answer: "H2O", current_score: {...}, question_number: 2, question: {...next question or null}}`
- Database: 
  - Validate quiz_session exists and not completed
  - Validate question_number matches expected sequence
  - Validate question not already answered (prevent re-answers)
  - Insert record into quiz_session_answer table
  - If final question: Mark quiz_session as completed, update User.total_score + User.games_played
- Validation: Answer matching logic (lowercase, special chars, substring)
- Error codes: 400 (missing answer), 404 (quiz/question), 422 (already answered, out of sequence, completed)
- Tests: Correct answer, incorrect answer, re-answer error, out-of-sequence error, quiz completion

**Frontend Work:**
- Component: QuizView.js (continue rewrite)
- Feature: Answer input + submit button + feedback display
- API call: POST /games/<session_id>/<question_num>
- State: Track current_score, display feedback (correct/incorrect + answer)
- Display: Show next question, OR show completion screen if null

**Integration Test:**
```
1. Quiz session 42 started, question 1 displayed
2. User enters answer "water"
3. Frontend POSTs /games/42/1 {user_answer: "water"}
4. Backend validates: quiz_session 42 exists, question 1 not answered yet
5. Backend fetches question, normalizes both answers, validates match
6. Backend creates quiz_session_answer record (session_id: 42, question_number: 1, is_correct: true)
7. Backend calculates score (correct: 1, total_answered: 1, total_questions: 5)
8. Backend randomly selects next science question (id: 15)
9. Backend returns {correct: true, correct_answer: "H2O", current_score: {correct: 1, ...}, question: {id: 15, question: "Capital of France?", ...}}
10. Frontend displays feedback "Correct! The answer is H2O"
11. Frontend displays next question with updated score

12. [Loop: User answers questions 2, 3, 4]

13. User answers final question 5
14. Backend marks quiz_session as completed
15. Backend updates User: total_score = 0 + 4 = 4, games_played = 0 + 1 = 1
16. Backend returns {correct: true, ..., question: null, quiz_status: "completed"}
17. Frontend displays final score screen "You got 4/5 (80%)"
18. Verify quiz_session.status = "completed" in DB
19. Verify User.total_score = 4 in DB
20. Verify User.games_played = 1 in DB
```

**Dependencies:** POST /games (need active session)
**Estimated complexity:** Hard (most complex logic)
**Why fifth:** Core quiz gameplay

---

### PHASE 2: DELETE OPERATIONS (DELETE)

---

## 6️⃣ DELETE /questions/:id - Delete Question

**Backend Work:**
- Endpoint: `DELETE /questions/<question_id>`
- Request: None
- Response: `{deleted: <question_id>, success: true}`
- Database: Delete from questions table
- Validation: Check question exists
- Error codes: 404 (not found)
- Tests: Success case, not found error

**Frontend Work:**
- Component: QuestionView.js (already exists, verify still works)
- Feature: Delete button on each question (already exists)
- API call: DELETE /questions/<id> (same as before)
- Display: Remove question from list after delete

**Integration Test:**
```
1. Question 25 displayed in question list
2. User clicks delete button
3. Frontend DELETEs /questions/25
4. Backend deletes from DB
5. Backend returns {deleted: 25, success: true}
6. Frontend removes question from list
7. Verify question_id 25 doesn't exist in DB
```

**Dependencies:** POST /questions (need questions to delete)
**Estimated complexity:** Easy
**Why sixth:** Existing endpoint, verify still works with new DB

---

## 7️⃣ DELETE /categories/:id - Delete Category (with force cascade)

**Backend Work:**
- Endpoint: `DELETE /categories/<category_id>?force=false`
- Query param: `force` (boolean, default false)
- Response (safe delete): `{deleted: <id>, success: true}`
- Response (cascade delete): `{deleted: <id>, questions_deleted: 5, success: true}`
- Database:
  - If force=false: Check if questions exist, fail if yes
  - If force=true: Delete all questions with this category_id, then delete category
- Validation: Check category exists
- Error codes: 404 (not found), 422 (has questions and force=false)
- Tests: Safe delete (no questions), safe delete fail (has questions), cascade delete success

**Frontend Work:**
- Component: CategoryManager.js (new) OR admin panel
- Feature: Delete button on each category
- API call: DELETE /categories/<id> OR DELETE /categories/<id>?force=true (confirm with user first)
- Display: Prompt user if questions exist ("Delete category and 5 questions?")

**Integration Test:**
```
1. Category "Science" (id: 1) has 3 questions

2. User clicks delete (normal)
3. Frontend DELETEs /categories/1
4. Backend checks: questions exist for category 1
5. Backend returns 422 error "Category has questions, use ?force=true to delete"
6. Frontend shows warning "Delete category and associated questions?"
7. User confirms

8. Frontend DELETEs /categories/1?force=true
9. Backend deletes all questions where category_id = 1 (3 records)
10. Backend deletes category record
11. Backend returns {deleted: 1, questions_deleted: 3, success: true}
12. Frontend removes category from list
13. Verify category 1 gone in DB
14. Verify questions 1-3 gone in DB (or have NULL category)
```

**Dependencies:** POST /categories, POST /questions (need data to test)
**Estimated complexity:** Medium
**Why seventh:** Cleanup operation, builds on previous endpoints

---

### PHASE 3: READ/GET OPERATIONS (GET)

---

## 8️⃣ GET /categories - List All Categories

**Backend Work:**
- Endpoint: `GET /categories`
- Request: None
- Response: `{categories: {1: "Science", 2: "Art", ...}, success: true}`
- Database: Query all categories
- Tests: Return all categories, empty list if none exist

**Frontend Work:**
- Component: QuizView.js (already using this)
- Feature: Verify still displays categories for quiz selection
- API call: GET /categories (same as before)
- Display: Dropdown/buttons for category selection

**Integration Test:**
```
1. Frontend mounts QuizView
2. Frontend calls GET /categories
3. Backend returns {categories: {1: "Science", 2: "Art", ...}}
4. Frontend displays in dropdown
5. Verify all categories from seed data appear
```

**Dependencies:** None (use seed data)
**Estimated complexity:** Easy
**Why eighth:** Already exists, verify works

---

## 9️⃣ GET /categories/:id - Get Single Category

**Backend Work:**
- Endpoint: `GET /categories/<category_id>`
- Request: None
- Response: `{id, type, success: true}`
- Database: Query category by id
- Validation: Check category exists
- Error codes: 404 (not found)
- Tests: Success case, not found error

**Frontend Work:**
- Component: CategoryDetail.js (new) OR QuizView
- Feature: View category details before starting quiz
- API call: GET /categories/<id>
- Display: Category name, question count, difficulty info

**Integration Test:**
```
1. User clicks "Science" category
2. Frontend calls GET /categories/1
3. Backend returns {id: 1, type: "Science", success: true}
4. Frontend displays "Science - 3 questions available"
5. User confirms to start quiz
```

**Dependencies:** POST /categories (need categories to exist)
**Estimated complexity:** Easy
**Why ninth:** Simple lookup, builds on categories work

---

## 🔟 GET /questions - List Questions with Pagination & Search

**Backend Work:**
- Endpoint: `GET /questions?page=1&search=water`
- Query params: `page` (int, default 1), `search` (string, optional)
- Response: `{questions: [...], total_questions, current_page, total_pages, categories: {...}, success: true}`
- Database: Query questions with pagination (10 per page), optional search filter
- Validation: Check page valid
- Error codes: 404 (page out of range), 400 (invalid page)
- Tests: List all questions, page 1, page 2, search filter, search with no results, invalid page

**Frontend Work:**
- Component: Search.js (already exists)
- Feature: Search input + pagination (already exists)
- API call: GET /questions?search=term&page=1 (update from POST to GET if needed)
- Display: Questions list, pagination controls, search results

**Integration Test:**
```
1. User opens Question list
2. Frontend calls GET /questions?page=1
3. Backend returns first 10 questions + pagination info
4. Frontend displays questions

5. User searches "water"
6. Frontend calls GET /questions?search=water&page=1
7. Backend filters questions by substring
8. Backend returns matching questions
9. Frontend displays search results
```

**Dependencies:** POST /questions (need questions to query)
**Estimated complexity:** Easy-Medium
**Why tenth:** Existing endpoint, verify works

---

## 1️⃣1️⃣ GET /categories/:id/questions - Get Questions by Category

**Backend Work:**
- Endpoint: `GET /categories/<category_id>/questions?page=1`
- Query params: `page` (int, default 1)
- Response: `{questions: [...], total_questions, current_page, current_category, success: true}`
- Database: Query questions filtered by category_id with pagination
- Validation: Check category exists, page valid
- Error codes: 404 (category not found or no questions), 400 (invalid page)
- Tests: Get questions for category, multiple pages, category with no questions, invalid category

**Frontend Work:**
- Component: QuestionView.js (already uses this)
- Feature: Click category → show only those questions (already exists)
- API call: GET /categories/<id>/questions (same as before)
- Display: Questions list filtered by category

**Integration Test:**
```
1. User clicks "Science" category in question list
2. Frontend calls GET /categories/1/questions?page=1
3. Backend returns only science questions
4. Frontend displays questions for Science category
5. Verify only questions with category_id=1 appear
```

**Dependencies:** POST /categories, POST /questions
**Estimated complexity:** Easy
**Why eleventh:** Existing endpoint, verify works

---

## 1️⃣2️⃣ GET /quizzes/:id - Get Quiz State (Catch-Up Endpoint)

**Backend Work:**
- Endpoint: `GET /quizzes/<quiz_session_id>`
- Request: None
- Response (in progress): `{game_session_id, question_number, current_score: {...}, question: {...}, success: true}`
- Response (completed): `{game_session_id, status: "completed", current_score: {...}, success: true}`
- Database: Query quiz_session by id, check status, get next unanswered question
- Validation: Check quiz_session exists
- Error codes: 404 (not found)
- Tests: Quiz in progress, quiz completed, quiz not found

**Frontend Work:**
- Component: QuizView.js (add catch-up logic)
- Feature: Optional - auto-recover if connection lost
- API call: GET /games/<id> (optional on mount)
- Display: Show current state + next question OR completion screen

**Integration Test:**
```
1. User mid-quiz (answered 3/5 questions)
2. Connection drops, refresh page
3. Frontend calls GET /games/42
4. Backend returns current state: {game_session_id: 42, question_number: 4, current_score: {correct: 3, ...}}
5. Frontend displays question 4 to continue
6. User finishes quiz normally

7. [Later] User calls GET /games/42
8. Backend returns {game_session_id: 42, status: "completed", current_score: {correct: 4, ...}}
9. Frontend shows "Quiz already completed, final score: 4/5"
```

**Dependencies:** POST /games, POST /games/<id>/<num> (need active or completed game)
**Estimated complexity:** Medium
**Why twelfth:** Quiz feature continues

---

## 1️⃣3️⃣ GET /users - List All Users

**Backend Work:**
- Endpoint: `GET /users`
- Request: None
- Response: `{users: [{id, username, total_score, games_played, created_at}, ...], total_users, success: true}`
- Database: Query all users
- Tests: List all users, empty list if none

**Frontend Work:**
- Component: UserSelector.js (needs this for select dropdown)
- Feature: Show list of users to select from
- API call: GET /users (on mount)
- Display: User list with scores

**Integration Test:**
```
1. UserSelector mounts
2. Frontend calls GET /users
3. Backend returns {users: [{id: 1, username: "alice", total_score: 4, ...}, ...]}
4. Frontend displays in select dropdown
5. User can click to select from list
```

**Dependencies:** POST /users (need users to exist)
**Estimated complexity:** Easy
**Why thirteenth:** User management feature

---

## 1️⃣4️⃣ GET /users/:id - Get User Details + Game History

**Backend Work:**
- Endpoint: `GET /users/<user_id>`
- Request: None
- Response: `{id, username, total_score, games_played, created_at, game_sessions: [{id, quiz_category, score, date_played, ...}, ...], success: true}`
- Database: Query user by id, fetch all game_sessions for that user (sorted by date_played desc)
- Validation: Check user exists
- Error codes: 404 (not found)
- Tests: Get user with game history, user with no games, user not found

**Frontend Work:**
- Component: UserDashboard.js (new)
- Feature: Display user profile + game history
- API call: GET /users/<id> (on mount when user clicks profile)
- Display: User name, total score, games played, history table

**Integration Test:**
```
1. User alice (id: 1) clicks "My Profile"
2. Frontend calls GET /users/1
3. Backend returns user + all game_sessions: {id: 1, username: "alice", total_score: 12, games_played: 3, game_sessions: [{quiz_category: 1, score: 4, ...}, ...]}
4. Frontend displays profile page
5. Verify game history shows correct sessions
```

**Dependencies:** POST /users, POST /games/<id>/<num> (need user with games)
**Estimated complexity:** Medium
**Why fourteenth:** User profile feature

---

## 1️⃣5️⃣ GET /leaderboard - Top Users by Score

**Backend Work:**
- Endpoint: `GET /leaderboard?limit=10&offset=0`
- Query params: `limit` (int, default 10), `offset` (int, default 0)
- Response: `{leaderboard: [{rank, id, username, total_score, games_played}, ...], total_users, success: true}`
- Database: Query users sorted by total_score desc, apply pagination
- Tests: Get top 10, get top 5, pagination works

**Frontend Work:**
- Component: Leaderboard.js (new)
- Feature: Display rankings
- API call: GET /leaderboard (on mount)
- Display: Ranking table (rank, username, score, games played)

**Integration Test:**
```
1. User opens Leaderboard
2. Frontend calls GET /leaderboard?limit=10
3. Backend returns sorted users: {leaderboard: [{rank: 1, username: "alice", total_score: 12, ...}, {rank: 2, username: "bob", total_score: 8}, ...]}
4. Frontend displays table in rank order
5. Verify alice (highest score) is rank 1
```

**Dependencies:** POST /users, complete quiz (populates scores)
**Estimated complexity:** Easy-Medium
**Why fifteenth:** Final feature (analytics)

---

## Implementation Dependency Graph

```
POST /users (1)
    ↓
POST /categories (2)
    ↓
POST /questions (3)
    ↓
POST /quizzes (4) → POST /quizzes/<id>/<num> (5)
    ↓
DELETE /questions (6)
DELETE /categories (7)
    ↓
GET /categories (8) → GET /categories/<id> (9)
GET /questions (10)
GET /categories/<id>/questions (11)
GET /quizzes/<id> (12)
GET /users (13) → GET /users/<id> (14)
GET /leaderboard (15)
```

---

## Testing Checklist (Per Endpoint)

Each endpoint should have:
- [ ] Backend pytest tests (success + error cases)
- [ ] Frontend component updated/created
- [ ] API call integration tested
- [ ] Database state verified
- [ ] Error handling tested
- [ ] Manual curl/Postman test successful

---

## Git Commits Plan

After each endpoint, create atomic commit:
```
git add flaskr/__init__.py data_access/*.py _tests/test_*.py
git commit -m "feat: POST /users endpoint with tests and validation"
git push

git add frontend/src/components/UserSelector.js
git commit -m "feat: UserSelector component for user creation"
git push
```

---

## Estimated Timeline

| Phase | Endpoints | Estimated Time |
|-------|-----------|-----------------|
| Phase 1 | 5 POSTs | 8-10 hours |
| Phase 2 | 2 DELETEs | 2-3 hours |
| Phase 3 | 8 GETs | 4-6 hours |
| **Total** | **15 endpoints** | **14-19 hours** |

---

## Success Criteria

✅ All 15 endpoints implemented and tested
✅ Full React component updates complete
✅ End-to-end integration tests pass
✅ All API responses match specification
✅ Database operations verified
✅ Error handling works for all edge cases
✅ Code adheres to PEP 8
✅ Backend tests achieve >80% coverage
✅ Seed data can be used to demo full flow
