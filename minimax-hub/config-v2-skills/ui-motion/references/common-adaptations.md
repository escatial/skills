# Common adaptation requests

The primary knob in this skill is the **brand profile** (in `brand_profile.json`), not the style anchor. Most user pushes can be addressed by editing the brand profile and re-running the relevant pipeline step. The style anchor and storyboard are downstream of the brand.

## "Make it more on-brand"

Don't touch the style anchor. Re-extract the brand profile from the user's images and text (Phase 2), and look for things you missed:

- Did you pick the right primary? Verify by sampling the most-saturated color in the brand's hero image
- Did you capture the typography mood correctly? "Humanist sans" vs "geometric sans" is the most common brand-drift cause
- Did you miss an accent color? Many brands have 2–3 accents, not just one
- Did you get the background right? Dark with warm undertone vs pure black vs gradient reads very differently

Once the brand profile is corrected, regenerate the storyboard and the i2v call. Most drift comes from a stale brand profile.

## "Make it more product-y"

User wants to see real UI, not abstract metaphors. Two options:

1. **Soft version** — keep the abstract style, but make the metaphor more concrete. A "thought captured" card becomes a card with a tiny UI hint (a button, a text line) in the corner.
2. **Hard version** — the user uploads a brand asset (product screenshot). The skill uses it as `brand_assets.first_frame`, the actual product UI appears at the start of the video.

The hard version is the right answer for most B2B and SaaS brands. Push the user to upload a screenshot.

## "Different brand"

Just edit `brand_profile.json`. The storyboard, frame prompt, motion prompt, music prompt — all are derived from the brand profile. Regenerate storyboard → first frame → video → music → mux. The style anchor stays the same (motion language), the brand changes (visual identity).

This is the single most useful property of the brand-first architecture: you can produce 10 videos in 10 different brand palettes using the same motion language by editing one file.

## "Shorter, 6s"

Single 6s take. The motion_prompt is shortened to fit 6s — typically just 2–3 beats instead of 5 (cold open → reveal → end card, or just reveal → end card). Edit `total_duration_sec` to 6, regenerate the storyboard, regenerate the i2v call (with `duration: 6`).

## "Different motion language"

Change `style_anchor.anchor` in `style_anchor.json`. The brand profile stays. Re-derive the storyboard's motion_prompt from the new style's motion verbs and easing vocabulary. Regenerate video + music.

If the user wants a motion language that doesn't match any of the 8 templates, set `style_anchor.anchor: "custom"` and write a `custom_spec` block. See `custom-style.md`.

## "Add a real voiceover"

Add a `voice` field to the storyboard:

```json
{
  "voice": {
    "voice_id": "male-qn-qingse",
    "text": "Notely captures your thoughts, organizes them in motion, and gets out of the way.",
    "file": "audio/vo.mp3"
  }
}
```

Call `synthesize_speech` to produce the VO. The `stitch.mjs` script supports a `--vo` flag that mixes VO at 0 dB and BGM at -18 dB under it.

When the VO references the brand, use the brand name and the brand's tagline — never a generic "your product".

## "Make it 30s / 60s"

Multi-take continuation. See `long-form.md`. The brand-first architecture makes this easy: 30s just means more time to show the brand in different contexts. The brand profile + style anchor stay the same; the storyboard gets a `takes` array.

## "Different aspect ratio, same content"

Change `aspect_ratio` in the storyboard. Then:

- `image_synthesize` re-renders the first frame at the new aspect ratio
- `gen_videos` re-renders the video at the new aspect ratio
- The motion_prompt text is unchanged
- Brand assets (if any) are re-resized to the new aspect ratio

For 1:1 (Instagram square), drop the "vertical scene" wording from the prompts. For 21:9 (cinematic), extend the end card hold and shorten the interaction beat.

## "The video doesn't look like my brand"

This is the most common complaint and the most important to address. Walk through the brand consistency checklist in `qa-checklist.md`:

1. Are the brand colors actually in the rendered frames? Sample 5 frames and check.
2. Is the real brand mark in the end card, or did the model fall back to a generic glyph?
3. Are the motion_prompts using the brand's color *names* ("warm coral") not the style's hardcoded names ("cyan")?
4. Did the model invent a "creative interpretation" that drifted from the brand?

If any of these failed, regenerate the affected content with explicit brand language in the prompts. Don't ship a video that doesn't look like the brand.
