# Storyboard JSON schema (v4)

`storyboard.json` carries the brand profile reference, the style anchor reference, the narrative (1 first_frame_prompt + 1 motion_prompt for single take), and optionally a `takes` array for >15s multi-take continuation.

## Single-take 15s (default)

```json
{
  "version": 4,
  "subject": "Notely — AI note-taking app",
  "aspect_ratio": "9:16",
  "resolution": "1K",
  "total_duration_sec": 15,
  "brand_profile_ref": "brand_profile.json",
  "style_anchor_ref": "style_anchor.json",
  "music": {
    "mood": "warm cinematic",
    "prompt": "ambient cinematic pulse with warm Rhodes keys, 70 BPM, no vocals, 15 seconds, gentle sub-bass swell every 4 bars",
    "file": "audio/bg.mp3"
  },
  "brand_assets": {
    "first_frame": {
      "image_path": "brand/notely-editor.png",
      "description": "Notely main editor screen, dark mode, with the New Note button highlighted"
    },
    "end_card": {
      "image_path": "brand/notely-logo.png",
      "description": "Notely wordmark, transparent PNG"
    }
  },
  "narrative": {
    "first_frame_prompt": "Near-black background with a warm undertone. A small Notely wordmark glyph materializes in the dead center, surrounded by a soft warm coral glow ring. No other text. Minimal.",
    "motion_prompt": "The wordmark fades in from black and settles. The coral glow ring expands and contracts once, like a slow inhale. A rounded-rectangle 'Capture' card slides up from below the frame with a soft spring; a small magenta dot pulses in its top-right corner. A cursor of light drifts in from the right, makes contact with the card, drags it slightly rightward; a soft coral glow trail follows. The card dissolves into a horizontal coral-to-magenta-to-violet spectrum ribbon, and the wordmark re-anchors above. The video ends on a clean end card: 'Notely' in light serif with a soft coral glow, the tagline 'Thought, in motion.' below, and App Store and Google Play badges in monochrome outline at the bottom. The frame holds on the end card."
  }
}
```

## Multi-take (30s+, 2-3 takes with continuation)

Add a `takes` array. Take 1 uses the brand asset or generated first frame. Take N+1's `first_frame_source: "continued"` means its first frame is the last frame of take N.

```json
{
  "version": 4,
  "subject": "AURA Smart Home — 30s product film",
  "aspect_ratio": "9:16",
  "resolution": "1K",
  "total_duration_sec": 30,
  "brand_profile_ref": "brand_profile.json",
  "style_anchor_ref": "style_anchor.json",
  "music": {
    "mood": "warm acoustic",
    "prompt": "gentle acoustic morning, soft nylon guitar, 70 BPM, no vocals, 30 seconds",
    "file": "audio/bg.mp3"
  },
  "narrative": {
    "summary": "Two 15s takes with continuation. Take 1: cold open + reveal + first interaction. Take 2: deeper demo + end card."
  },
  "takes": [
    {
      "index": 1,
      "duration_sec": 15,
      "first_frame_source": "generated",
      "first_frame_prompt": "Warm cream wall with a soft window-light gradient. A small AURA home glyph fades in center-screen.",
      "motion_prompt": "The AURA home glyph materializes, then a room-card grid fades in (Living Room / Bedroom / Kitchen / Bathroom). The 'Bedroom' card highlights in coral. The view switches into the Bedroom card; a 'Good Night' scene pill highlights.",
      "first_frame_file": "frames/take-1.png",
      "last_frame_file": "frames/take-1-last.png",
      "clip_file": "clips/take-1.mp4"
    },
    {
      "index": 2,
      "duration_sec": 15,
      "first_frame_source": "continued",
      "motion_prompt": "From the highlighted 'Good Night' scene, the background shifts to soft blue (evening), the light card drops to 5%, the curtain closes to 0%, and the AC card highlights in sage green. The view zooms out to show the full home, then the end card fades in: the AURA home glyph + 'AURA — The Home That Glows.' in serif, with App Store and Google Play badges in color below. The frame holds.",
      "first_frame_file": "frames/take-1-last.png",
      "clip_file": "clips/take-2.mp4"
    }
  ]
}
```

## Version

- `version: 4` — the schema after the single-take redesign. Replaces v3 (which had a `shots` array, deprecated — single-take replaces multi-cut). v4 supports `narrative` for single-take and an optional `takes` array for >15s.

## Top-level fields

- `version` — `4`.
- `subject` — one-line description.
- `aspect_ratio` — `9:16` or `16:9`.
- `resolution` — `1K` for 9:16, `2K` for 16:9.
- `total_duration_sec` — must equal the sum of `takes[*].duration_sec` (or the implicit single take).
- `brand_profile_ref` — path to brand_profile.json.
- `style_anchor_ref` — path to style_anchor.json.

## Brand assets

`brand_assets` is optional. A map from slot to asset descriptor.

| Slot | Used for |
|---|---|
| `first_frame` | The i2v input for take 1. The actual brand asset (logo, product screenshot) becomes the first frame of the video. |
| `end_card` | The brand mark for the end card beat. Either composited over the last frame by the i2v, or used as the i2v's reference for the end card beat. |

| Field | Type | Notes |
|---|---|---|
| `image_path` | file path (workspace-relative) | PNG or JPG. Transparent PNGs work best for logos |
| `description` | string | What the image is, for the model's reference |

## Narrative (single-take case)

`narrative` is required for single-take. It has 2 fields:

- `first_frame_prompt` — required if `brand_assets.first_frame` is not set. The static first frame. Colors come from `brand_profile.colors`, typography from `brand_profile.typography`, geometry from style anchor.
- `motion_prompt` — required. 2–4 sentences walking through the 5 beats: cold open → reveal → interaction → wow → end card. Use the brand's color names and the style anchor's motion verbs.

## Takes (multi-take case)

`takes` is required for >15s. Each take:

| Field | Type | Notes |
|---|---|---|
| `index` | number | 1-based |
| `duration_sec` | number | 6, 10, or 15 |
| `first_frame_source` | enum | `"generated"` (default), `"brand_asset"` (use `brand_assets.first_frame`), or `"continued"` (use previous take's last frame) |
| `first_frame_prompt` | string | Required when `first_frame_source: "generated"`, ignored otherwise |
| `motion_prompt` | string | Required. Describes the motion for this take only — the model doesn't see the other takes |
| `first_frame_file` | path | Where the first frame is saved / loaded from |
| `last_frame_file` | path | (Optional) Where the last frame will be extracted for continuation |
| `clip_file` | path | Where the i2v output is saved |

Take 1's `first_frame_source` is `"generated"` or `"brand_asset"`. Subsequent takes' `first_frame_source` is `"continued"`, meaning the first frame is extracted from the previous take's last frame.

## Validation

Sum check: `Σ takes[*].duration_sec == total_duration_sec` (when `takes` is present).

Brand coherence: every prompt that mentions a color uses a color from `brand_profile.colors` (or a derived shade). Stray colors = bug.

Motion coherence: motion verbs come from the style anchor's motion signature, not invented.

Word count: `first_frame_prompt` 20–60 words. `motion_prompt` 60–150 words (it's the full narrative).

End card: when `brand_assets.end_card` is set, the end card beat in the motion_prompt must reference the real brand mark in the brand's font and color — not a generic glyph.
