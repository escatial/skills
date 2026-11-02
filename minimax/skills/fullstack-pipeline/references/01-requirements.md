# Stage 1: Requirements Brainstorming

## Persona
**Account Manager + Domain Expert**. The job is to surface business pain
the user hasn't articulated yet. Avoid jumping to solutions or tech
choices — that's stage 3.

## Goal
Produce `01-requirements.md` that captures:
- User personas (1-3 typical users with concrete traits, not "everyone")
- Business scenarios (3-7 scenarios, each with a trigger, actors, and
  the success state)
- Functional requirements list, each tagged P0/P1/P2
- Non-functional requirements (performance, security, compliance,
  availability, i18n, accessibility — pick what's relevant)
- Success metrics (e.g. "cashier can complete inventory check in <3 min")

## How to run the brainstorm

1. **Open with 3-5 clarifying questions**, not a feature list. Good
   opening questions:
   - "Who will use this every day vs. occasionally?"
   - "What's the worst part of their current workflow?"
   - "What does success look like 3 months after launch?"
   - "Is there anything competitors do that you specifically don't want?"

2. **Use the 5-Why loop on each candidate feature.** When the user
   says "we need a dashboard", ask "what decision will the user make
   because of this dashboard?" — keep asking until you hit the actual
   decision. Reason: features serving no decision get built and
   abandoned.

3. **Surface implicit assumptions.** When the user says "users will
   log in with phone number", push back: "what if a store has shared
   tablets? Single account per device?" Reason: implicit assumptions
   become hard bugs at stage 5.

4. **Use MoSCoW or P0/P1/P2** to force a cut. P0 = cannot launch
   without; P1 = important but not blocking; P2 = nice to have.
   Reason: a project that ships P2 before P0 dies in the first month.

5. **End with a "non-goals" section.** List 3-5 things explicitly out
   of scope. Reason: scope creep is the #1 reason fullstack projects
   ship late.

## Output template

```markdown
# 01-requirements.md

## Project name
<one-liner>

## Personas
### P1. <name> — <role>
- Background: ...
- Pain today: ...
- Success looks like: ...

## Business scenarios
### S1. <scenario name>
- Trigger: ...
- Actor: P1 (cashier)
- Pre-condition: ...
- Flow: ...
- Success state: ...
- Failure modes: ...

## Functional requirements
| ID | Feature | Priority | Scenario |
|----|---------|----------|----------|
| F-001 | Phone+password login | P0 | S2 |
| ... | ... | ... | ... |

## Non-functional requirements
- Performance: list page P95 < 500ms
- Security: ...
- Availability: 99.5% monthly
- Data retention: ...

## Success metrics
- M1. <measurable>

## Non-goals
- NG1. <out of scope>
```

## Exit gate (do not advance until these are true)
- [ ] Every P0 feature traces back to a scenario
- [ ] User can articulate the success state for each persona
- [ ] Non-goals section is non-empty
- [ ] User has explicitly approved the doc

## Common failure modes
- Feature list with no scenarios — leads to un-prioritizable backlog
- Solution language ("we need a microservice for X") — that's stage 3
- Missing non-functional requirements — found too late, expensive to fix
- Skipping non-goals — scope explodes by stage 4
