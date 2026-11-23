# CapCut / Editor Import Guide (scenes 001–010)

CapCut was **not available** in the cloud environment where this was produced, so **no native CapCut project was created.** Everything below can be imported into CapCut (desktop) or any NLE (Premiere, DaVinci Resolve, Final Cut) in a few minutes.

## What's here
| File | Use |
|---|---|
| `../05_ANIMATIONS/scene_###/scene_###.mp4` | 10 separate scene clips, for re-timing in CapCut |
| `what_if_mosquitoes_disappeared_scenes_001-010_video_only.mp4` | All clips joined, no audio |
| `…_voice_only.wav` | Narration on the exact timeline (48 kHz) |
| `…_sfx_only.wav` | Sound effects on the exact timeline |
| `../06_AUDIO/music/music_bed_curious_72bpm.wav` | Original music bed (used at about −16 dB under the voice) |
| `…_audio_mix.wav` | Finished mix (voice + SFX + music) |
| `….srt` | Captions, timed to the narration |
| `…_timeline.json` | Start time, duration, narration and file of every scene |
| `…_concat.txt` | FFmpeg concat list (for rebuilding with FFmpeg) |

## Fastest CapCut workflow
1. **New project**, 1920×1080, 24 fps.
2. Import `…_video_only.mp4` → track 1.
3. Import `…_voice_only.wav` → audio track 1 at 0:00.
4. Import `…_sfx_only.wav` → audio track 2 at 0:00.
5. Import the music bed → audio track 3 at 0:00. Set its volume to about −16 dB and fade out over the last 1.5 s.
6. Captions: **Text → Import captions** (or Captions → Import) → choose the `.srt`.

Everything lines up because all files start at 0:00.

## Fine-editing workflow (per scene)
Import the 10 clips from `05_ANIMATIONS` in order. Place each narration file `06_AUDIO/narration/scene_###.wav` at **clip start + 0.12 s**:

| Scene | Clip start | Duration |
|---|---|---|
| 001 | 0:00.000 | 4.833 |
| 002 | 0:04.833 | 7.375 |
| 003 | 0:12.208 | 3.250 |
| 004 | 0:15.458 | 2.125 |
| 005 | 0:17.583 | 2.000 |
| 006 | 0:19.583 | 2.042 |
| 007 | 0:21.625 | 8.250 |
| 008 | 0:29.875 | 2.167 |
| 009 | 0:32.042 | 2.000 |
| 010 | 0:34.042 | 5.125 |

## Suggested polish in CapCut
- If you prefer a human voice or a different TTS voice, replace the narration. Re-time clips to the new voice; each clip should be about voice length + 0.5 s.
- Add a 0.25 s cross-dissolve between 004→005 and 009→010 (location changes). Keep hard cuts elsewhere.
- Add a subtle "whoosh" before the title in scene 010 if you want more punch.
