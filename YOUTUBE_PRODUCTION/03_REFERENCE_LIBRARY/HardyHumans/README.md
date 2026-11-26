# Reference Library: Hardy Humans

- **Channel:** https://www.youtube.com/@HardyHumans
- **Reference video:** https://youtu.be/wqMaepNXeBc ("What If You Were the Last Human on Earth for 3 Years? (Full Story)", 37:12)
- **Researched:** 2026-11-26

## Contents

| File | What it is | In git? |
|---|---|---|
| `01_Competitor_Research/competitor_report.md` | Channel positioning, performance, titles, thumbnails, storytelling, opportunities, recommendations | ✔ |
| `01_Competitor_Research/channel_videos.csv` | 23 videos: views, likes, comments, length, both title variants (snapshot) | ✔ |
| `01_Competitor_Research/thumbnails/`, `thumbnails_contact_sheet.jpg` | Competitor thumbnails | ✘ gitignored |
| `02_Reference_Analysis/report.md` | Deep analysis of the reference video: **start here** | ✔ |
| `02_Reference_Analysis/scene_timeline.csv` | 225 sampled frames with frame type, shot, environment, caption and measured stats | ✔ |
| `02_Reference_Analysis/keyframe_metrics.csv`, `video_info.json` | Measured stats; metadata and chapters | ✔ |
| `02_Reference_Analysis/visual_style_bible.md` | Their look, as production guidance, plus the do-not-copy list | ✔ |
| `02_Reference_Analysis/camera_and_lighting_notes.md` | Shot vocabulary, composition, lighting moods, Blender equivalents | ✔ |
| `02_Reference_Analysis/motion_notes.md` | Motion: **not observed** (video not downloadable); inferences and open questions | ✔ |
| `02_Reference_Analysis/keyframes/`, `contact_sheets/` | 225 frames and 8 sheets | ✘ gitignored |

## Why some files are not in git

The repository is **public**, so the competitor's frames and thumbnails (their copyrighted images) are kept local only. Rebuild them in about 1 minute:

```bash
cd YOUTUBE_PRODUCTION
pip3 install -q "yt-dlp[default]"            # needs Node on PATH
python3 tools/fetch_reference_frames.py "https://www.youtube.com/watch?v=wqMaepNXeBc" \
    "https://www.youtube.com/@HardyHumans" 03_REFERENCE_LIBRARY/HardyHumans
python3 tools/reference_labels_HH_wqMaepNXeBc.py 03_REFERENCE_LIBRARY/HardyHumans/02_Reference_Analysis
```

The session needs the "video" cloud environment, or any network policy that allows the YouTube hosts.
