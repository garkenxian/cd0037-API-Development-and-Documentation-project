# Mini-Model Project Completion Plan

## Purpose
This plan is the execution roadmap to finish this project as a fully RESTful, secure, and rubric-aligned submission while remaining manageable for a smaller model.

It is grounded in the current codebase, assignment files, API specification, and implementation notes.

## Source of Truth Hierarchy
Use this priority order when conflicts appear:
1. `PROJECT_RUBRIC.md`
2. `backend/API_SPECIFICATION.md`
3. `README.md` and `backend/README.md`
4. Current backend/frontend code behavior
5. Historical planning markdown notes

## Hard Constraints
1. Every backend and frontend source file under test must be >= 80% coverage before merge.
2. Final hardening phase targets 100% per-file coverage where practical.
3. No secrets in source control. Environment variables only.
4. Any endpoint contract change requires tests + docs updates in the same PR.
5. Python runtime baseline is 3.10+ (3.7 is deprecated/EOL and not a supported target for this project pass).

## Delivery Order Constraint
1. Backend API completion and contract correctness are the current priority.
2. Frontend changes are intentionally deferred until backend/API behavior is complete and stable.
3. Frontend work in the current phase is limited to lightweight unit-test maintenance only.

## Current State Snapshot (2026-09-05)

### What is already strong
1. Backend layered architecture exists: controllers, services, repositories, models.
2. 16 endpoint surface is mostly present.
3. Backend tests pass and total backend coverage is high (~93%).
4. Python environment and tooling are mostly stable on 3.10+.
5. Runtime baseline decision is explicit: assignment historically referenced 3.7, but project standard is 3.10 as the lowest supported modern version.

### Critical gaps to close
1. Game flow correctness/security is incomplete:
   - `POST /games/<id>/<question_number>` currently validates against randomly selected questions, not deterministic served-question state.
   - No durable answer audit table is present yet (`game_session_answer`), so sequence integrity and replay resistance are weak.
2. API/docs drift is high:
   - Several docs mix `quiz` vs `game` terminology and old endpoints.
3. Frontend API drift is high:
   - `QuizView.js` and `QuestionView.js` still call legacy `/quizzes` and POST search flow.
4. Frontend coverage is far below requirement:
   - Current frontend per-file coverage is around 16%-71% in key components.
5. Error contract inconsistency:
   - Error bodies in code are minimal (`{"error": "Bad Request"}`) but API spec describes structured error payloads with message/success semantics.
6. Data/service quality concerns worth fixing now:
   - Duplicate method name in `UserService` (`get_all_users`) overrides the earlier paginated version.
   - Category uniqueness is service-level only; no DB uniqueness constraint.
7. Database-enforced validation is incomplete:
   - Several domain rules are currently service-only and need PostgreSQL CHECK/UNIQUE constraints to be authoritative.

## Callouts (Best-Practice Deviations)
These are not stylistic nitpicks; they are correctness or maintainability risks:
1. Endpoint determinism is currently violated in game answer validation. This is the highest-risk issue and should block release.
2. Test totals are high, but backend per-file gate currently fails for at least `controllers/questions.py` (<80%), so total coverage alone is insufficient.
3. Frontend tests currently pass, but coverage depth is intentionally incomplete at this stage because frontend completion is deferred until backend/API completion.

## Execution Strategy For a Mini Model
Keep each task narrow and verifiable:
1. One phase at a time.
2. One primary objective per PR.
3. Max 2-4 files changed per mini-model run when possible.
4. Each run must end with: tests run, coverage check, docs updated if behavior changed.
5. At the end of each phase, re-evaluate all remaining phases and adjust future tasks/ordering based on what changed.

## Phase Exit Revalidation Rule (Applies To Every Phase)
Before closing any phase as done:
1. Re-check API spec, plan, and backlog for downstream impact from the completed work.
2. Update remaining phase tasks, entry criteria, and definitions of done if assumptions changed.
3. Record any scope/order changes in the Decision Log or Spec-to-Implementation Alignment Backlog.
4. Confirm the next phase is still valid before starting implementation.

## Phased Plan

## Phase 0 - Baseline Lock and Alignment
Goal: freeze reality before deeper changes.

Tasks:
1. Record current backend and frontend coverage baselines in a single status section.
2. Confirm active endpoint contracts from controllers and compare to `backend/API_SPECIFICATION.md`.
3. Create a contract mismatch checklist (code vs docs vs frontend).
4. Add a quality gate checklist to PR template (coverage, tests, docs parity, security checks).

Done when:
1. Mismatch checklist exists and is reviewed.
2. Baseline metrics are documented and reproducible with commands.

## Phase 1 - Deterministic Secure Game Session Core (Highest Priority)
Goal: make game flow correct, auditable, and secure-by-design.

Tasks:
1. Add `game_session_answer` model with constraints:
   - unique `(game_session_id, question_number)`
   - immutable snapshot fields for asked question text and expected answer
2. Add repository and service operations for:
   - store initial served question
   - fetch expected question by game/question_number
   - record user answer exactly once
   - compute next question number
   - compute current score
3. Refactor `POST /games`:
   - persist first served question mapping deterministically.
4. Refactor `POST /games/<id>/<question_number>`:
   - reject out-of-sequence and duplicate submits.
   - validate against stored expected answer, not random fetch.
5. Refactor `GET /games/<id>`:
   - return resumable state from persisted session/answers.
6. Ensure user stats updates happen exactly once on completion.

Done when:
1. No random-question validation path remains.
2. All game-session tests pass, including sequence and replay tests.
3. Per-file coverage for game controller/service/repository/model is >=80%.

## Phase 2 - REST and Error Contract Normalization
Goal: ensure API behavior and payloads match the published contract and rubric.

Tasks:
1. Standardize all error responses to one schema:
   - `{ "success": false, "error": <code>, "message": "..." }`
2. Ensure category delete behavior exactly matches current simplified spec (no force cascade).
3. Validate request/response consistency for all 17 endpoints.
4. Remove legacy terminology and legacy endpoint traces from active code paths.
5. Align service-layer validation messages and status mapping with database constraint violations.

Done when:
1. Integration tests assert status code + payload schema for all common errors.
2. API spec examples match observed responses.
3. Service validation and database constraints enforce the same domain rules.

## Phase 3 - Backend Coverage Gate to 80% Per File
Goal: enforce your hard rule in CI and eliminate weak backend files.

Tasks:
1. Track per-file coverage manually in development workflow (developer policy, not CI-enforced).
2. Add missing tests for low files first:
   - `controllers/questions.py`
   - edge error paths in categories and games where uncovered.
3. Keep existing high-coverage layers stable.

Done when:
1. Coverage report shows every backend source file >=80%.
2. Coverage checks are repeatable locally and documented in the team workflow.

## Phase 4 - Frontend Contract Migration
Goal: align frontend to new REST contracts and remove legacy quiz logic.

Entry criteria:
1. Backend API contract is complete and stable against `backend/API_SPECIFICATION.md`.
2. Backend contract and error-schema tests are passing.

Tasks:
1. Update `QuizView.js` to session-based game flow:
   - start game via `POST /games`
   - answer via `POST /games/<id>/<question_number>`
   - optional resume via `GET /games/<id>`
2. Update `QuestionView.js` search to `GET /questions?search=...`.
3. Keep add/delete/list question screens compatible with backend responses.
4. Introduce shared API helper utilities to reduce duplicate request logic.

Done when:
1. No frontend calls to `/quizzes` remain.
2. End-to-end manual flow works for create user -> start game -> answer -> complete.

## Phase 5 - Frontend Test Expansion to 80% Per File
Goal: satisfy your hard gate on frontend quality.

Entry criteria:
1. Phase 4 frontend contract migration is complete.
2. No backend contract-breaking changes are pending.

Tasks:
1. Expand tests for:
   - `QuizView.js` state transitions, request errors, completion path
   - `QuestionView.js` pagination, category filter, search
   - `FormView.js` field handling + submit error paths
   - `Header.js` route/state rendering
2. Add mock API failure tests for each component.
3. Add per-file frontend coverage gate >=80%.

Done when:
1. Every frontend source file under `src/components` is >=80% statements and lines.
2. CI fails on per-file regression.

## Phase 6 - Security Hardening Pass
Goal: strengthen operational security while preserving assignment scope.

Tasks:
1. Restrict CORS origins by environment (dev wildcard only).
2. Add input length limits and normalization for text fields.
3. Add simple abuse protection:
   - per-IP/game-session throttling on answer endpoint (lightweight)
4. Ensure no answer leakage except intended reveal after submit.
5. Verify dependency hygiene (backend + frontend audit).

Done when:
1. Security checklist passes in README.
2. Abuse and invalid-input paths are tested.

## Phase 7 - Documentation Consolidation and Final Submission Pack
Goal: one canonical, reviewer-friendly document set.

Tasks:
1. Rewrite root `README.md` to match actual architecture, endpoints, setup, and tests.
2. Reconcile `backend/API_SPECIFICATION.md` with implemented contracts.
3. Keep `backend/BUSINESS_DECISIONS.md` as design rationale (clean terminology).
4. Add final test/coverage instructions with exact commands for Windows.

Done when:
1. A fresh reviewer can run app/tests from docs only.
2. No stale endpoint names or contradictory payload examples remain.

## Phase 8 - 100% Stretch Coverage and Polish
Goal: optional final excellence pass.

Tasks:
1. Raise backend files from >=80% toward 100% one by one.
2. Raise frontend files similarly where realistic.
3. Add regression tests for every bug fixed in prior phases.

Done when:
1. Coverage plateaus near 100% with meaningful tests (not trivial assertions).

## Recommended Mini-Model Work Units
Use this template for each run:
1. Objective: one bullet (single phase task).
2. Files allowed: explicit list.
3. Non-goals: explicit exclusions.
4. Verification commands: backend tests, frontend tests, coverage command.
5. Output required: summary + changed files + any spec updates.

Example work unit:
1. Objective: implement deterministic answer recording for `POST /games/<id>/<question_number>`.
2. Files: `backend/controllers/games.py`, `backend/services/game_session_answer_service.py`, `backend/data_access/game_session_answer_repository.py`, `backend/models/game_session_answer.py`, related tests.
3. Non-goals: no frontend edits.
4. Verify: pytest + coverage.
5. Output: endpoint behavior summary + tests added.

## Markdown Cleanup Recommendations

### Keep as canonical
1. `README.md`
2. `PROJECT_RUBRIC.md`
3. `backend/API_SPECIFICATION.md`
4. `backend/BUSINESS_DECISIONS.md`
5. `backend/README.md`
6. `backend/TESTING.md`
7. `PYTHON_VERSION.md`

### [DONE] Archive to docs/archive/ (recommended)
These appear temporary, superseded, or PR-specific:
1. `COPILOT_PR4_FIXES_FINAL.md`
2. `COPILOT_REVIEW_RESOLUTION.md`
3. `PR_RESOLUTION.md`
4. `API_IMPLEMENTATION_ORDER.md`
5. `PHASE_1B_ENDPOINT_INTEGRATION.md`
6. `REACT_COMPONENT_PLAN.md`
7. `SEED_DATA_UPDATE.md` (after extracting any unique content into canonical docs)
8. `TEST_COVERAGE_SUMMARY.md` (replace with generated CI badge/report links)
9. `TERMINOLOGY_CONSOLIDATION.md` (after merge into API spec/business decisions)
10. `CODECOV_SETUP.md` (keep only if actively used; otherwise merge key steps into README)
11. `PROJECT_PLAN.md` (historical and now superseded)

### [DONE] Delete generated artifacts from repo tracking if present
1. `backend/htmlcov/` (should be gitignored and untracked)
2. `frontend/coverage/` (should be gitignored and untracked)

## Quality Gates (apply at end of every phase)
1. Backend tests pass.
2. Frontend tests pass.
3. Per-file backend coverage >=80%.
4. Per-file frontend coverage >=80% for touched files (and globally by Phase 5).
5. Docs updated for changed behavior.
6. No TODO/FIXME left in changed files.
7. Remaining phases have been revalidated and updated for any downstream impacts.

## Decision Log (Confirmed + Open)
1. Auth scope: CONFIRMED
   - Keep username-only (assignment scope).
   - Users are created via form and selected via dropdown.
   - No OAuth/JWT/session auth in this project pass.
2. Category delete contract: CONFIRMED
   - Simplify behavior: no `force=true` cascade path.
   - Delete only when category has no linked questions; otherwise return 422.
   - Update API spec, tests, and frontend assumptions accordingly.
3. Score semantics: CONFIRMED
   - Use `correct_count` only.
   - `score` for a game = number of correct answers in that game.
   - `total_score` for a user = sum of correct answers across all completed games.
   - No weighted or point-based scoring model in this project pass.
4. Frontend modernization: CONFIRMED
   - Keep class-based components.
   - Apply only contract-alignment changes required by endpoint redesign.

## Immediate Next 3 Executable Tasks
1. Build Phase 1 model/repo/service for deterministic game answers and integrate into all 3 game endpoints.
2. Add/adjust tests for game sequence, duplicate answer rejection, completion idempotency, and resume state.
3. Fix backend per-file coverage failure in `controllers/questions.py` and verify per-file 80% manually in local checks.

## Spec-to-Implementation Alignment Backlog (v1.0 Contract)
Use this checklist to bring runtime behavior in line with `backend/API_SPECIFICATION.md`.

0. Runtime and tooling alignment
   - Ensure all docs consistently state Python 3.10+ as required.
   - Ensure CI uses Python 3.10 for required checks.
   - Treat Python 3.7 compatibility as out-of-scope for this project pass.

0.1 Data validation constraints alignment
    - Implement PostgreSQL constraints defined in `backend/API_SPECIFICATION.md`:
       - users.username length (3-50, trimmed) and case-insensitive uniqueness
       - categories.type length (1-100, trimmed) and case-insensitive uniqueness
       - questions.question/answer length, difficulty range, rating range
       - game_sessions score non-negative and number_of_questions range (1-20)
       - game_session_answer required NOT NULL/CHECK/UNIQUE rules
    - Mirror these rules in services for early, user-friendly errors.
    - Add integration tests that prove DB-level constraints reject invalid writes.

1. Categories contract updates
   - Keep simplified delete semantics only (no force cascade).
   - Return 422 when category has linked questions.
   - Ensure tests assert this behavior directly.

2. Questions contract updates
   - Ensure `GET /questions/<id>` is fully implemented, documented, and tested as a first-class endpoint.
   - Ensure category-filtered question listing returns 200 with empty list when category exists but has no questions.

3. Games contract updates (highest priority)
   - Implement deterministic question assignment and answer validation using `game_session_answer`.
   - Remove any random-question scoring path from answer submission.
   - Enforce ordered answering and duplicate-submit rejection.
   - Keep score semantics as `correct_count` only.

4. Users contract updates
   - Align leaderboard route to `GET /users/leaderboard`.
   - Align user game history payload fields to spec naming.

5. Error contract updates
   - Standardize all error responses to `{ "success": false, "error": <code>, "message": "..." }`.
   - Add tests for 400/404/422/500 payload structure across representative endpoints.

6. Contract governance updates
   - Treat API spec as active source of truth (v1.0).
   - Any endpoint contract change requires same-PR updates to controller tests and spec examples.
   - Add a lightweight pre-merge checklist item: "Spec examples match actual responses".
