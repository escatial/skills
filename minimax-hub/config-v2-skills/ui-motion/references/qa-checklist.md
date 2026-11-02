# Pre-delivery QA Checklist

Run through this before sending `final.mp4` to the user. **Brand consistency is the top check** — every other check is secondary if the video doesn't look like the brand.

## Brand consistency (the top check)

- [ ] All colors in the rendered frames come from `brand_profile.colors` (or are derived shades — primary at 50% alpha, etc.). No stray cyan/magenta/violet glows if the brand is warm coral.
- [ ] The end card uses the real brand mark from `brand_assets.end_card` (or the user's uploaded logo), not a generic glyph. The model must NOT fall back to a sparkle ✦, music note, or any signature glyph from a style template.
- [ ] The end card wordmark is in the brand's typography (or a reasonable fallback). Sans brand on a serif brand is a bug.
- [ ] The motion_prompt uses the brand's color *names* ("warm coral", "deep navy") not the style anchor's hardcoded color names. Search the storyboard.json for any leftover "cyan", "magenta", "violet" from Style A — replace with the brand's actual accent names.
- [ ] If the user provided a brand asset, that asset is visibly in the rendered frame. Verify by watching the final video.
- [ ] Music prompt doesn't reference the style's default mood if the brand has its own. A warm brand shouldn't get the "industrial metallic hits" template from Style C.

## Spec

- [ ] Total runtime matches the requested length ±0.15s (e.g. 14.85–15.15s for a 15s ask)
- [ ] Resolution matches the declared aspect ratio: 1080×1920 for 9:16, 1920×1080 for 16:9
- [ ] 30 fps (H.264 + AAC both default to 30 fps)
- [ ] Pixel format `yuv420p` (universal playback, required by most social platforms)

## Visual

- [ ] No frame contains literal iOS / Android UI chrome (no system status bar, no app icons, no notification center)
- [ ] On-screen text budget: ≤ 6 words total across the whole video, except the end card which may have product name + tagline + store badges
- [ ] End card text legible at 100% on a phone screen
- [ ] No text on the first frame (it becomes the platform's poster image; text on it tanks completion rate on 抖音/小红书)

## Audio

- [ ] BGM peaks below -3 dBFS
- [ ] No clipping
- [ ] Total audio length matches video length ±0.1s
- [ ] Final mux uses an explicit `-t <total_duration_sec>`; do not use `-shortest`
- [ ] Verify both stream durations with `ffprobe` after muxing; the audio must not end before the video

## Multi-take continuation (>15s only)

- [ ] The join between take N and take N+1 has no visible jump. Watch the seam at 0.5x speed.
- [ ] If drift is visible, regenerate take N+1 with a "from this static frame, fade and reveal end card" prompt
- [ ] Audio is continuous across the join (no gap, no click)

## Platform-specific

- **抖音 / 小红书 (Reels/Shorts)**: poster image should be a clean freeze of the end card
- **YouTube / B站 (16:9)**: end card may include a Subscribe/Follow cue if the user is a creator
- **Twitter / X (in-feed video)**: autoplay is muted, so the first 2 seconds need to be visually punchy without audio

## File

- [ ] Filename ends in `.mp4`
- [ ] File size under 50 MB (raise ffmpeg `-crf` from 20 to 24 if over)
- [ ] `moov atom` at the start (ffmpeg's `-movflags +faststart` ensures this)

## If any check fails

**Brand consistency failure** is the most common and most visible. Don't ship a video that doesn't look like the brand. If the model drifted, regenerate the affected segment with a more explicit prompt that names the brand colors and the real brand mark.
