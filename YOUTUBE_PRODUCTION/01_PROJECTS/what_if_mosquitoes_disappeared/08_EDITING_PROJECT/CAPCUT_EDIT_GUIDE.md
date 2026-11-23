# CapCut / Editor Import Guide: full episode (98 scenes, 12:06)

CapCut was **not available** in the cloud environment where this was produced, so **no native CapCut project was created.** Everything below imports into CapCut desktop (or Premiere, Resolve or Final Cut) and lines up at 0:00.

## Files
| File | Use |
|---|---|
| `../07_FINAL_VIDEO/what_if_all_mosquitoes_disappeared_full.mp4` | Finished video, picture and mixed sound |
| `../05_ANIMATIONS/scene_###/scene_###.mp4` | 98 separate scene clips, for re-editing |
| `what_if_all_mosquitoes_disappeared_full_voice_only.wav` | Narration stem on the exact timeline |
| `what_if_all_mosquitoes_disappeared_full_sfx_only.wav` | Sound-effects stem (already at the new, lower level and ducked) |
| `what_if_all_mosquitoes_disappeared_full_music_only.wav` | Music stem (already ducked under the voice) |
| `what_if_all_mosquitoes_disappeared_full.srt` | Captions |
| `what_if_all_mosquitoes_disappeared_full_timeline.json` / `SCENE_TIMELINE.md` | Start time and duration of every scene |
| `what_if_all_mosquitoes_disappeared_full_concat.txt` | FFmpeg concat list |

Two regenerable files are not stored in git, to save space:

- `*_video_only.mp4` (silent picture)
- `*_audio_mix.wav`

Recreate both with `python3 tools/assemble.py 01_PROJECTS/what_if_mosquitoes_disappeared 1 98 what_if_all_mosquitoes_disappeared_full`. Or use the final MP4 and mute its audio in CapCut.

## Fastest CapCut setup (adjustable sound levels)
1. Create a new project at 1920×1080, 24 fps.
2. Import the final MP4 onto track 1 and **mute its audio**.
3. Add the stems at 0:00, each on its own audio track:
   - voice → audio track 1
   - SFX → audio track 2
   - music → audio track 3
4. Set the levels to taste. Each stem's volume slider now controls that layer independently. For example, lower the SFX track further if you want effects even quieter.
5. Import captions: Text → Import captions → choose the `.srt`.

## Re-cutting scenes
Use `SCENE_TIMELINE.md`. Each narration file `../06_AUDIO/narration/scene_###.wav` starts at clip start + 0.12 s.
