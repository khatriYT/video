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

## 2026-11-27

**Character passes and shot review**
- Character passes done: EMERGE_PIP_WAVE, HIB_ENTER, AGAVE_BAT_CU, HIB_FUNGUS_CU (held frame), FARM_MOTHS. CORN_NET is part-done and resumes.
- Each finished shot is composited and checked as soon as its pass lands. A contact sheet of the 37 scenes composited so far was reviewed.

**Issues found and fixed (details in `08_Scenes/LOOKDEV_REVIEW.md`, R1–R14)**
- **Corn and cotton fields were broken.** Geometry-Nodes instancing scattered each plant's parts separately: bare stalks, floating tassels, leaf clumps with no stalk, and corn ears or cotton bolls lying on the soil.
  - Fixed by putting multi-part plants in child collections, so whole plants are instanced.
  - Added crop-free corridors along low cameras' sight lines and around placed actors.
  - All 13 farm plates are queued for re-render. Character passes are unaffected: vegetation is not rendered in them; occlusion comes from the plate depth.
- **Moon chapter backgrounds were a flat disc on a gradient.** Now: a textured moon (maria), moonlit cloud wisps, a ridge with gnarled bare trees, and three bats scripted to cross the moon.
- **Farm moths read as glowing pairs of dots.** Redrawn as depth-layered insects with flapping wings and trails. The porch moths now circle the porch lamp.
- **Agave close-up: the nectar bat was nearly black and half out of frame.** Fixed in compositing with a luminance lift, a moonlight rim and a reframing move toward the bat.
- **Cave exit (HIB_SNOW_EXIT) was a blown-out emissive placeholder.** Replaced with a lit winter exterior: snowfield, bare trees, drifts and an overcast sky.

**Interruptions**
- The container rebooted once. Queues were restarted from claim directories. Finished frames were all checked as valid PNGs; nothing was lost.
- Two parallel test renders were killed for lack of memory: a farm plate with full corn needs about 5 GB. Farm plates now run one at a time.
