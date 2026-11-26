# YOUTUBE_PRODUCTION: "The Disappearance Files" pipeline

A reusable pipeline that takes a video from research to a finished export:

research → script → storyboard → images → animation → voice → mix → export

for animated "What if X disappeared?" science videos.

- **System docs:** `00_SYSTEM/`
  - competitor research
  - visual style guide
  - scriptwriting framework
  - topic ideas
  - config
- **Projects:** `01_PROJECTS/<project>/`, one folder per video, using the standard 01–10 subfolders.
- **Shared assets:** `02_SHARED_ASSETS/`, holding the character sheets and background plates.
- **Reference library:** `03_REFERENCE_LIBRARY/<channel>/`, holding competitor research and deep reference-video analysis.
  - Hardy Humans, 2026-11-26: start with `HardyHumans/02_Reference_Analysis/report.md`.
  - Competitor images are gitignored because the repo is public. `tools/fetch_reference_frames.py` rebuilds them.
- **Tools:** `tools/`, the Python pipeline. Commands are in `00_SYSTEM/SYSTEM_CONFIG.json`.

## Start of every session
Read these first:
1. `00_SYSTEM/production_tracker.md`
2. `00_SYSTEM/decisions_log.md`
3. `00_SYSTEM/SYSTEM_CONFIG.json`

Then check `00_SYSTEM/CAPABILITY_REPORT.md`: the cloud container is ephemeral, so Blender and the pip tools may need reinstalling.

## Episode 3 onward (master-prompt workflow)
- **Topic shortlist:** `00_SYSTEM/TOPIC_SHORTLIST_EP3.md` (waiting for your choice).
- **Proposed hybrid-3D house style:** `00_SYSTEM/STYLE_BIBLE_v2_DRAFT.md` (waiting for your approval).
- **New project:** `python3 tools/new_project.py <slug> "<Working Title>"` creates the `00_Project_Admin … 14_Delivery` layout.
- **Blender check:** `blender -b --factory-startup -P tools/blender_benchmark.py -- EEVEE out.png 32`

## Projects
- Episode 1: `01_PROJECTS/what_if_mosquitoes_disappeared/` (12:06)
- Episode 2: `01_PROJECTS/what_if_all_bees_disappeared/` (12:02), with more detailed backgrounds and animated on-screen text

## Episode 1 notes
`01_PROJECTS/what_if_mosquitoes_disappeared/`. The full 12-minute episode is in `07_FINAL_VIDEO/`. See `PROJECT_STATUS.md` there.

## New video in 6 steps
1. Copy the project folder layout. Write `tools/storyboard_data.py` for the new topic (sections plus scenes), after research.
2. `python3 tools/build_docs.py 01_PROJECTS/<p>` builds the script and storyboard documents.
3. `python3 tools/tts.py 01_PROJECTS/<p> <kokoro_dir>` records narration for every scene.
4. Write the scene functions in `tools/scenes_<topic>.py`. Then run:
   - `python3 tools/render.py 01_PROJECTS/<p> still` and inspect the stills
   - `python3 tools/render.py 01_PROJECTS/<p> anim`
5. `python3 tools/make_audio_assets.py 01_PROJECTS/<p>` makes the music and SFX.
6. `python3 tools/assemble.py 01_PROJECTS/<p> 1 N <name>` builds the final video and the editing project.

`render.py` currently imports `scenes_mosquito`. Point it at the new scenes module for a new topic.

## Episode 2 commands (multi-project tools)
```
python3 tools/build_docs.py 01_PROJECTS/what_if_all_bees_disappeared storyboard_bees
python3 tools/tts.py 01_PROJECTS/what_if_all_bees_disappeared <kokoro_dir>
python3 tools/render.py 01_PROJECTS/what_if_all_bees_disappeared still --scenes=scenes_bees --pad=0.85
python3 tools/render.py 01_PROJECTS/what_if_all_bees_disappeared anim  --scenes=scenes_bees --pad=0.85   # split ids across processes
python3 tools/make_audio_bees.py 01_PROJECTS/what_if_all_bees_disappeared
python3 tools/assemble.py 01_PROJECTS/what_if_all_bees_disappeared 1 105 what_if_all_bees_disappeared_full --sfx=sfx_bees
python3 tools/render_thumbnail_bees.py 01_PROJECTS/what_if_all_bees_disappeared
```
In the storyboard, an optional 9th field per scene (`"style|position|main|sub"`) adds animated on-screen text, which `tools/kinetic.py` renders automatically.
