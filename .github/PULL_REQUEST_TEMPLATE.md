## Summary

- 

## Scope

- Phase:
- Behavior changes:
- Non-goals:

## Verification

- [ ] Backend tests pass locally.
- [ ] Frontend tests pass locally.
- [ ] Coverage captured for touched areas.

## Quality Gate Checklist

- [ ] Backend per-file coverage is >= 80% for all touched backend source files.
- [ ] Frontend per-file coverage is >= 80% for all touched frontend source files.
- [ ] API contract behavior changes include tests in the same PR.
- [ ] API contract behavior changes include docs/spec updates in the same PR.
- [ ] Error payloads follow the project contract for changed endpoints.
- [ ] No secrets are introduced in code, config, logs, or test artifacts.
- [ ] Input validation and failure paths are covered for changed endpoints/components.
- [ ] Security-sensitive behavior changes were reviewed (CORS, data leakage, replay/idempotency, abuse paths).
- [ ] No TODO/FIXME markers were introduced in changed files.

## Manual Checks

- [ ] Endpoint examples in backend/API_SPECIFICATION.md match observed API responses for changed routes.
- [ ] Frontend API calls match current backend contract for changed flows.
