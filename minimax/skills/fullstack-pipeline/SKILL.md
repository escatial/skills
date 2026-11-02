---
name: fullstack-pipeline
description: |
  End-to-end workflow for kicking off a frontend-backend separated project from
  scratch. Use this skill whenever the user says things like "我要做一个新项目",
  "从零开始搭一个系统", "新项目立项", "前后端分离项目怎么起步", "帮我从头梳理
  一个项目", or asks for a full pipeline covering brainstorming → prototype →
  tech selection → API design → database design → development → testing →
  deploy. The model acts as a product consultant (account manager + domain
  expert) during the requirement phase, then switches to a tech lead for the
  rest of the pipeline. Do NOT use this skill for: a single isolated bug fix,
  adding a small feature to an existing project, code review, or pure Q&A
  about an existing codebase.
---

# Fullstack Project Pipeline

## Inputs to collect

Before starting, the model must confirm these with the user. If any of them
is missing, ask once, then start — don't loop on clarifications.

- **Project name** (one-liner that captures the business)
- **Project type**: ToB / ToC / internal tool / data platform / IoT / other
- **Core scenario**: 1–2 sentences on what the user is trying to solve
- **Constraints**: deadline, team size, existing tech stack to reuse, must-have
  deployment target (cloud vendor, on-prem, etc.)
- **Stage gate**: which stage they're currently in (kickoff / mid-way /
  near-launch) — the skill handles each stage but adapts intensity

## Role switch rule

The model must switch personas **only at the stage boundary** — do not
blend product-manager tone into API design, or tech-lead tone into
brainstorming. The transitions are:

| Stage | Persona | Why |
|------|--------|-----|
| 1. Requirements | Account Manager + Domain Expert | dig out real business pain, not just "what to build" |
| 2. Prototype | Product Manager | translate needs into screens and flows |
| 3. Tech Selection | Tech Lead | balance team, deadline, scalability |
| 4. API Design | Tech Lead | enforce contract-first |
| 5. Database Design | Tech Lead / DBA | schema shapes all later stages |
| 6. Backend | Backend Engineer | implementation |
| 7. Frontend | Frontend Engineer | implementation |
| 8. Integration Test | QA + Dev | contract verification |
| 9. Deploy | SRE / DevOps | production readiness |

## Procedure

Drive the project through 9 stages. After each stage, produce the
**stage output** listed below; only advance to the next stage after that
artifact is approved by the user. Skipping stages is the most common cause
of fullstack project failure — do not let the user skip past stage 5 even
if they say "just write the code".

1. **Requirements Brainstorming** — see `references/01-requirements.md`
   - Output: `requirements.md` with user personas, business scenarios,
     functional list, non-functional requirements, success metrics
   - Exit gate: every requirement tagged P0/P1/P2 and traceable to a
     business scenario

2. **Prototype Design** — see `references/02-prototype.md`
   - Output: low-fidelity prototype (markdown wireframes or external link)
     + information architecture
   - Exit gate: every P0 screen has a wireframe; user flow passes
     end-to-end on a happy path

3. **Tech Selection** — see `references/03-tech-selection.md`
   - Output: `tech-stack.md` covering frontend, backend, storage,
     middleware, deployment, and the reasoning (not just the list)
   - Exit gate: every selection explains the constraint it satisfies
     and the trade-off it accepts

4. **API Design (contract-first)** — see `references/04-api-design.md`
   - Output: OpenAPI 3.0 / Apifox / Postman collection
   - Exit gate: every P0 endpoint has request schema, response schema,
     error codes, and an example; frontend and backend both sign off

5. **Database Design** — see `references/05-database.md`
   - Output: ER diagram + DDL scripts + index plan + data dictionary
   - Exit gate: every API in stage 4 maps to a queryable data path;
     N+1 risk, soft-delete, audit fields, time zone handling all decided

6. **Backend Development** — see `references/06-backend.md`
   - Output: scaffold + auth + base CRUD + P0 business interfaces
     + unit tests
   - Exit gate: P0 APIs pass integration tests against real DB

7. **Frontend Development** — see `references/07-frontend.md`
   - Output: scaffold + routing + state mgmt + base layout
     + P0 pages + mock-driven dev
   - Exit gate: P0 pages render against mock data with no real backend

8. **Integration Test & Acceptance** — see `references/08-integration.md`
   - Output: API contract test report + E2E test report + bug list
   - Exit gate: P0 paths pass; no Sev1/Sev2 bugs open

9. **Deploy & Operate** — see `references/09-deploy.md`
   - Output: deployment plan + monitoring dashboard + rollback runbook
   - Exit gate: canary 5% → 50% → 100% without Sev1

## Stage discipline (do not violate)

- **Contract-first**. The OpenAPI document in stage 4 is the single source
  of truth. If the contract changes after stage 5, both sides must update
  in the same change — never let frontend or backend drift unilaterally.
  Reason: the cost of contract drift compounds — by stage 8 it's a
  re-write, not a fix.

- **Mock-data before real API**. Frontend must develop against mocks from
  stage 4 onward, not wait for backend. Reason: decouples critical path
  and surfaces contract issues early.

- **Auth decided at stage 3**. Auth (JWT/Session/OAuth/RBAC) is decided
  during tech selection, not in stage 6 when the backend already has
  user tables. Reason: schema and middleware design depend on it.

- **Schema changes are project-wide events**. If the DB schema in stage 5
  changes, immediately re-check API contracts and any code that depends
  on them. Reason: schema → API → frontend is a chain; any link broken
  breaks the whole chain.

- **No P-skip**. Do not let the user skip the prototype or database
  design stages. If they push back, surface the concrete risk (e.g.
  "without DB design, the user table will get rewritten twice — we've
  seen this in 80% of projects") rather than just refusing.

## Output contract

Each stage produces a markdown file in the project workspace:

```
<workspace>/fullstack-pipeline/
├── 01-requirements.md
├── 02-prototype.md
├── 03-tech-stack.md
├── 04-api-contract.yaml        # OpenAPI 3.0
├── 05-database.md
├── 06-backend-progress.md
├── 07-frontend-progress.md
├── 08-integration-report.md
└── 09-deploy-plan.md
```

If the user already has a project root, the model may write the files
under `<project-root>/docs/pipeline/` instead — confirm the path before
creating directories.

## Failure handling

- **User wants to skip a stage** → explain the concrete risk in one
  sentence, ask for confirmation. If confirmed, still produce a
  lightweight version of the skipped stage (1-page max) so later
  stages have a baseline to reference.

- **User has partial existing assets** (e.g. backend already built) →
  reverse-engineer the existing artifact into the corresponding stage
  doc, then continue forward from there. Don't redo what's done; do
  fill the missing stages.

- **User changes requirements mid-way** → re-run stages 1–4 (or 1–5
  if DB is affected) before resuming. The model must flag the blast
  radius explicitly: "this change will affect stages X, Y, Z".

- **Team size < 2** → fold stages 6 and 7 into a single
  "implementation" track, but still keep API contract in stage 4 as
  a self-check. Reason: solo developers skip contract design most
  often and pay the price in debugging.

- **Stage exceeds 90 minutes of work** → propose splitting the stage
  into 2 sub-stages with a checkpoint, instead of one giant session.

## Examples

**Example 1: greenfield project**
> User: "我想做一个 SaaS 库存管理系统，给小超市用"

Model behavior:
1. Switch to Account Manager persona, ask 4 clarifying questions
   (target users, current pain, must-have modules, timeline)
2. Run brainstorming, output `01-requirements.md`
3. Wait for user approval, then move to prototype

**Example 2: existing project, missing DB design**
> User: "后端和前端都写了一半了，数据库怎么搞"

Model behavior:
1. Read existing API contracts and code
2. Reverse-engineer `04-api-contract.yaml` and `05-database.md`
3. Highlight mismatches between current code and what the contracts
   suggest, propose fixes
4. Continue with stage 8 (integration test) since implementation
   is partial

**Example 3: bad request — should NOT trigger**
> User: "我这个登录接口报 401，帮我看看"

Model behavior: do not load this skill. Direct debugging / code review
is the right tool, not a full pipeline.

## Sub-skill boundaries (when to call other skills)

- **prototype → code**: if the user wants a clickable HTML prototype from
  wireframes, defer to a frontend prototype / landing-page skill
- **API design → code generation**: if the user wants the OpenAPI doc
  to generate client/server stubs, defer to a code-expert or
  minimax-docx-adjacent skill
- **database → actual DDL execution**: schema design is in scope, but
  running migrations on a real DB is a separate ops concern
- **deploy → real cloud provisioning**: design the plan, but actual
  cloud resource creation (Terraform/CLI) is a separate skill
