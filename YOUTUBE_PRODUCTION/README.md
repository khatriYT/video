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
- **Tools:** `tools/`, the Python pipeline. Commands are in `00_SYSTEM/SYSTEM_CONFIG.json`.

## Current project
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
