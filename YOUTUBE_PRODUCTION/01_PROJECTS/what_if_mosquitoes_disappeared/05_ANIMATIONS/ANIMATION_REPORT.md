# Animation Report: all 98 scenes (v2)

## Method
The animation is programmatic 2D:

- Every scene is a function of time. It moves joints, creatures, props and the camera, and adds blinks, line boil (3 drawings alternating at 8 fps) and eased camera pushes and pans.
- Each frame is rendered by headless Chromium and encoded by FFmpeg: H.264 CRF 18, yuv420p, 1920×1080, 24 fps, with static paper grain.
- **Clip length** = narration length + 0.7 s (minimum 2.0 s). The breathing room went up from 0.55 s in v1 to give the longer episode a calmer pace.

## Results
| Item | Value |
|---|---|
| Clips | 98 / 98: `scene_###/scene_###.mp4` |
| Frames | 17,440 |
| Total duration | 726.67 s (12:06.7) |
| Verification | ffprobe on every clip: 1920×1080, 24/1 fps, duration within 0.06 s of the target. **0 failures.** |
| Visual check | Frames sampled every 60 s from the assembled video; clips 001–010 also checked at 10%, 50% and 90% |
| Render time | About 25 min, 4 parallel Chromium workers at about 0.37 s per frame |

## Typical motion vocabulary
- **Characters:** blink, breathing bob, arm raises, shrugs, nods, pointing, thumbs-up, hat drop with bounce and squash, walking bob.
- **Creatures:** wing flutter, figure-8 hover, swarm drift, fish tail swim and gulp, larva wriggle, pupa tumble, bat flap, caribou walk and graze.
- **Info-graphics:**
  - bars that grow or shrink
  - icons that pop in
  - heat-map pulse, glow spreading across a family tree or map, calendar flips
  - stamps that slam down with an overshoot ease
- **Camera:** 4–15% push-ins and pull-outs, slow pans, one tilt down below a water line (scene 032).

## Issues and fixes
- A batch-list bug in the shell loop skipped one of the four render batches. It was detected because the clip count was 73 of 98, and the 25 missing clips were re-rendered.
- Earlier performance and size fixes from v1 still apply: grain is done in FFmpeg, and static grain keeps file size down.
