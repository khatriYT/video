# Motion Notes: Hardy Humans (wqMaepNXeBc)

> **Status: motion was NOT observed.**
>
> - YouTube refused the media stream to this cloud server, and further download workarounds were not attempted.
> - Only still storyboard samples were available: one every 9.92 s.
> - Everything below is **[INFERRED]** from consecutive stills unless tagged [VERIFIED].
> - Replace this file once the video is supplied.

## 1. What the stills do tell us

| Evidence | What it implies |
|---|---|
| The same plate appears in 2–3 consecutive samples (10–30 s) with the character in a slightly different pose or position. Examples: rooftop 02:18–02:38, stairs 35:52–36:52 [VERIFIED] | Long holds on one plate. Motion probably comes from slow camera push-ins or pans over the still plate plus small character puppet moves [INFERRED] |
| A caption word in 69% of samples [VERIFIED], one word at a time | Word-by-word kinetic captions synced to the narration. That suggests auto-timed subtitles at about 2–3 words per second [INFERRED] |
| "DAY 12" title text half-faded over the plate at 05:07 [VERIFIED] | Title cards **dissolve out** over the plate rather than hard-cutting [INFERRED] |
| Smoke columns, fire, steam, snow and rain in many plates [VERIFIED] | Probably animated overlays (particles, looping smoke) on still plates [INFERRED] |
| Characters drawn as flat vector puppets [VERIFIED] | Cut-out (puppet) animation: head tilt, arm wave, blink, walk cycles for small figures [INFERRED] |
| "Graphic over blurred plate" frames [VERIFIED] | Graphics probably pop or scale in over the blurred plate, then cut back to the sharp plate [INFERRED] |
| 44 chapters averaging 51 s, and a different frame type in nearly every 10 s sample | Average **shot length is probably ≤ 5–6 s**. A rough estimate: 225 samples changed setup about 190 times. That puts the cut count at **at least 190 visible changes**, so the true number is higher [INFERRED] |

## 2. Questions to answer when the video is available

1. Average and median shot length per act. Use FFmpeg scene detection: `select='gt(scene,0.3)'`.
2. Camera moves: are the plates static, pushed in by 2–10%, panned, or given 2.5D parallax (separated layers)?
3. Character animation depth: blink and mouth flaps only, or full limb and walk cycles?
4. Transitions: hard cut, dissolve, whip, match cut? How are chapter and day transitions handled?
5. How captions are timed and styled in motion (pop, scale, colour flash on key words?).
6. The narrator's voice (human or TTS), pace (words per minute), music genre and level, SFX density.
7. Whether chapter starts reuse a sound motif, such as a "day stamp" hit.

## 3. Motion guidance for our production (independent of the reference)

These carry over from our existing house rules (`00_SYSTEM/COMPETITOR_VISUAL_STYLE_GUIDE.md`, B.7), adjusted for the hybrid 3D plan:
- **Camera:** one eased move per shot: a push-in of up to 8% scale, a slow pan, or a short Blender camera dolly on hero shots. Ease in and out over about 0.5 s.
- **Characters and creatures:**
  - Clear start and end poses.
  - Anticipation before big moves.
  - Settle at the end.
  - Loop secondary motion: breathing, antenna twitch, wing flutter.
- **Environment life:**
  - Grass and leaf sway.
  - Drifting particles: pollen, snow, dust.
  - Water shimmer, smoke loops.

  These are cheap ways to keep a still plate alive.
- **Shot length:** 3–7 s. Change setup at least every 6–8 s in the first 60 seconds.
