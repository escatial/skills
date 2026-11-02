# Stage 6: Backend Development

## Persona
**Backend Engineer**. Implement the API contract from stage 4 against
the database from stage 5.

## Goal
Produce a working backend with:
- Project scaffold (chosen framework, structure, configs)
- Database migrations from `05-database.md`
- Auth implementation (from stage 3)
- Base CRUD for every resource in the API contract
- P0 business endpoints with validation, error handling, logging
- Unit + integration tests

## Implementation order

1. **Scaffold first, slow down later.** Get a `/health` endpoint
   returning 200 with the chosen stack running. Reason: every later
   step needs the scaffold to actually start.

2. **Migrations applied to local DB.** Run `05-database.md` scripts
   via the chosen migration tool. Reason: the first integration bug
   is usually "schema doesn't match the migration".

3. **Cross-cutting infrastructure before endpoints:**
   - Request ID / trace ID middleware
   - Structured logging (JSON, with traceId correlation)
   - Error handler (maps domain errors to the API error shape from
     stage 4)
   - Validation middleware (zod / class-validator / joi)
   - Auth middleware (token verify + role check)
   - Rate limiting (default 100/min/user)

4. **CRUD endpoints per resource, in this order per resource:**
   - `GET /` (list, with pagination)
   - `GET /{id}` (single)
   - `POST /` (create)
   - `PATCH /{id}` (partial update)
   - `DELETE /{id}` (soft delete by default)
   Reason: list/get/filter exercises 80% of the read path; create
   exercises validation and the soft-delete path. Get these right
   before business endpoints.

5. **Then P0 business endpoints, one at a time.** After each
   endpoint:
   - Add validation schema
   - Add service-layer logic
   - Add unit tests (business logic) and integration tests
     (HTTP + DB roundtrip)
   - Update `06-backend-progress.md` with the endpoint ID and
     test status

6. **Don't touch the API contract without a written change.** If
   stage 4's spec is wrong, edit `04-api-contract.yaml` first, get
   frontend's ack, then implement. Reason: silent contract drift
   is the worst class of bug.

## Module structure (typical)

```
src/
├── config/              # env, db, etc.
├── common/
│   ├── middleware/      # auth, request-id, error handler
│   ├── filters/         # global exception filter
│   ├── interceptors/    # logging, response transform
│   ├── guards/          # role guard
│   └── decorators/      # @CurrentUser, @Roles
├── modules/
│   ├── auth/            # login, refresh, logout
│   ├── user/
│   ├── order/
│   └── ...
├── database/
│   ├── migrations/
│   └── seeds/           # only for dev
├── app.module.ts
└── main.ts
```

## What to test

- **Unit**: pure business logic — pricing, validation rules, state
  transitions
- **Integration**: HTTP layer hitting a real (test) DB
  - happy path
  - validation error
  - 401 unauthenticated
  - 403 wrong role
  - 404 not found
  - 409 conflict (duplicate, stock-out, etc.)
- **NOT in scope here**: load tests (stage 8), security audit (stage 8/9)

## Exit gate
- [ ] All P0 endpoints from `04-api-contract.yaml` implemented
- [ ] P0 endpoints have integration tests
- [ ] No P0 endpoint has a known Sev1 bug
- [ ] OpenAPI doc still matches implementation (re-validate)
- [ ] Backend can run with a one-line command (`docker-compose up` or
      `make dev`) and serve the API

## Common failure modes
- Implementing CRUD before cross-cutting infrastructure — every
  endpoint ends up rolling its own auth/error handling
- Skipping the "list with pagination" endpoint — always needed,
  always forgotten
- Forgetting `Content-Type` and `Accept` validation — chaos ensues
  when frontend sends form-encoded by accident
- Trusting frontend to send correct IDs — always re-validate
  ownership (user can't edit another user's order)
- Not handling concurrent updates — last write wins, no warning;
  add optimistic locking if stage 4 says so
