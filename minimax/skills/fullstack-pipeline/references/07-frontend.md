# Stage 7: Frontend Development

## Persona
**Frontend Engineer**. Implement the prototype from stage 2 against
the API contract from stage 4. Develop against mocks until stage 8
integration.

## Goal
Produce a working frontend with:
- Project scaffold (chosen framework, build tool, UI library)
- Routing + state management + base layout
- Auth flow (login, token storage, refresh, logout)
- P0 pages rendered against mock data
- P0 pages wired to the real API (during stage 8)

## Implementation order

1. **Scaffold first.** Get the dev server running with a placeholder
   home page. Reason: every later step needs the toolchain live.

2. **Cross-cutting infrastructure:**
   - HTTP client wrapper (axios/fetch) with interceptors:
     - Attach auth token
     - Refresh on 401 (single refresh, queue subsequent requests)
     - Normalize error to the API error shape from stage 4
   - Global state (Pinia/Redux/Zustand) for: auth, current user,
     theme/locale
   - Router with auth guards (redirect to login if unauthenticated)
   - Token storage decision: `httpOnly cookie` if backend supports;
     otherwise `localStorage` with documented XSS risk
   - Base layout: header (user menu, logout), sidebar (nav), main,
     footer
   - Loading / empty / error components reused across pages

3. **Mock service worker setup.** Use MSW (Mock Service Worker) or
   a tool like Apifox's mock server. Generate mocks from
   `04-api-contract.yaml` if possible. Reason: lets frontend ship
   without waiting for backend.

4. **P0 pages, in this order per page:**
   - Static structure matching the stage 2 wireframe
   - Mock data wiring
   - Form validation matching the API schema
   - Loading / empty / error states
   - Permission checks (hide actions user can't do)
   Reason: order matters because cross-page patterns (table, form)
   emerge early; refactoring at page 20 is 10x the cost of page 3.

5. **Auth flow:**
   - Login page → POST /auth/login → store token → redirect
   - Token refresh on 401 (transparent retry once)
   - Logout clears token and redirects
   - Refresh-token rotation if backend supports it

6. **Don't refactor the prototype away.** The stage 2 wireframe is
   the spec; if a screen needs to deviate, update the prototype
   doc and the user, then the code. Reason: design drift between
   what was approved and what gets built.

## Page structure (typical)

```
src/
├── api/                 # generated or hand-written client
├── components/
│   ├── common/          # Button, Input, Modal
│   └── business/        # OrderTable, InventoryCard
├── pages/               # route components
│   ├── Login.tsx
│   ├── Dashboard.tsx
│   ├── Inventory/
│   │   ├── List.tsx
│   │   └── Detail.tsx
│   └── ...
├── stores/              # auth, user, ...
├── router/
├── layouts/
├── mocks/               # MSW handlers
└── main.tsx
```

## What to test (frontend)

- **Component test** (Vitest / React Testing Library): form
  validation, conditional rendering, key user interactions
- **E2E** (Playwright / Cypress): leave for stage 8 — they need
  the backend
- **NOT in scope here**: full accessibility audit, performance
  optimization (defer to stage 8/9)

## Exit gate
- [ ] P0 pages render correctly with mock data
- [ ] Auth flow works end-to-end with mock auth
- [ ] All 4 screen states (default, empty, loading, error) covered
- [ ] No P0 page has a known Sev1 bug against mocks
- [ ] Frontend builds and runs with one command

## Common failure modes
- Building pages without mock data, waiting for backend — frontend
  blocked
- Putting business logic in components instead of stores/services —
  impossible to test, impossible to reuse
- Token in `localStorage` when XSS is a real threat — session
  hijack
- No request deduplication — refresh on 401 causes infinite loop
- Form validation diverges from API validation — bad UX, double work
- Hiding "permission denied" errors — user clicks button, nothing
  happens, no feedback
