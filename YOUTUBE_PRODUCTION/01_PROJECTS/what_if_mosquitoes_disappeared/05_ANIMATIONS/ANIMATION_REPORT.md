# Animation Report: scenes 001–010

## Method
No AI image-to-video service is configured. Clips are made with **programmatic 2D animation**:

1. Each scene function in `tools/scenes_mosquito.py` is evaluated at every frame time (24 fps). It moves joints, creatures, props and the camera.
2. Headless Chromium renders the frame.
3. FFmpeg encodes the frames as H.264 (CRF 18, yuv420p, 1920×1080, 24 fps) with a static paper-grain noise.
4. A hand-drawn **line boil** (SVG turbulence displacement, 3 drawings alternating at 8 fps) is applied to every frame.

**Clip length** = narration length + 0.55 s (minimum 2.0 s). Clips are therefore cut to the real voice-over, not to estimates.

## Clips
| Scene | File | Duration | Frames | Motion |
|---|---|---|---|---|
| 001 | `scene_001/scene_001.mp4` | 4.83 s | 116 | Clock hand ticks to 12; mosquito hovers in a figure-8, then drops dead (X-eyes) onto the blanket; "z"s float; push-in 6% |
| 002 | `scene_002/scene_002.mp4` | 7.38 s | 177 | 170 tiny mosquitoes around the globe vanish in a left-to-right wave (fall and fade); stars twinkle; pull-out 8% |
| 003 | `scene_003/scene_003.mp4` | 3.25 s | 78 | Mosquito buzzes by Pip's ear with vibrating buzz lines; puff; face goes from annoyed to a happy smile |
| 004 | `scene_004/scene_004.mp4` | 2.13 s | 51 | Pip scratches the bitten arm; bumps shrink and fade; sparkle |
| 005 | `scene_005/scene_005.mp4` | 2.00 s | 48 | Bed net rises out of frame; dawn light brightens; parent and child smile |
| 006 | `scene_006/scene_006.mp4` | 2.04 s | 49 | Arm swings up into a thumbs-up (overshoot ease); sparkles; body bob; blink |
| 007 | `scene_007/scene_007.mp4` | 8.25 s | 198 | Scientist A shrugs and returns; blinks; jar mosquito hovers; slow pan right |
| 008 | `scene_008/scene_008.mp4` | 2.17 s | 52 | Scientist B raises a magnifier to the jar and frowns; slow pan |
| 009 | `scene_009/scene_009.mp4` | 2.00 s | 48 | Bucket hat drops onto Pip's head with a bounce and squash; expression goes from "o" to a grin |
| 010 | `scene_010/scene_010.mp4` | 5.13 s | 123 | Title pops in (back-ease); reeds sway; water shimmers; sun rises; pull-out 8% |

**Verified with ffprobe:** all 10 files exist, are 1920×1080 at 24 fps, and frame counts match. Frames at 10%, 50% and 90% of each clip were inspected visually and the motion matches the storyboard.

## Issues found and fixed
- The first render took about 3 s per frame because the grain SVG filter was computed live. Grain moved to FFmpeg, bringing it to about 0.3 s per frame.
- Temporal grain inflated the final file to 178 MB for 39 s. Switching to static grain brought it to 23 MB.
- The first scene_001 render was interrupted. It was deleted and re-rendered.

## Not yet animated
Scenes 011–068. Each has an animation prompt in `../03_STORYBOARD/STORYBOARD.md`.
