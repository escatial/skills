---
name: widgetdesign
description: Kimi widget design system. Read this BEFORE rendering any inline widget. Covers the runtime contract and conversation layout; read references/design-system.md for visual style and host components.
---

# Kimi Widget

Design compact visual or interactive answers using the system prompt's Default visual policy.
Choose the layout, chart form, density, and interactions that best serve the content within the
Kimi design system. Static visuals are sufficient when interaction adds no value.

## Choose the display surface

Default to inline conversation display unless the task explicitly targets another surface.
A dashboard, comparison, or multi-panel composition can still be a conversation widget.

- **Conversation only:** use the complete layout guidance in "Size in conversation" below.
  Do not read `references/layout-and-sizing.md` or the `canvas` skill for layout; grid spans,
  drag regions, and placement size tiers do not apply to this task.
- **Explicitly targeting Canvas, a pinned window, or fullscreen:** read
  [references/layout-and-sizing.md](references/layout-and-sizing.md) for available sizes and
  host behavior, then choose a target size.
- **Moving a conversation widget onto Canvas:** read the layout reference even if the inline
  version already renders well. Follow the `canvas` skill's conversion guidance: inspect the
  existing HTML and adjust only what the chosen placement needs, preserving what works.

## Read the visual guidance

Unless the user has already specified the precise styling for this widget, you MUST read
[references/design-system.md](references/design-system.md) before writing code. It contains
visual rules, reusable host classes, component examples, and the token map. Small or static
widgets still use it.

If using icons, also read [references/icon-system.md](references/icon-system.md) for the manifest,
exact `<kimi-icon>` names, sizing, and construction rules.

## Runtime contract

The widget runs in a sandboxed iframe with the Kimi design system CSS already loaded. Use its
variables and component classes; never redefine them or hardcode colors, fonts, or radii.

- Use HTML, SVG, CSS, inline JavaScript, and native browser APIs.
- Do not use external scripts, modules, stylesheets, images, fonts, CDN libraries, npm packages,
  `fetch`, or WebSocket. Build charts and diagrams with SVG, Canvas, CSS, or the DOM.
- Keep explanatory prose, introductions, and summaries in the surrounding response. After the
  widget renders, add only information it cannot show; do not repeat or narrate the visual.
- Put content in one root wrapper with `padding-block-start: var(--kimi-space-4)` and
  `padding-inline: var(--kimi-space-4)`. Bottom padding follows the composition.

## Design for the intended size

Choose a target size that suits the content and surface; use the user's requested size when
provided. A widget that works well at one chosen size is a complete result. Check that size;
additional layouts, compact summaries, and fullscreen adaptations are optional unless requested.
Available sizes and component examples inform the design without prescribing its composition.

## Size in conversation

- Connect the visual to the surrounding answer and avoid unnecessary scrolling. There is no
  preferred portrait or landscape ratio: the content column sets width and content sets height.
- Let the outer wrapper fit the content column with `width: 100%`.
- Keep `html`, `body`, and the outer wrapper in normal document flow, with height following
  content. Avoid viewport-based root heights such as `height: 100%` or `100vh`, and spacers that
  inflate the measured height. Size individual charts and controls as their design requires.
- Aim to keep the inline composition within 720px, the current Desktop's inline frame height cap.
  Do not add empty space to reach that height. Simplify or reveal details through interaction
  when the content would otherwise outgrow the conversation.
