# Final Production Report: Episode 2, "What If All Bees Disappeared?"

## Summary
| Item | Value |
|---|---|
| Topic choice | Bees: the most popular candidate from the topic list, with strong myth-busting angles |
| Research | `01_RESEARCH/TOPIC_SCIENTIFIC_RESEARCH.md`: 9 sections with tagged claims and sources |
| Script | 1,636 words, 105 scenes, 18 sections |
| Narration | 105 / 105 scenes, Kokoro TTS (`am_michael`), 632.9 s of speech |
| Scene images | 105, all QC-checked (fixes listed in `04_IMAGES/IMAGE_GENERATION_REPORT.md`) |
| Animated clips | 105, **17,337 frames**, all verified 1920×1080 at 24 fps with duration = narration + 0.85 s |
| Animated on-screen text | 60 scenes with automatic kinetic text: counters, pop-in words, typewriter, stamps, sliding labels, checklists, highlighter |
| **Final duration** | **12:02.4 (722.38 s)** |
| Video | H.264, yuv420p, about 6.1 Mb/s (more detail than episode 1, so a higher bitrate) |
| Audio | AAC 192 kb/s, 48 kHz stereo, −15.1 LUFS integrated, −3.9 dBFS peak |
| Music | New original bed for this episode (`music_bed_sunny_84bpm.wav`), ducked under the voice |
| SFX | Bee buzz, pops, ticks, stamp thuds, typewriter keys, cued automatically from the text animations. Peaks about 18 dB below the voice (same level as the episode 1 fix). |
| File size | 551 MB |

## What changed from episode 1 (per your request)
1. **More designed backgrounds.** Every environment is layered (sky, sun rays, clouds, tree lines, hills, detailed foregrounds). There are about 20 new detailed sets: cottage garden, supermarket in perspective, kitchen, apiary, honeycomb interior, orchards, terraces, greenhouse, city rooftops, farmyard and more.
2. **More detailed objects.** New characters: bees with pollen baskets, a queen and a courier, a bumblebee, solitary bees, a beekeeper with a veil. There are about 40 food items and props.
3. **Animated text.** A new kinetic-text engine (`tools/kinetic.py`) animates each scene's text cue from the storyboard, and sound effects are synced to it.

## File locations
All paths are relative to `YOUTUBE_PRODUCTION/01_PROJECTS/what_if_all_bees_disappeared/`.

- **Final:** `07_FINAL_VIDEO/what_if_all_bees_disappeared_full.mp4`
- **Exports:** in `10_EXPORTS/`
  - the `.mp4`
  - the `.srt`
  - `YOUTUBE_UPLOAD.md` (search research, titles)
  - `description.txt` (with chapters)
  - `tags.txt`
- **Thumbnail:** `09_THUMBNAIL/thumb_bees_detailed_1280x720.jpg`, plus the master and a mobile preview
- **Editing:** `08_EDITING_PROJECT/`
  - `CAPCUT_EDIT_GUIDE.md`
  - `SCENE_TIMELINE.md`
  - voice, SFX and music stems
  - SRT, timeline JSON, concat list
- **Clips:** `05_ANIMATIONS/scene_###/scene_###.mp4`
- **Images:** `04_IMAGES/scenes/`
- **Audio:** `06_AUDIO/`

## Remaining notes
- No native CapCut project, because CapCut isn't available here. Import steps are in the guide.
- The voice is TTS. Review it, or re-voice it.
- Loudness is −15.1 LUFS, about 1 LU under YouTube's reference. That's fine.
- The Lancet figures are **model estimates for all animal pollinators**, and the script says so on screen and in narration.
