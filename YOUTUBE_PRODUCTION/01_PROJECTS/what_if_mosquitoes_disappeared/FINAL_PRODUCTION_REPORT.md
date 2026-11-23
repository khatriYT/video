# Final Production Report: "What Would Happen If All Mosquitoes Disappeared?"

**Version 2 (full episode).** Changes since v1 (the 39 s preview of scenes 001–010), all requested by the user:

- **Length:** the script grew from 1,049 to 1,687 words with five new researched sections:
  - How a mosquito finds you
  - An ancient survivor
  - The night shift (predators and the bat myth)
  - We've tried this before (Panama Canal, the 1955–69 eradication campaign)
  - The risks of gene drives

  Wolbachia and sterile-male releases were added to "Could we do it?", plus a short outro.
- **All 98 scenes** are now illustrated and animated. The finished episode runs **12:06**.
- **Sound effects** are about 11 dB quieter relative to the voice, and duck a further ~5 dB under narration. The music bed also ducks under the voice.
- **Loudness** now uses two-pass normalisation.

## Summary
| Item | Value |
|---|---|
| Script | 1,687 words, 98 scenes, 15 sections |
| Narration | 98 / 98 scenes, Kokoro TTS (voice `am_michael`) |
| Scene images | 98, all QC-checked (scenes 4, 16 and 73 fixed after review) |
| Reference images | 8 (2 character sheets, 5 backgrounds, 1 object) |
| Animated clips | 98, **17,440 frames**, all verified 1920×1080 at 24 fps with duration = narration + 0.7 s |
| **Final video duration** | **12:06.67 (726.67 s)** |
| Resolution / frame rate | 1920×1080 (16:9), 24 fps |
| Video | H.264, yuv420p, about 3.6 Mb/s |
| Audio | AAC 192 kb/s, 48 kHz stereo. Measured −15.0 LUFS integrated, −4.2 dBFS peak. |
| SFX level | Peaks 18.5 dB below the voice (v1: 7.2 dB below) |
| File size | 323 MB |

## Exact final file locations
All paths are relative to `YOUTUBE_PRODUCTION/01_PROJECTS/what_if_mosquitoes_disappeared/`.

- **Final video:** `07_FINAL_VIDEO/what_if_all_mosquitoes_disappeared_full.mp4`
- **Exports (upload these):** in `10_EXPORTS/`
  - `what_if_all_mosquitoes_disappeared_full.mp4`
  - `what_if_all_mosquitoes_disappeared_full.srt`
  - `YOUTUBE_UPLOAD.md` (titles, description with chapters, tags)
- **Thumbnail:** `09_THUMBNAIL/thumbnail_1280x720.jpg`
- **Editing project:** in `08_EDITING_PROJECT/`
  - `CAPCUT_EDIT_GUIDE.md`
  - `SCENE_TIMELINE.md`
  - voice, SFX and music stems (WAV)
  - SRT
  - timeline JSON
  - concat list
- **Clips:** `05_ANIMATIONS/scene_001/scene_001.mp4` … `scene_098/scene_098.mp4`
- **Images:** `04_IMAGES/scenes/scene_001.png` … `scene_098.png`, plus `characters/`, `backgrounds/` and `objects/`
- **Narration:** `06_AUDIO/narration/scene_001.wav` … `scene_098.wav`

## Storage note
Videos and WAVs are stored with **Git LFS**, because GitHub rejects any single file over 100 MB on every plan. Two large files are regenerable and kept out of git:

- `08_EDITING_PROJECT/*_video_only.mp4`
- `08_EDITING_PROJECT/*_audio_mix.wav`

To regenerate them, run `python3 tools/assemble.py 01_PROJECTS/what_if_mosquitoes_disappeared 1 98 what_if_all_mosquitoes_disappeared_full`.

## Missing assets and remaining tasks
- **CapCut:** no native project was created, because CapCut isn't available in this cloud environment. Import steps are in `08_EDITING_PROJECT/CAPCUT_EDIT_GUIDE.md`.
- **Voice:** TTS narration. Listen and decide whether to keep it or re-voice.
- **Loudness:** −15 LUFS, 1 LU under YouTube's −14 reference. Fine as is; raise by 1 dB in CapCut if you like.
- **Fact check:** some second-half details rely on secondary summaries (marked *(secondary)* in the research file). Spot-check before publishing.
- **Competitor motion analysis:** still inferred, because YouTube blocked playback in this environment.
