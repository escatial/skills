# Stage 8: Integration Test & Acceptance

## Persona
**QA + Dev together**. This is the contract verification stage. The
goal is to prove that frontend, backend, and the API contract from
stage 4 all agree.

## Goal
Produce `08-integration-report.md` with:
- API contract verification (every endpoint, every response shape)
- E2E test results for P0 user flows
- Performance baseline (P95 latency on top 10 endpoints)
- Bug list with severity (Sev1/Sev2/Sev3) and status
- Sign-off checklist for P0

## Test layers

### 1. Contract test (most important)

Generate from `04-api-contract.yaml` and run against the real backend:
- Every endpoint exists
- Request schema matches what frontend actually sends
- Response schema matches what frontend actually expects
- Status codes match (especially 4xx)
- Error response shape matches the convention

Tools: Dredd, Spectral, Schemathesis, Pact, or simply a script that
hits every endpoint and validates the response against the OpenAPI
schema. Reason: contract drift between stage 4 and stage 8 is the
#1 source of "works in dev, breaks in prod" bugs.

### 2. E2E test

P0 user flows from `01-requirements.md` scenarios, run as real
browser automation:
- Login → dashboard → action
- Create order → list shows it → detail loads
- Empty state path
- Error state path (force a 500, force a 401)

Tools: Playwright (preferred) or Cypress.

### 3. Performance smoke

Not full load test, but a baseline:
- Top 10 endpoints, 100 concurrent users, 30s
- Record P95 latency
- Flag any endpoint > 2x its single-user baseline
- Flag any error rate > 0.1%

Tools: k6, wrk, vegeta, JMeter.

### 4. Security smoke (lightweight)

- All endpoints (except login, register, health, public docs)
  require auth — verify by stripping token
- RBAC: cashier cannot hit admin endpoint
- SQL injection: try `' OR 1=1 --` on text fields
- XSS: try `<script>alert(1)</script>` in free-text fields
- IDOR: user A cannot GET user B's resource by guessing ID

Reason: a real security audit is a separate engagement, but these
five checks catch the most common oversights.

## Bug triage

| Sev | Definition | SLA |
|-----|-----------|-----|
| Sev1 | P0 flow broken, data loss, security hole | Block release |
| Sev2 | P0 flow degraded, P1 broken | Fix before release |
| Sev3 | Cosmetic, minor edge case | Backlog |

## Exit gate
- [ ] Contract test: 100% pass (or all failures triaged)
- [ ] E2E test: P0 flows 100% pass
- [ ] Performance: P95 within budget (defined in stage 1 non-functional)
- [ ] No Sev1 bugs open
- [ ] No Sev2 bugs open (or user explicitly accepted as known issues)
- [ ] Security smoke: 5 checks pass

## Common failure modes
- Skipping contract test, relying on manual click-through — manual
  tests don't catch JSON shape mismatches
- Performance test on dev machine, not production-like — passes
  locally, fails in prod
- Ignoring flaky E2E tests — they hide real bugs and erode trust
  in the test suite
- "It works on my machine" accepted as a fix — usually isn't
- Security checks skipped because "we'll do it later" — later
  is after the breach
