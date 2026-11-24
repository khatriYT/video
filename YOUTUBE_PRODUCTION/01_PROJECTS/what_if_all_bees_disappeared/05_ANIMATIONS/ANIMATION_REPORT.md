# Animation Report: Episode 2 (Bees)

## Method
The same pipeline as episode 1, with two additions: richer scenes and an **animated text layer**.

- Every scene is a function of time. Characters, creatures, props and the camera move, with blinks, the 8-fps line-boil effect and eased push/pan camera moves.
- `tools/kinetic.py` draws each scene's `onscreen` cue from the storyboard on top of the animation, outside the line-boil effect so it stays sharp. The styles:
  - **count:** numbers roll up, e.g. 0 → 20,000, 0 → 87 OF 115, 0 → 2.7 MILLION
  - **pop:** words pop in one by one with an overshoot and a slight wobble
  - **type:** typewriter with a blinking cursor (the fake Einstein quote)
  - **stamp:** slams in with a shake (FAKE QUOTE, EMPTY, EU BAN · 2018)
  - **label:** caption card slides in (place names, species names)
  - **list:** checklist items appear one by one
  - **marker:** highlighter swipe behind the text
  - **title:** the two-line episode title
- Rendering: headless Chromium, then FFmpeg (H.264 CRF 18, 1920×1080, 24 fps, static paper grain). Four parallel workers took about 35 minutes.
- **Clip length** = narration + 0.85 s (minimum 2.0 s). The extra breathing room gives the animated text time to read and brings the episode to 12 minutes.

## Verification
| Item | Value |
|---|---|
| Clips | 105 / 105 |
| Frames | 17,337 |
| Total | 722.38 s |
| ffprobe | Every clip 1920×1080, 24/1, duration within 0.06 s of target. **0 failures.** |
| Visual check | Frames sampled every 60 s from the final video; all 105 keyframe stills reviewed |
