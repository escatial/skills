# Available sizes & host behavior

Read this only when the task explicitly targets Canvas, a pinned window, or fullscreen. Skip
this reference for conversation-only widgets, including dashboards and multi-panel compositions;
their complete layout guidance is in "Size in conversation" in `../SKILL.md`.
`design-system.md` owns the visual style on every surface.

Placement geometry — grid units and span limits — is owned by the `canvas` skill's "Current Size
Model". The examples below use that model to help you choose a size.

## Available Canvas sizes

The grid has 12 columns, with 80px columns, 32px rows, and 12px gaps. A span of `w x h` renders at
`w*80 + (w-1)*12` wide by `h*32 + (h-1)*12` high.

| Placement | Grid span | Rendered size |
|---|---|---:|
| Minimum | 2 x 2 | 172 x 76 |
| Default | 5 x 8 | 448 x 340 |
| Maximum | 12 x 33 | 1092 x 1440 |

Choose a span within these limits that suits the content; intermediate spans are available.
Designing and checking one chosen size is sufficient unless the user requests multiple sizes.
The minimum and maximum describe available placements, not required design or test targets.

For dashboards, wide or near-square placements are useful starting points for metrics,
comparisons, and trend charts, especially when several widgets need to be visible together.
Lists and timelines may benefit from a taller placement. Let the content guide the proportions;
no aspect ratio is required. Compare rendered pixels, not grid counts: the default `5 x 8` span
is `448 x 340px`, so it is wider than it is tall.

Canvas and pinned-window viewports are sized by the host. Fullscreen uses the available window
area and has no fixed pixel size. The same HTML document is used across surfaces; this does not
require a layout optimized for every surface or for every step of a resize.

## Keep the top strip free of controls

Current Desktop hosts overlay drag regions and hover actions at the widget's top edge:

- Canvas placements: the drag strip starts 8px from the top and is 32px tall in normal interaction.
- Pinned windows: the header hit area occupies the top 32px.
- Hover action buttons also occupy the top-right corner.

The widget runtime does not expose these overlay bounds. Keep your pointer targets clear of them;
reserving roughly the top 40px for non-interactive content is a useful convention:

- Put only non-interactive content in the top ~40px — titles, labels, status text.
- Keep buttons, chips, menus, and any pointer targets below that strip and out of the top-right
  corner.

Conversation and fullscreen surfaces have no such drag overlay; this reservation does not apply
there.

## Optional host size tier

The host continuously classifies the iframe viewport and exposes it as `data-daimon-size-tier` on
the root `<html>` element:

| Value | Condition |
|---|---|
| `compact` | width < 300px or height < 220px |
| `expanded` | width >= 760px and height >= 500px |
| `regular` | everything in between |

The attribute updates live as the placement resizes. The pre-loaded CSS ships no tier styles.
If you choose to support multiple sizes, you may use attribute selectors to adjust your styles,
or choose breakpoints that better suit the content. A design for one target size can ignore it.
