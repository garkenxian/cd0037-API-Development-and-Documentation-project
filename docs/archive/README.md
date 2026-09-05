# Archive Directory

This directory contains temporary, superseded, or PR-specific planning documents that were active during development phases but are no longer the canonical source of truth.

## Why Archive?

During active development, many markdown files were created for phase planning, PR resolutions, and tracking fixes. To maintain clarity and reduce cognitive load for reviewers, these have been moved to archive while the core canonical documents remain at the root level.

## Contents

### Temporary Planning Files
- `API_IMPLEMENTATION_ORDER.md` - Historical endpoint implementation sequence
- `PHASE_1B_ENDPOINT_INTEGRATION.md` - Phase-specific integration tracking
- `PROJECT_PLAN.md` - Superseded by MINI_MODEL_COMPLETION_PLAN.md

### PR and Resolution Documents  
- `COPILOT_PR4_FIXES_FINAL.md` - PR #4 specific fixes and resolutions
- `COPILOT_REVIEW_RESOLUTION.md` - Review feedback resolution tracking
- `PR_RESOLUTION.md` - PR closure documentation

### Consolidation and Migration Documents
- `TERMINOLOGY_CONSOLIDATION.md` - Terminology alignment (merged into API_SPECIFICATION.md and BUSINESS_DECISIONS.md)
- `REACT_COMPONENT_PLAN.md` - Frontend component strategy (superseded by actual implementation)
- `SEED_DATA_UPDATE.md` - Database seeding updates (kept for reference; apply strategically)

### Reporting and Configuration
- `TEST_COVERAGE_SUMMARY.md` - Snapshot coverage report (refresh via `make coverage`)
- `CODECOV_SETUP.md` - CodeCov CI configuration (reference only; maintain locally if in use)

## Canonical Documents (at Root or Backend)

The following documents remain canonical and are the source of truth:

### Project Level
- `README.md` - Main project documentation
- `PROJECT_RUBRIC.md` - Assignment requirements and grading rubric
- `MINI_MODEL_COMPLETION_PLAN.md` - Active execution roadmap (phases 0-8)
- `PYTHON_VERSION.md` - Python version requirements

### Backend
- `backend/API_SPECIFICATION.md` - REST API contract (v1.0)
- `backend/BUSINESS_DECISIONS.md` - Design rationale and terminology
- `backend/README.md` - Backend setup and architecture
- `backend/TESTING.md` - Testing strategy and commands

## Recovery

If you need content from archived files:
1. Check the appropriate file in this directory
2. For consolidated content, refer to the canonical document instead (e.g., terminology use API_SPECIFICATION.md)
3. For historical context, the archive provides a searchable record

## Cleanup Notes

The following generated artifacts are tracked in `.gitignore` and should not appear in the repository:
- `backend/htmlcov/` - pytest coverage HTML reports (generated locally)
- `frontend/coverage/` - Jest/Node coverage reports (generated locally)

These directories can be safely regenerated via:
- Backend: `make coverage` or `pytest --cov`
- Frontend: `npm run test:ci`
