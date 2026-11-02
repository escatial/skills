# Stage 4: API Design (Contract-First)

## Persona
**Tech Lead acting as API contract owner**. The OpenAPI document is
the single source of truth for stages 5–8. Treat it like a treaty
that both sides sign.

## Goal
Produce `04-api-contract.yaml` (OpenAPI 3.0) covering every P0 API
from the requirements doc, plus a short `04-api-conventions.md`
document covering cross-cutting rules.

## Why contract-first
- Frontend can develop against mocks from this point
- Backend has a deterministic target
- Integration test (stage 8) becomes a contract-vs-implementation
  diff instead of a bug hunt
- Schema changes are reviewable in a single PR

## What every endpoint must specify

For each endpoint:
1. **Method + path** with version prefix (`/api/v1/...`)
2. **Auth requirement** (public, authenticated, role X)
3. **Request schema** with required fields, types, validation rules
4. **Response schema** for 200 and key error codes (400, 401, 403, 404, 409, 500)
5. **Pagination strategy** if returning a list
6. **Idempotency** strategy for mutations (idempotency-key header?)
7. **Rate limit** annotation (if non-default)
8. **One example** of both request and response

## Cross-cutting conventions (`04-api-conventions.md`)

- **URL**: kebab-case resources, plural nouns (`/api/v1/orders`),
  nested only 1 level (`/api/v1/orders/{id}/items`, not deeper)
- **HTTP method semantics**: GET = idempotent read, POST = create,
  PUT = full replace, PATCH = partial update, DELETE = soft by default
- **Status codes**: 200 success with body, 201 created with
  `Location` header, 204 no content, 400 client input error,
  401 unauthenticated, 403 unauthorized, 404 not found, 409 conflict
  (e.g. duplicate), 500 server error
- **Error response shape** (consistent across all endpoints):
  ```json
  {
    "code": "ORDER_NOT_FOUND",
    "message": "Order 123 not found",
    "traceId": "abc-123",
    "details": {}
  }
  ```
- **Pagination**: cursor-based for >10k records, offset-based OK for
  smaller lists; always include `total` when offset-based
- **Time**: ISO 8601 UTC, with `Z` suffix, no local timezones
- **Versioning**: URL path (`/api/v1/...`); breaking changes bump
  major; non-breaking add new optional fields
- **Idempotency**: POST mutations accept `Idempotency-Key` header;
  store key for 24h, return same response on replay

## How to design well

1. **List every resource first.** Pull nouns from the prototype:
   order, user, store, item, inventory, sale. These become URL
   resources.

2. **Then list actions per resource.** Most actions map to CRUD;
   special actions go under `/api/v1/{resource}/{id}/{action}` (e.g.
   `/orders/{id}/cancel`).

3. **Always include the 4xx error responses.** Teams that skip 401/403
   in the contract always rebuild them under pressure later.

4. **Reject field-name inconsistency.** If one endpoint returns
   `userId` and another `user_id`, the frontend writes 2 parsers.
   Pick one style (camelCase for JSON) and enforce it.

5. **Don't expose internal IDs as primary keys if there's a privacy
   concern.** Use surrogate IDs and a separate external reference
   (order number) for human-facing flows.

6. **Bulk operations get their own endpoint.** Don't make clients
   loop calling POST 100 times; design `POST /api/v1/orders/bulk`.

7. **Webhooks and async operations need explicit design.** Don't
   pretend everything is sync. If the backend needs 30s to process,
   return 202 + a polling endpoint, or push via webhook.

## OpenAPI skeleton (minimal example)

```yaml
openapi: 3.0.3
info:
  title: Inventory API
  version: 1.0.0
servers:
  - url: https://api.example.com/api/v1
paths:
  /auth/login:
    post:
      summary: Login with phone + SMS code
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [phone, code]
              properties:
                phone: { type: string, pattern: '^1[3-9]\d{9}$' }
                code:  { type: string, pattern: '^\d{6}$' }
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LoginResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'
components:
  schemas:
    Error:
      type: object
      properties:
        code: { type: string }
        message: { type: string }
        traceId: { type: string }
  responses:
    Unauthorized:
      description: Missing or invalid credentials
      content:
        application/json:
          schema: { $ref: '#/components/schemas/Error' }
```

## Exit gate
- [ ] Every P0 feature in `01-requirements.md` maps to ≥1 endpoint
- [ ] Every endpoint has request + response + error schemas
- [ ] Conventions doc covers error shape, pagination, time, versioning
- [ ] Frontend and backend both signed off (this is the contract — both
      sides commit to it)
- [ ] OpenAPI doc validates (run through Swagger CLI or Apifox import)

## Common failure modes
- Vague types (`object` instead of a schema) — frontend can't
  generate types
- Missing 4xx responses — frontend writes its own error guessing
- Date format inconsistent — bugs appear at year boundaries
- Mixing sync and async semantics on the same resource — frontend
  doesn't know whether to poll
- No idempotency on POST — duplicate orders on retry
