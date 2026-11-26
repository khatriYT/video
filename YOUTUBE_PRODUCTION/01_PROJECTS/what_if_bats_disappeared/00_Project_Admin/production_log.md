# Production Log: What If All Bats Disappeared?

## 2026-11-26

**Setup and research**
- Created the project with `tools/new_project.py`.
- Research: 25 sources (S01–S25) and 37 claims (C01–C37), each checked against a primary abstract or reputable secondary reporting.
- Script: 66 scenes, 1,277 words. Kokoro narration lasts 492.5 s; the cut runs 558.5 s (9:18).

**Look-dev**
- Pip v3, the farmer, and four bat species sculpted as SDFs and rigged.
- Look-dev iterations: 4 on Pip, 5 on the bats, 4 on environments (see `08_Scenes/LOOKDEV_REVIEW.md`).

**Rendering**
- Started three background queues on this CPU-only container:
  - plates: 2 workers;
  - character passes: 1 worker;
  - bat flight-cycle sprites.
- Plate review pass 1 found the eye-scale bug, the crude agave flowers and a dark durian plate. All fixed and re-queued.
