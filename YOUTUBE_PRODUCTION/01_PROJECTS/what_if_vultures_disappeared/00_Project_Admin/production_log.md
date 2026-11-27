# Production Log: What If Every Vulture Disappeared?

## 2026-11-26
- Project created with tools/new_project.py
- Research: 20 sources, 24 claims (web searches 2026-11-26); several claims corrected (see decisions log)
- Narration: Kokoro v1.0 am_michael, 74 scenes, 531.7 s
- Blender look-dev: fixed metaball capsule sizing (absolute half-length), sky/haze compositing (Env pass + mist on geometry only), vulture proportions, beak, fallen pose; point lights were placed at the origin (bug) - fixed, P07/P18 re-rendered
- Renders: 26 stills at 2304x1296 (13-60 s each), A01 68 f, A02 108 f, A03 94 f at 1600x900
- Cards: 24 designs; layout fixes (tag position, compare legend, bans stamp, poison layout)
- v2 (2026-11-26): rigs.py, envs2.py, render3.py, compose3.py.
  - Plates: 27 at 2304×1296 / 16 samples, about 90 s each.
  - Character passes: 45 scenes, about 4,000 frames at 12 fps, 4–7 s per frame; 3–6 parallel workers with a claim-based queue.
  - Full-3D orbit (SC071): 108 frames.
- v2 fixes:
  - Portrait and head framing re-rendered: the head was under the chapter card.
  - Soaring shot re-pathed: the bird had left the frame.
  - SC073 switched from full-3D to layered for render time.
  - SC065 was missed in the first v2 pass and was added.
