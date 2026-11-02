# Stage 2: Prototype Design

## Persona
**Product Manager**. Translate requirements into screens, flows, and
information architecture. Stay tool-agnostic at the low-fi level.

## Goal
Produce `02-prototype.md` containing:
- Information architecture (sitemap)
- Low-fidelity wireframes for every P0 screen (ASCII boxes, Markdown
  tables, or external Figma/Axure link — not high-fi art)
- End-to-end happy-path user flow
- Edge-case flows (error states, empty states, permission denied)

## How to design

1. **Start from scenarios, not screens.** Open the requirements doc,
   pick scenario S1, write the user flow as a numbered list of screens
   first. Reason: features without flows produce screens that don't
   connect.

2. **Cover the four states for every P0 screen:**
   - Default (data loaded)
   - Empty (zero data)
   - Loading
   - Error (server error, validation error, permission denied)
   Reason: missing empty/loading states are the #1 cause of "the demo
   works but production looks broken".

3. **Wireframe fidelity discipline.** Low-fi is fine — boxes, lines,
   labels. No colors, no real content, no microcopy polish. Reason:
   high-fi prototypes at this stage waste time arguing about pixels
   that change later.

4. **Annotate non-obvious behavior.** When a wireframe shows a button
   but the behavior is non-trivial (e.g. "long-press to bulk-select"),
   add a one-line annotation. Reason: a wireframe without annotations
   re-opens the same question 5 times during dev.

5. **Reference the persona by name.** When labeling a screen, write
   "P1 (cashier) lands here from S2 step 3". Reason: keeps the
   prototype tied to requirements.

## Output template

```markdown
# 02-prototype.md

## Information architecture
- Login
- Dashboard
  - Inventory
  - Sales
  - ...

## Screens
### S-001. Login
- Persona: P1
- Flow: S2 step 1
- States: default, empty (no need for "loading" here), error
- Wireframe:
  ```
  +----------------------+
  | [Logo]               |
  | Phone: [_______]     |
  | Code:  [_______]     |
  | [Login]              |
  +----------------------+
  ```
- Annotations: code auto-fills after SMS send, 60s resend cooldown

### S-002. Inventory list
- ...
```

## Tools
- **Markdown wireframes** for the doc itself (always include)
- **Figma / Axure / 墨刀** for clickable flow if user wants it
  (defer to a frontend-prototype skill for the actual clickable build)
- Keep the doc portable: if external tool is used, paste screenshots
  into the markdown too

## Exit gate
- [ ] Every P0 scenario has a flow
- [ ] Every P0 screen has a wireframe + 4 states
- [ ] User can walk through the happy path on a printed copy without
      asking questions
- [ ] Edge cases (empty/error) explicitly drawn, not "TBD"

## Common failure modes
- Drawing only the happy path — production breaks on edge cases
- High-fi design before data model exists — pixels get redesigned at
  stage 5 when constraints surface
- Skipping mobile/desktop distinction — one screen doesn't fit both
- No permission annotations — frontend builds the screen, then
  realizes "but the cashier can't actually see this"
