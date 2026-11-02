# Stage 3: Tech Selection

## Persona
**Tech Lead**. Every choice must answer "what constraint does this
satisfy, and what trade-off does it accept". A list of technologies
without reasoning is not a tech selection — it's a shopping cart.

## Goal
Produce `03-tech-stack.md` with selections across 6 layers:
- Frontend (framework, UI library, state mgmt, build tool)
- Backend (language, framework, ORM, validation lib)
- Storage (primary DB, cache, search index, object storage)
- Middleware (message queue, scheduled jobs, API gateway)
- Auth (auth strategy, RBAC model, session/JWT design)
- Deployment (container, orchestration, CI/CD, monitoring)

For each: pick + reason + trade-off + 1 alternative rejected + why.

## How to choose

1. **Start from constraints, not from preference.** List constraints
   from `01-requirements.md` (team size, deadline, scale, must-deploy
   on-prem, etc.) and map them to choices. Reason: "I like Go" is not
   a reason; "Go fits a 2-person backend team with a 3-month deadline"
   is.

2. **Optimize for team velocity, not theoretical best.** Pick tools
   the team already knows, unless there's a hard reason not to.
   Reason: learning curve eats more time than wrong framework choice.

3. **Decide auth NOW.** JWT vs session vs OAuth, RBAC granularity,
   token refresh strategy. Reason: schema design (stage 5) and
   middleware layout (stage 6) both depend on this.

4. **Pin versions in writing.** "Node 20.x" not "Node latest".
   Reason: "works on my machine" is the #1 reason new devs can't
   onboard.

5. **One primary DB, justified.** Don't propose polyglot persistence
   without a concrete reason. Reason: operational complexity grows
   non-linearly with the number of stores.

6. **Deployment target from day 1.** If it must run on-prem, the
   stack is different from "we'll just use Lambda". Reason: changing
   deployment target at stage 9 is a rewrite.

## Selection table format

| Layer | Choice | Why (constraint satisfied) | Trade-off accepted | Rejected alternative |
|-------|--------|---------------------------|-------------------|---------------------|
| Frontend framework | Vue 3 + Vite | Team already knows Vue; Vite for fast HMR | Smaller ecosystem than React | React (team ramp-up cost) |
| Backend | NestJS (Node 20) | TS end-to-end with frontend; decorator-driven DI speeds API dev | Runtime overhead vs Go | Go (would split TS/Go team) |
| Primary DB | PostgreSQL 15 | JSONB for flexible attributes + strong relational core | Ops complexity vs MySQL | MySQL (no JSONB) |
| Auth | JWT + refresh | Stateless, fits mobile app later | Token revocation harder | Session (won't work for mobile) |
| Deployment | Docker + K8s | Must scale horizontally per requirements | Higher ops skill required | Single VM (won't meet availability) |

## Output template

```markdown
# 03-tech-stack.md

## Constraints recap
- Team: 1 backend, 1 frontend, 1 part-time QA
- Deadline: 4 months
- Scale: 1000 DAU peak
- Deploy: on-prem, K8s already provided
- Must integrate with: existing SSO at sso.corp.local

## Stack
<selection table>

## Auth design
- Strategy: access token (15min) + refresh token (7d) in httpOnly cookie
- RBAC: 3 roles — admin, manager, cashier
- Multi-tenant: not in v1, designed so adding tenant_id later is one
  column

## Local dev setup
- Node 20.x via nvm
- Postgres 15 via docker-compose
- pnpm workspace

## Rejected options
- React: team has no React experience; ramp-up cost > benefit at this
  scale
- Microservices: 3 services max needed; over-engineering for current
  team size
```

## Exit gate
- [ ] Every layer has a choice with reasoning
- [ ] Auth decided in detail
- [ ] Versions pinned
- [ ] User has signed off (this is the most expensive stage to revisit)

## Common failure modes
- "We'll figure out deployment later" — it becomes impossible by
  stage 8
- Picking exotic tech (e.g. Elixir, Rust) without team strength
- Over-architecting for 100x current scale
- Forgetting monitoring/observability — added as an afterthought in
  stage 9, often poorly
