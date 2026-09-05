# Phase 1b Endpoint Integration - Stubs Added

**Date**: September 4, 2026  
**File Modified**: `backend/controllers/games.py`  
**Status**: Phase 1b stub integration complete - awaiting Phase 1b model/repo/service implementation

---

## Summary

All three game endpoints have been updated with Phase 1b (game_session_answer audit table) integration points. The endpoints now:

1. ✅ Import GameSessionAnswerService (with graceful ImportError handling)
2. ✅ Call Phase 1b methods with clear documentation of what's needed
3. ✅ Gracefully degrade if Phase 1b not available (with appropriate status codes)
4. ✅ Fix critical bugs once Phase 1b is implemented

---

## Endpoint Changes

### 1. POST /games - Create Game Session

**Integration Added** (Lines 70-82):
```python
# Phase 1b: Store the initial question in game_session_answer audit table
# This ensures question_number=1 is deterministically linked to this specific question
# When answer_question() is called, it validates against this stored question
if PHASE_1B_AVAILABLE:
    GameSessionAnswerService.store_initial_question(
        game_session_id=game_session.id,
        question_number=1,
        question=first_question
    )
```

**What This Does**:
- When creating a new game, stores the first question in the audit table
- Links question_number=1 to the specific question object served
- Ensures GET /games/:id can later retrieve this same question

**Will Be Implemented By**:
- `GameSessionAnswerService.store_initial_question(game_session_id, question_number, question)`

---

### 2. GET /games/:id - Get Game State (Catch-Up Endpoint)

**Integration Added** (Lines 102-159):
```python
# Phase 1b: Query game_session_answer audit table to find next unanswered question
if PHASE_1B_AVAILABLE:
    # Get the next unanswered question number
    next_question_number = GameSessionAnswerService.get_next_question_number(game_session_id)
    
    # Retrieve the next question that was prepared for this game
    next_answer_record = GameSessionAnswerService.get_by_game_and_question_number(
        game_session_id=game_session_id,
        question_number=next_question_number
    )
    
    if next_answer_record:
        # Game is in-progress, return next question
        return jsonify({
            'game_session_id': game_session.id,
            'question_number': next_question_number,
            'current_score': {
                'correct': GameSessionAnswerService.get_correct_count(game_session_id),
                'total_answered': next_question_number - 1,
                'total_questions': GameSessionAnswerService.get_total_questions(game_session_id)
            },
            'question': next_answer_record.get_question_format(),
            'success': True
        }), 200
    else:
        # All questions answered, game completed
        return jsonify({...})
```

**What This Does**:
- Supports catch-up after connection loss
- Queries audit table to find next unanswered question
- Returns correct score counts from audit table (not hardcoded)
- Detects game completion when all questions answered

**Will Be Implemented By**:
- `GameSessionAnswerService.get_next_question_number(game_session_id)` → next question number
- `GameSessionAnswerService.get_by_game_and_question_number(game_session_id, question_number)` → original question
- `next_answer_record.get_question_format()` → question dict for client
- `GameSessionAnswerService.get_correct_count(game_session_id)` → count of correct answers
- `GameSessionAnswerService.get_total_questions(game_session_id)` → total questions in game

---

### 3. POST /games/:id/:question_number - Answer Question ⚠️ CRITICAL FIX

**Integration Added** (Lines 167-221):
```python
# CRITICAL: This endpoint requires Phase 1b (game_session_answer audit table) to work correctly.
# Without Phase 1b, scoring is nondeterministic (answers validated against random questions).

if not PHASE_1B_AVAILABLE:
    # Phase 1b not available - cannot validate deterministically
    abort(501)  # Not Implemented - waiting for Phase 1b

# Phase 1b INTEGRATION: Retrieve the ORIGINAL question that was served for this question_number
# This ensures answers are validated against the same question the user saw
answer_record = GameSessionAnswerService.get_by_game_and_question_number(
    game_session_id=game_session_id,
    question_number=question_number
)

if not answer_record:
    # Question_number was never served in this session
    abort(404)

# Check if already answered (prevent duplicates)
if answer_record.is_already_answered():
    abort(422)  # Unprocessable: question already answered in this session

# Validate against the STORED question, not a random one
# This ensures deterministic, repeatable scoring
correct_answer = answer_record.correct_answer.lower().strip()
user_ans = user_answer.lower().strip()
is_correct = user_ans == correct_answer

# Record the answer in the audit table (Phase 1b)
answer_record.record_user_answer(
    user_answer=user_answer,
    is_correct=is_correct
)

# Return correct score counts from audit table
return jsonify({
    'current_score': {
        'correct': GameSessionAnswerService.get_correct_count(game_session_id),
        'total_answered': question_number,
        'total_questions': GameSessionAnswerService.get_total_questions(game_session_id)
    },
    ...
}), 200
```

**Critical Changes**:
1. ✅ Returns 501 (Not Implemented) if Phase 1b unavailable - no more nondeterministic bug
2. ✅ Retrieves ORIGINAL question from audit table (not random)
3. ✅ Validates against stored question deterministically
4. ✅ Prevents duplicate answers (422 if already answered)
5. ✅ Records answer in audit table for persistence
6. ✅ Returns correct score semantics (count, not points)

**Will Be Implemented By**:
- `GameSessionAnswerService.get_by_game_and_question_number()` → retrieve stored question
- `answer_record.is_already_answered()` → check duplicate
- `answer_record.correct_answer` → original answer for validation
- `answer_record.record_user_answer(user_answer, is_correct)` → persist answer
- `GameSessionAnswerService.get_correct_count()` → count correct answers
- `GameSessionAnswerService.get_total_questions()` → count total questions

---

## Phase 1b Service Methods Required

The endpoints import and call the following GameSessionAnswerService methods:

### From POST /games endpoint:
- `GameSessionAnswerService.store_initial_question(game_session_id, question_number, question)`

### From GET /games/:id endpoint:
- `GameSessionAnswerService.get_next_question_number(game_session_id)`
- `GameSessionAnswerService.get_by_game_and_question_number(game_session_id, question_number)`
- `GameSessionAnswerService.get_correct_count(game_session_id)`
- `GameSessionAnswerService.get_total_questions(game_session_id)`

### From POST /games/:id/:question_number endpoint:
- `GameSessionAnswerService.get_by_game_and_question_number(game_session_id, question_number)`
- `answer_record.is_already_answered()`
- `answer_record.record_user_answer(user_answer, is_correct)`
- `GameSessionAnswerService.get_correct_count(game_session_id)`
- `GameSessionAnswerService.get_total_questions(game_session_id)`

---

## Import Handling

**Lines 6-12**: Safe import with PHASE_1B_AVAILABLE flag
```python
try:
    from services import GameSessionAnswerService
    PHASE_1B_AVAILABLE = True
except ImportError:
    PHASE_1B_AVAILABLE = False
```

**Why This Pattern**:
- Tests and other code can run without Phase 1b implemented
- Graceful degradation - POST /games/:id/:question_number returns 501 instead of crashing
- Once Phase 1b is complete, import succeeds automatically
- No code changes needed to endpoints - just implement the service

---

## Testing Strategy

### Before Phase 1b Implementation
```powershell
# Tests will fail on answer_question() at 501 response
# This is EXPECTED - Phase 1b is not implemented yet
# create_game() and get_game() will skip Phase 1b integration (fallback behavior)
```

### During Phase 1b Implementation
```powershell
# 1. Create GameSessionAnswer model
# 2. Create GameSessionAnswerRepository with all methods
# 3. Create GameSessionAnswerService - stub implementations
# 4. Tests will pass once service methods exist and return valid objects
# 5. Implement each service method to actual logic
```

### After Phase 1b Complete
```powershell
# All endpoints work with deterministic scoring
# Catch-up after connection loss works
# Duplicate answer prevention works
# Score semantics correct (count, not points)
```

---

## Critical Bug Fixed

**The Problem** (Before):
- POST /games/:id/:question_number picked a random question
- Validated answer against that random question
- User saw Question A, but was scored against Question B → nondeterministic, wrong

**The Solution** (After Phase 1b):
- Create game: Store Question A in audit table with question_number=1
- Answer question: Retrieve Question A from audit table
- Validate answer against Question A (same one user saw) → deterministic, correct

---

## Next Steps

1. ✅ Endpoints updated with Phase 1b integration points
2. ⏳ Implement Phase 1b (model, repository, service)
   - `backend/models/game_session_answer.py`
   - `backend/data_access/game_session_answer_repository.py`
   - `backend/services/game_session_answer_service.py`
3. ⏳ Implement service methods called by endpoints
4. ⏳ Tests will automatically pass once service is complete
5. ✅ No further endpoint changes needed

---

## Code Review Notes

**For PR #4 follow-up**:
- Endpoints now integrate with Phase 1b stubs
- POST /games/:id/:question_number returns 501 until Phase 1b complete
- This prevents the nondeterministic bug from being used in production
- Once Phase 1b service is ready, all tests will pass automatically

**Graceful degradation**:
- GET /games/:id can fallback to basic game info if Phase 1b unavailable
- POST /games/:id/:question_number blocks with 501 (requires Phase 1b)
- This is intentional - answer endpoint cannot work without audit table
