# Edit Package: What If Every Vulture Disappeared? (Episode 3)

The finished review video is `12_Exports/what_if_every_vulture_disappeared_REVIEW.mp4` (10:00, 1080p24). Use this package only if you want to re-edit it in CapCut, Premiere or Resolve.

CapCut cannot be automated from this cloud container, so this is an import-ready package, **not a native CapCut project**.

## What's here

| File | Use |
|---|---|
| `what_if_every_vulture_disappeared_timeline.json` | Every scene: start time, duration, narration text, visual spec, relative clip and audio paths |
| `what_if_every_vulture_disappeared.srt` | Subtitles, one cue per scene, offset 0.12 s |
| `*_voice_only.m4a` | Narration stem (normalised) |
| `*_music_only.m4a` | Score stem, already ducked under the voice |
| `*_sfx_only.m4a` | Sound-effects stem, already ducked |
| `*_audio_mix.m4a` | Full mix, before the final loudness pass |
| `*_concat.txt` | Clip order for FFmpeg concat |

## Rebuilding the scene clips

The 74 per-scene clips (`09_Animation/SC###.mp4`, about 1.9 GB) are not stored in git. Rebuild them in about 25 minutes:

```bash
cd YOUTUBE_PRODUCTION
# renders: blender -b --factory-startup -P tools/vulture3d/shots.py -- 01_PROJECTS/what_if_vultures_disappeared/08_Scenes/renders all --frames=A01:68 --frames=A02:108 --frames=A03:94
python3 tools/vulture3d/compose.py 01_PROJECTS/what_if_vultures_disappeared
python3 tools/vulture3d/audio.py 01_PROJECTS/what_if_vultures_disappeared assets
python3 tools/vulture3d/audio.py 01_PROJECTS/what_if_vultures_disappeared music
python3 tools/vulture3d/audio.py 01_PROJECTS/what_if_vultures_disappeared assemble what_if_every_vulture_disappeared
```

The committed `08_Scenes/renders/*.jpg` and `A0*.mp4` are compact copies of the renders, for review.

## Manual edit steps (CapCut or similar)

1. Import the clips in `_concat.txt` order onto track V1. They butt-join with hard cuts.
2. Put `voice_only.m4a` on A1 at 0:00.
3. Put `music_only.m4a` on A2 and `sfx_only.m4a` on A3. They are already level-matched.
4. Import the SRT as captions if you want burned-in subtitles.
5. Export at 1080p24, H.264, AAC 48 kHz, with loudness at about −14 LUFS.
