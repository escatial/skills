---
name: ui-motion
description: |
  Generate single-take 15-second UI motion graphics videos driven by the user's actual brand visual (uploaded images + text description). One continuous take, no hard cuts — matches the Lumen / youmotion / Hailuo reference aesthetic where a glyph / card / cursor morphs naturally through 5 beats into a brand end card. Use when the user asks for a UI animation, App promo reel, brand film, "做一个 15 秒 App 宣传片", "scaffold a SaaS hero animation", "motion design for X", or any product that needs a stylized synthetic UI demo. The 8 style files in `references/styles/` are motion-language anchors (pacing, easing, motion verbs, transitions, music mood) — they are NEVER the source of colors, typography, or photography mood; those come from the user's brand. For >15s the skill uses 2-3 take continuation. Do NOT use for: real filmed ads or TVC (use `promo-video`); personal multi-scene vlogs (use `vlog`); static HTML pages (use `visual-page`); narration-heavy explainers; raw 3D scene generation.
---

# UI Motion

This skill produces single-take UI motion graphics that look like **the brand**, not like a stock template. The architecture has three load-bearing ideas:

1. **Brand is the source of truth.** Colors, typography, photography mood, end-card mark all come from the user's brand assets. The 8 style files contribute motion language only.
2. **One continuous take.** A single 15s `gen_videos` (i2v) call produces the whole video. The model handles the natural morphing between 5 beats (cold open → reveal → interaction → wow → end card). No hard cuts, no ffmpeg transitions. For >15s the skill uses continuation: extract last frame of take N, use it as first frame of take N+1.
3. **Brand assets can appear in the video.** The user's real logo, product screenshots, and photography can be used as the i2v first frame (or as end-card compositing material), so the video shows their actual product, not an abstract metaphor.

## Inputs to collect

Ask the user in this order. Items 1–3 are **required**; 4–7 unlock a better output.

1. **Product / concept** — what the video is for.
2. **Brand visual** — at least one of:
   - Brand images (1–3 files): logo, product screenshot, marketing banner, brand guideline
   - Text description (2–5 sentences): the user's own words about the brand
   - Both is best. If the user has neither, ask once more, then default to a generic palette and call it out in the chat reply.
3. **Brand text** — product name, tagline, store badges. English by default; ask if the user wants something else.
4. **"What good looks like" reference** (optional) — a reference video the user admires. The original `ui动画.zip` upload is a perfect example. This informs motion language (pacing, easing, music mood) without touching brand identity.
5. **Aspect ratio** — `9:16` (Reels/Shorts/小红书/抖音) or `16:9` (B站/YouTube). Default `9:16`.
6. **Length** — `6s`, `10s`, `15s` (default), or `30s+` (uses multi-take continuation). The model natively supports 6s / 10s / 15s in one take.
7. **Music mood** — `cinematic`, `lofi`, `electronic`, `ambient`, `corporate`, or freeform. Default: derived from the brand profile.

If the user provides everything except the brand visual, **do not proceed with a stock template**. Push back once: *"I need at least one brand image or a 2-sentence brand description to make this look like you, not like a stock reel."*

## Procedure

### 1. Lock the brief

Write a 1-paragraph brief to `<workspace>/ui-motion/brief.md` capturing: product/concept, the brand visual sources (file paths or quoted text), brand text, optional reference video, aspect ratio, length.

### 2. Extract the brand profile (REQUIRED)

This is the heart of the skill. The brand profile is a structured JSON capturing the brand's visual DNA in model-actionable form. See `references/brand-analysis.md` for the full procedure.

Steps:

1. For each brand image, `read` it (the model can see images). Extract:
   - Background base (light / dark / gradient / photographic)
   - Dominant colors (3–5 with descriptive names + hex)
   - Typography feel (geometric / humanist / serif, weight, tracking)
   - Photography mood (lifestyle, abstract, technical, warm, clinical)
   - Visual density (spacious / balanced / dense)
   - Motion hints from composition
2. For any text description, parse mood words into the same fields.
3. Resolve conflicts (images win over text; logos win over marketing banners for color; ask the user once if unresolvable).
4. Write to `<workspace>/ui-motion/brand_profile.json`. Schema in `brand-analysis.md`.

Do not skip this step even if the user only provided one image. One image is enough.

### 3. Lock inspiration (optional)

If the user provided a "what good looks like" reference, analyze it for pacing, easing, transition vocabulary, music mood. Write to `<workspace>/ui-motion/inspiration_profile.json`. The 8 style files are pre-built inspiration profiles — if the user's reference matches one, adopt that style's profile directly (see `style-matching.md`).

If the user did not provide a reference, derive the inspiration profile from the brand profile alone: warm/wellness brands → slow + spring; energetic brands → fast + snap; corporate/SaaS → medium + smooth-ease.

### 4. Choose a style anchor (optional)

The 8 style files are reference points for motion language. They contribute: motion rhythm, easing, transition vocabulary, music mood template, geometry vocabulary. They do **NOT** contribute colors, typography, or photography mood — those come from the brand profile.

Procedure:

1. If the user named a style, anchor to it.
2. Otherwise, score each of the 8 against the brand profile. See `style-matching.md`.
3. If a strong match (>70%): suggest, ask once, anchor.
4. If no match or all weak: do **not** anchor to any style. Derive a custom style from the brand + inspiration profiles (see `custom-style.md`).
5. Record in `<workspace>/ui-motion/style_anchor.json` with `anchor: "A" | "B" | … | "H" | "custom"`. If custom, include a `custom_spec` block.

### 5. Build the storyboard

The storyboard for a single-take video is small: **1 first_frame_prompt + 1 motion_prompt**. The motion_prompt describes the full 15s in 2–4 sentences, walking through the 5 beats (cold open → reveal → interaction → wow → end card) using the brand's color names and the style anchor's motion verbs.

For >15s, the storyboard has 2+ takes. Each take has its own first_frame_prompt + motion_prompt. Take N+1's first frame is the last frame of take N (continuation). See `references/storyboard-schema.md` for the full schema.

Both prompts must be derived from the **brand profile first**, with the style anchor's motion language applied second. Specifically:

- Colors in the prompts come from `brand_profile.colors` (descriptive names, not hex).
- Typography keywords come from `brand_profile.typography`.
- Motion verbs come from the style anchor's motion signature (or the custom spec).
- The end card uses the real brand mark from the user's logo, in the brand's font and color.

Write the result to `<workspace>/ui-motion/storyboard.json`. Schema v4.

### 6. Generate the first frame

For a single take:

- If the user provided a brand asset for the first frame, use it (resize to target aspect ratio with ffmpeg/sips, save as `frames/first_frame.png`).
- Otherwise, call `image_synthesize` with `first_frame_prompt`. Save to `frames/first_frame.png`.

For multi-take (>15s): each take that has `first_frame_source: "brand_asset"` uses the user's asset; `first_frame_source: "continued"` uses the previous take's last frame; `first_frame_source: "generated"` uses `image_synthesize`.

### 7. Generate the video (i2v)

Call `gen_videos` with the first frame as `input_image_path` and `motion_prompt`. Set `duration` to `6`, `10`, or `15` based on the user's length request. Set `reference_type: "first_frame"`. Save to `clips/take-1.mp4`.

For multi-take: generate each take in sequence. After each take, extract the last frame with ffmpeg (`ffmpeg -sseof -0.1 -i clips/take-N.mp4 -frames:v 1 -q:v 2 frames/take-N-last.png`). The next take uses that last frame as its first frame.

### 8. Generate the music

Call `batch_text_to_music` once. The prompt is a hybrid: rhythm and tempo from the style anchor (or custom spec), mood and instrumentation from the brand profile. Length matches the video. Save to `audio/bg.mp3`.

### 9. Mux (and concat if multi-take)

For single take:

```bash
ffmpeg -i clips/take-1.mp4 -i audio/bg.mp3 \
       -map 0:v:0 -map 1:a:0 \
       -c:v copy -c:a aac -b:a 128k -t <total_duration_sec> \
       -movflags +faststart \
       final.mp4
```

Use the requested video length as the explicit `-t` value. Do not use
`-shortest`: with concat-filtered video or generated BGM, it can stop the
audio stream early even when the source music is long enough. The default
audio contract is BGM (plus optional VO via `--vo`); generated clip audio is
not carried into the final mix unless the user explicitly asks for it.

For multi-take, the bundled `scripts/stitch.mjs` handles concat + mux in one call:

```bash
node .opencode-v2/skills/ui-motion/scripts/stitch.mjs \
  --manifest storyboard.json \
  --out final.mp4
```

If `ffmpeg` is missing, deliver the raw clips + the brand_profile.json + a clear note that assembly needs ffmpeg.

### 10. Deliver and verify brand consistency

Send `final.mp4` to the user with `<deliver-assets>`. Run through `references/qa-checklist.md` with **brand consistency as the top check**:

- Are the rendered colors from the brand profile (not the style anchor's defaults)?
- Is the real brand mark in the end card, or did the model fall back to a generic glyph?
- Any stray colors that don't appear in the brand palette?

Mention any brand-consistency flag in the chat reply. Don't ship a video that doesn't look like the brand.

The chat reply follows this structure:

1. **Creative interpretation** (2–3 sentences). What you extracted from the brand and how it shaped the design. Quote one or two specific brand signals you leaned on.
2. **What the viewer sees** (1 sentence per beat, 5 total).
3. **Brand-consistency flags + next steps** (1–2 sentences).

## Output contract

- One file: `<workspace>/ui-motion/final.mp4`, H.264, AAC, 9:16 or 16:9, 15s (or requested length).
- Process artifacts: `brief.md`, `brand_profile.json`, `inspiration_profile.json` (if used), `style_anchor.json`, `storyboard.json`, intermediate `frames/` and `clips/`, `audio/bg.mp3`.
- Chat reply contains the final asset + the 3-paragraph summary.

## Failure handling

- **No brand visual at all** (no image, no text) → ask once. If the user still can't provide, push back: *"I can produce a generic Style X video, but it won't look like your brand. Confirm you want generic, or send me a logo / screenshot / 2-sentence description."*
- **`read` of a brand image fails** → fall back to the text description. If both fail, see previous bullet.
- **Brand colors and style anchor colors conflict** → brand wins. Always.
- **`image_synthesize` rejects a prompt** (safety / content) → soften (drop brand text, keep composition), regenerate only that frame.
- **`gen_videos` rejects 15s** (in case the model in the user's region caps at 10s) → fall back to 2-拍 continuation (10s + 6s) automatically. The skill's `stitch.mjs` supports both schemas.
- **Multi-take join has visible drift** → regenerate take 2 with a tighter "from this frame, fade to background and reveal end card" prompt. If still drifting, shorten take 1 to end on a more static moment.
- **Final audio ends before the video** → remove `-shortest`, set `-t` to the requested total duration, and verify both stream durations with `ffprobe`.
- **Stitch fails on missing ffmpeg** → ship the raw clips + brand_profile.json.
- **The user wants > 15s** → multi-take continuation. See `long-form.md`.
- **The brand doesn't match any style** → use the custom path. Don't force a fit.

## Windows (win32) platform notes

Replace the `node .opencode-v2/.../stitch.mjs` call with `node ".opencode-v2\\skills\\ui-motion\\scripts\\stitch.mjs"`. The script is pure Node.js. Install ffmpeg via `winget install Gyan.FFmpeg` or `choco install ffmpeg`. `image_synthesize`, `gen_videos`, `batch_text_to_music`, `read` are Mavis tools and unchanged.

## Examples

**Input**: "帮我做一个 15 秒的 UI 动效视频，产品叫 Notely，是个 AI 笔记 App"

→ No brand visual. Push back once for logo + screenshot. If provided, extract brand profile (e.g. warm cream + coral accent + Fraunces serif + spacious density + slow motion). Storyboard: 1 first frame + 1 motion prompt. Single i2v call for 15s. End card uses real Notely logo in Fraunses on warm cream.

**Input**: "15s video for AURA smart home app, here's my logo and the app icon"

→ Brand intake: 2 images. Brand extraction: warm cream + orange + green + soft photography. Style anchor: custom (the brand is its own thing). Storyboard: single 15s take, motion prompt describes 5 beats using AURA's cream/orange/green. End card: real AURA logo.

**Input**: "15s Vision Pro style, here's my logo"

→ Brand intake: 1 image. Style anchor: G (user named "Vision Pro style"). Storyboard: 15s single take using style G's motion language (concrete gallery, hand gestures) but with the brand's color instead of G's default violet. End card: real logo in brand color.

**Input**: "我想要 30s 的"

→ Multi-take: 2 takes of 15s + 15s with continuation. Stitch handles concat. Or 10+10+10 with two joins. See `long-form.md`.
