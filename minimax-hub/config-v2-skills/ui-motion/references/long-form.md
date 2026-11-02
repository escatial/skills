# Long-form (30s+) extensions

The base skill is locked at 15s single take. Anything longer uses **multi-take continuation**: generate take 1 (15s), extract its last frame, use that frame as take 2's first frame, generate take 2 (15s), and so on. The joins are seamless because the i2v model is told "continue from this frame".

The brand-first architecture makes long-form easier: the brand profile + style anchor stay the same. Only the storyboard structure changes (from `narrative` to `takes`).

## 30s structure (2 takes × 15s)

```
Take 1 (15s)
┌────────────────────────────────────┐
│ cold open + reveal + interaction   │  ← beats 1-3
│ + first half of wow beat           │
│ [last frame: a static moment]      │  ← chosen for minimal drift
└────────────────────────────────────┘
                ↓ extract last frame
Take 2 (15s)
┌────────────────────────────────────┐
│ continuation + end card reveal     │  ← beats 4-5
│ [last frame: end card holding]     │
└────────────────────────────────────┘
                ↓
        concat (seamless)
        mux with 30s BGM using an explicit `-t 30` duration (never `-shortest`)
```

The seam is invisible when take 1 ends on a **static moment** (held pose, ribbon fully spread, glyph at rest). The i2v model continues from that frame with minimal drift.

## 60s structure (3 takes × 15s + 1 take × 15s, or 4 takes × 15s)

For 60s, use 4 takes of 15s with 3 seams. Apply the static-end rule at every seam. The motion_prompt for each take is the 15s narrative for its portion of the story.

For 30s stories that work:

- **Tutorial**: show 3 features sequentially, each with a real product asset
- **Comparison**: split-screen "before / after" using two half-frame panels, both in the brand colors
- **Documentary**: layer a narrator voice over the visuals (see Voice-over below)

## Voice-over

If the user wants narration, add this to the storyboard:

```json
{
  "voice": {
    "voice_id": "male-qn-qingse",
    "text": "Notely captures your thoughts, organizes them in motion, and gets out of the way.",
    "file": "audio/vo.mp3"
  }
}
```

The `stitch.mjs` script supports a `--vo` flag that mixes VO at 0 dB and BGM at -18 dB under it.

## Music length

For 30s, use `format: wav` and ask for 30s in the `batch_text_to_music` prompt explicitly. For 60s, batch two 30s calls and crossfade in the stitch.

The music prompt should still be derived from the brand profile. A 30s piece has more time to develop — the same brand mood but with longer phrasing, more harmonic movement.

## Brand profile stability across long-form

The brand profile is the *constant* across a 30s or 60s video. You don't re-extract the brand profile per take — the same `brand_profile.json` drives all of them. The brand's color names, typography, photography mood are stable inputs.

## Avoiding drift at the seams

Three rules to keep the multi-take continuation seamless:

1. **End take N on a static moment** — held pose, fully-spread ribbon, glyph at rest. The model has nothing to "continue" if the frame is dynamic, so it invents motion that doesn't match.
2. **Keep the motion_prompt for take N+1 focused on the local beat** — "from this static frame, fade to background and reveal the end card" — not a recap of what came before.
3. **If drift appears, regenerate take N+1 only** — take N is fine. Don't re-roll the whole video.

## Schema extension

The base `storyboard.json` already supports the long-form case via the optional `takes` array. The version stays at `4`. The brand fields are unchanged.
